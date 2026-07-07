from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.storage import save_kyc_document
from app.modules.audit.service import AuditService
from app.modules.auth.models import User, UserStatus
from app.modules.kyc.models import (
    ACTIONABLE_STATUSES,
    IDENTITY_DOCUMENT_TYPES,
    IN_FLIGHT_STATUSES,
    MAX_KYC_LEVEL,
    REQUIRED_DOCUMENTS_FOR_LEVEL,
    DocumentType,
    KycDocument,
    KycProfile,
    KycStatus,
)
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import NotificationService


class KycService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)

    async def _latest_profile(self, user_id) -> KycProfile | None:
        result = await self.db.execute(
            select(KycProfile)
            .where(KycProfile.user_id == user_id)
            .order_by(KycProfile.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _documents_for(self, profile_id) -> list[KycDocument]:
        result = await self.db.execute(
            select(KycDocument).where(KycDocument.kyc_profile_id == profile_id)
        )
        return list(result.scalars())

    async def start(self, user: User) -> KycProfile:
        if user.kyc_level >= MAX_KYC_LEVEL:
            raise ValidationError("Le niveau KYC maximum est déjà atteint")

        existing = await self._latest_profile(user.id)
        if existing is not None:
            if existing.status in IN_FLIGHT_STATUSES:
                raise ConflictError("Une vérification KYC est déjà en cours de traitement")
            if existing.status in ACTIONABLE_STATUSES:
                return existing

        profile = KycProfile(user_id=user.id, level_requested=user.kyc_level + 1)
        self.db.add(profile)
        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=user.id, action="kyc.started", target_type="kyc_profile",
            target_id=str(profile.id),
        )
        return profile

    async def _get_actionable_profile(self, user: User) -> KycProfile:
        profile = await self._latest_profile(user.id)
        if profile is None or profile.status not in ACTIONABLE_STATUSES:
            raise ValidationError("Aucune session KYC active — appelez /kyc/start d'abord")
        return profile

    async def add_document(
        self, user: User, document_type: str, file: UploadFile
    ) -> KycDocument:
        if document_type not in {d.value for d in DocumentType}:
            raise ValidationError(f"Type de document invalide : {document_type}")

        profile = await self._get_actionable_profile(user)
        content = await file.read()
        if not content:
            raise ValidationError("Le fichier est vide")

        file_path = save_kyc_document(user.id, file.filename or "document", content)
        document = KycDocument(
            kyc_profile_id=profile.id,
            document_type=document_type,
            file_path=file_path,
            original_filename=file.filename or "document",
        )
        self.db.add(document)
        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=user.id, action="kyc.document.uploaded",
            target_type="kyc_profile", target_id=str(profile.id),
            context={"document_type": document_type},
        )
        return document

    async def submit(self, user: User) -> KycProfile:
        profile = await self._get_actionable_profile(user)
        documents = await self._documents_for(profile.id)
        submitted_types = {d.document_type for d in documents}

        required = REQUIRED_DOCUMENTS_FOR_LEVEL.get(profile.level_requested, set())
        missing = required - submitted_types
        if missing:
            raise ValidationError(f"Documents manquants : {', '.join(sorted(missing))}")
        if not (submitted_types & IDENTITY_DOCUMENT_TYPES):
            raise ValidationError(
                "Un document d'identité est requis (carte nationale ou passeport)"
            )

        now = datetime.now(timezone.utc)
        profile.status = KycStatus.SUBMITTED.value
        profile.submitted_at = now
        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=user.id, action="kyc.submitted",
            target_type="kyc_profile", target_id=str(profile.id),
        )
        await self.notifications.create(
            user.id, NotificationType.KYC_SUBMITTED.value,
            "Vérification KYC soumise", "Votre dossier est en cours de traitement.",
        )

        # Sandbox-only: no human reviewer or partner API exists yet, so the
        # submission is auto-reviewed and approved synchronously.
        await self._sandbox_auto_approve(user, profile)
        return profile

    async def _sandbox_auto_approve(self, user: User, profile: KycProfile) -> None:
        now = datetime.now(timezone.utc)
        profile.status = KycStatus.APPROVED.value
        profile.reviewed_at = now
        profile.reviewed_by = "sandbox_auto_reviewer"
        user.kyc_level = profile.level_requested
        if user.status == UserStatus.PENDING_KYC.value:
            user.status = UserStatus.ACTIVE.value
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="kyc.auto_approved", target_type="kyc_profile",
            target_id=str(profile.id), context={"level": profile.level_requested},
        )
        await self.notifications.create(
            user.id, NotificationType.KYC_APPROVED.value,
            "KYC approuvé", f"Votre niveau KYC {profile.level_requested} a été approuvé.",
        )

    async def get_status(self, user: User) -> tuple[KycProfile | None, list[KycDocument]]:
        profile = await self._latest_profile(user.id)
        documents = await self._documents_for(profile.id) if profile else []
        return profile, documents

    async def approve(self, profile_id, reviewer_id: str) -> KycProfile:
        profile = await self.db.get(KycProfile, profile_id)
        if profile is None:
            raise NotFoundError("Profil KYC introuvable")
        if profile.status not in IN_FLIGHT_STATUSES:
            raise ForbiddenError("Ce profil KYC n'est pas en attente de revue")

        user = await self.db.get(User, profile.user_id)
        now = datetime.now(timezone.utc)
        profile.status = KycStatus.APPROVED.value
        profile.reviewed_at = now
        profile.reviewed_by = reviewer_id
        user.kyc_level = profile.level_requested
        if user.status == UserStatus.PENDING_KYC.value:
            user.status = UserStatus.ACTIVE.value
        await self.db.flush()
        await self.audit.log(
            actor_type="admin", action="kyc.approved", target_type="kyc_profile",
            target_id=str(profile.id), context={"reviewer_id": reviewer_id},
        )
        await self.notifications.create(
            user.id, NotificationType.KYC_APPROVED.value,
            "KYC approuvé", f"Votre niveau KYC {profile.level_requested} a été approuvé.",
        )
        return profile

    async def reject(self, profile_id, reviewer_id: str, reason: str) -> KycProfile:
        profile = await self.db.get(KycProfile, profile_id)
        if profile is None:
            raise NotFoundError("Profil KYC introuvable")
        if profile.status not in IN_FLIGHT_STATUSES:
            raise ForbiddenError("Ce profil KYC n'est pas en attente de revue")

        profile.status = KycStatus.REJECTED.value
        profile.rejection_reason = reason
        profile.reviewed_at = datetime.now(timezone.utc)
        profile.reviewed_by = reviewer_id
        await self.db.flush()
        await self.audit.log(
            actor_type="admin", action="kyc.rejected", target_type="kyc_profile",
            target_id=str(profile.id), context={"reviewer_id": reviewer_id, "reason": reason},
        )
        await self.notifications.create(
            profile.user_id, NotificationType.KYC_REJECTED.value,
            "KYC rejeté", f"Votre dossier KYC a été rejeté : {reason}",
        )
        return profile

    async def request_more_info(self, profile_id, reviewer_id: str, reason: str) -> KycProfile:
        profile = await self.db.get(KycProfile, profile_id)
        if profile is None:
            raise NotFoundError("Profil KYC introuvable")
        if profile.status not in IN_FLIGHT_STATUSES:
            raise ForbiddenError("Ce profil KYC n'est pas en attente de revue")

        profile.status = KycStatus.REQUIRES_MORE_INFO.value
        profile.rejection_reason = reason
        profile.reviewed_at = datetime.now(timezone.utc)
        profile.reviewed_by = reviewer_id
        await self.db.flush()
        await self.audit.log(
            actor_type="admin", action="kyc.requires_more_info", target_type="kyc_profile",
            target_id=str(profile.id), context={"reviewer_id": reviewer_id, "reason": reason},
        )
        return profile
