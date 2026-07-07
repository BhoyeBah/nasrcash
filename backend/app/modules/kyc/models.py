import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class KycStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_MORE_INFO = "requires_more_info"
    EXPIRED = "expired"


# Statuses a user can still act on (add documents / resubmit).
ACTIONABLE_STATUSES = {KycStatus.DRAFT.value, KycStatus.REQUIRES_MORE_INFO.value}
# Statuses meaning "a review is already in flight for this profile".
IN_FLIGHT_STATUSES = {KycStatus.SUBMITTED.value, KycStatus.UNDER_REVIEW.value}


class DocumentType(StrEnum):
    NATIONAL_ID = "national_id"
    PASSPORT = "passport"
    SELFIE = "selfie"
    PROOF_OF_ADDRESS = "proof_of_address"
    BUSINESS_DOCUMENT = "business_document"


IDENTITY_DOCUMENT_TYPES = {DocumentType.NATIONAL_ID.value, DocumentType.PASSPORT.value}

# Document types required to reach a given KYC level.
REQUIRED_DOCUMENTS_FOR_LEVEL: dict[int, set[str]] = {
    1: {DocumentType.SELFIE.value},  # plus one of IDENTITY_DOCUMENT_TYPES, checked separately
    2: {DocumentType.SELFIE.value, DocumentType.PROOF_OF_ADDRESS.value},
}

MAX_KYC_LEVEL = 2


class KycProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kyc_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    level_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default=KycStatus.DRAFT.value, nullable=False
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class KycDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "kyc_documents"

    kyc_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kyc_profiles.id"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
