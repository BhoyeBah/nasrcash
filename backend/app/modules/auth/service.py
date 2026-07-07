import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError, ValidationError
from app.core.security import (
    IssuedToken,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_secret,
    verify_secret,
)
from app.modules.audit.service import AuditService
from app.modules.auth.models import OtpCode, OtpPurpose, RefreshToken, User, UserStatus
from app.modules.countries.models import Country
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import NotificationService
from app.modules.wallets.service import WalletService

settings = get_settings()
logger = logging.getLogger("nasrcash.auth")


def _generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)

    async def _get_user_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def _issue_otp(self, user: User, purpose: OtpPurpose) -> str:
        code = _generate_otp_code()
        otp = OtpCode(
            user_id=user.id,
            purpose=purpose.value,
            code_hash=hash_secret(code),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.otp_expire_seconds),
        )
        self.db.add(otp)
        await self.db.flush()
        # Sandbox-only: the OTP is never actually sent by SMS yet, only logged.
        logger.info("[SANDBOX OTP] phone=%s purpose=%s code=%s", user.phone, purpose.value, code)
        return code

    async def _consume_otp(self, user: User, purpose: OtpPurpose, code: str) -> None:
        result = await self.db.execute(
            select(OtpCode)
            .where(
                OtpCode.user_id == user.id,
                OtpCode.purpose == purpose.value,
                OtpCode.consumed_at.is_(None),
            )
            .order_by(OtpCode.created_at.desc())
            .limit(1)
        )
        otp = result.scalar_one_or_none()
        if otp is None:
            raise ValidationError("Aucun code OTP en attente pour ce numéro")
        if otp.expires_at < datetime.now(timezone.utc):
            raise ValidationError("Le code OTP a expiré")
        if otp.attempts >= otp.max_attempts:
            raise ValidationError("Nombre maximal de tentatives OTP atteint")

        otp.attempts += 1
        if not verify_secret(code, otp.code_hash):
            await self.db.flush()
            raise ValidationError("Code OTP invalide")

        otp.consumed_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def _issue_token_pair(
        self, user: User, device_id: str | None, device_name: str | None
    ) -> tuple[IssuedToken, IssuedToken]:
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        self.db.add(
            RefreshToken(
                user_id=user.id,
                jti=refresh.jti,
                device_id=device_id,
                device_name=device_name,
                expires_at=refresh.expires_at,
            )
        )
        await self.db.flush()
        return access, refresh

    async def register(
        self, phone: str, country_code: str, pin: str
    ) -> tuple[User, str]:
        existing = await self._get_user_by_phone(phone)
        if existing is not None:
            raise ConflictError("Un compte existe déjà pour ce numéro")

        country = await self.db.get(Country, country_code)
        if country is None or not country.is_active:
            raise ValidationError(f"Pays non supporté : {country_code}")

        user = User(
            phone=phone,
            country_code=country_code,
            pin_hash=hash_secret(pin),
            status=UserStatus.PENDING_KYC.value,
        )
        self.db.add(user)
        await self.db.flush()

        await WalletService(self.db).create_wallet_for_user(
            user.id, country_code, country.currency_code
        )
        await self.notifications.create(
            user.id, NotificationType.ACCOUNT_CREATED.value,
            "Bienvenue sur NasrCash", "Votre compte a été créé avec succès.",
        )

        otp_code = await self._issue_otp(user, OtpPurpose.REGISTRATION)
        await self.audit.log(
            actor_type="user", actor_id=user.id, action="auth.register", target_type="user",
            target_id=str(user.id),
        )
        return user, otp_code

    async def verify_otp(
        self, phone: str, code: str, device_id: str | None, device_name: str | None
    ) -> tuple[IssuedToken, IssuedToken]:
        user = await self._get_user_by_phone(phone)
        if user is None:
            raise ValidationError("Numéro de téléphone inconnu")

        await self._consume_otp(user, OtpPurpose.REGISTRATION, code)
        user.phone_verified_at = datetime.now(timezone.utc)
        await self.db.flush()

        await self.audit.log(
            actor_type="user", actor_id=user.id, action="auth.otp.verified", target_type="user",
            target_id=str(user.id),
        )
        return await self._issue_token_pair(user, device_id, device_name)

    async def login(
        self, phone: str, pin: str, device_id: str | None, device_name: str | None
    ) -> tuple[IssuedToken, IssuedToken]:
        user = await self._get_user_by_phone(phone)
        if user is None:
            raise UnauthorizedError("Numéro ou PIN invalide")

        if user.status in (UserStatus.SUSPENDED.value, UserStatus.CLOSED.value):
            raise ForbiddenError("Ce compte est suspendu ou fermé")

        now = datetime.now(timezone.utc)
        if user.locked_until is not None and user.locked_until > now:
            raise ForbiddenError("Compte temporairement verrouillé, réessayez plus tard")

        if not verify_secret(pin, user.pin_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.max_login_attempts:
                user.locked_until = now + timedelta(minutes=settings.login_lockout_minutes)
            await self.db.flush()
            await self.audit.log(
                actor_type="user", actor_id=user.id, action="auth.login.failed",
                target_type="user", target_id=str(user.id),
            )
            raise UnauthorizedError("Numéro ou PIN invalide")

        user.failed_login_attempts = 0
        user.locked_until = None
        await self.db.flush()

        await self.audit.log(
            actor_type="user", actor_id=user.id, action="auth.login.success", target_type="user",
            target_id=str(user.id),
        )
        return await self._issue_token_pair(user, device_id, device_name)

    async def refresh(self, refresh_token: str) -> tuple[IssuedToken, IssuedToken]:
        payload = decode_token(refresh_token, TokenType.REFRESH)
        jti = payload["jti"]

        result = await self.db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        session = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at.replace(tzinfo=timezone.utc) < now
        ):
            raise UnauthorizedError("Session invalide ou expirée")

        user = await self.db.get(User, session.user_id)
        if user is None or user.status in (UserStatus.SUSPENDED.value, UserStatus.CLOSED.value):
            raise UnauthorizedError("Session invalide")

        session.revoked_at = now
        await self.db.flush()

        return await self._issue_token_pair(user, session.device_id, session.device_name)

    async def logout(self, refresh_token: str, all_devices: bool) -> None:
        payload = decode_token(refresh_token, TokenType.REFRESH)
        jti = payload["jti"]
        user_id = uuid.UUID(payload["sub"])
        now = datetime.now(timezone.utc)

        if all_devices:
            result = await self.db.execute(
                select(RefreshToken).where(
                    RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
                )
            )
            for session in result.scalars():
                session.revoked_at = now
        else:
            result = await self.db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
            session = result.scalar_one_or_none()
            if session is not None:
                session.revoked_at = now

        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=user_id,
            action="auth.logout.all" if all_devices else "auth.logout",
        )

    async def change_pin(self, user: User, current_pin: str, new_pin: str) -> None:
        if not verify_secret(current_pin, user.pin_hash):
            raise UnauthorizedError("PIN actuel invalide")

        user.pin_hash = hash_secret(new_pin)
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None)
            )
        )
        for session in result.scalars():
            session.revoked_at = now
        await self.db.flush()

        await self.audit.log(
            actor_type="user", actor_id=user.id, action="auth.pin.changed", target_type="user",
            target_id=str(user.id),
        )

    async def forgot_pin(self, phone: str) -> str | None:
        user = await self._get_user_by_phone(phone)
        if user is None:
            # Do not reveal whether the phone number is registered.
            return None
        return await self._issue_otp(user, OtpPurpose.PIN_RESET)

    async def reset_pin(self, phone: str, code: str, new_pin: str) -> None:
        user = await self._get_user_by_phone(phone)
        if user is None:
            raise ValidationError("Numéro de téléphone inconnu")

        await self._consume_otp(user, OtpPurpose.PIN_RESET, code)
        user.pin_hash = hash_secret(new_pin)
        user.failed_login_attempts = 0
        user.locked_until = None

        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None)
            )
        )
        for session in result.scalars():
            session.revoked_at = now
        await self.db.flush()

        await self.audit.log(
            actor_type="user", actor_id=user.id, action="auth.pin.reset", target_type="user",
            target_id=str(user.id),
        )
