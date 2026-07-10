import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class NotificationType(StrEnum):
    ACCOUNT_CREATED = "account_created"
    KYC_SUBMITTED = "kyc_submitted"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    TOPUP_RECEIVED = "topup_received"
    WITHDRAWAL_SUCCESSFUL = "withdrawal_successful"
    WITHDRAWAL_FAILED = "withdrawal_failed"
    CARD_CREATED = "card_created"
    CARD_FUNDED = "card_funded"
    PAYMENT_ACCEPTED = "payment_accepted"
    PAYMENT_DECLINED = "payment_declined"
    CARD_FROZEN = "card_frozen"
    SECURITY_ALERT = "security_alert"
    SUPPORT_REPLY = "support_reply"


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
