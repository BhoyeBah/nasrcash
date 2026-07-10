import uuid
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentStatus(StrEnum):
    SETTLED = "settled"
    DECLINED = "declined"
    REFUNDED = "refunded"


class DeclineReason(StrEnum):
    INSUFFICIENT_BALANCE = "insufficient_balance"
    CARD_FROZEN = "card_frozen"
    CARD_BLOCKED = "card_blocked"
    UNSUPPORTED_CURRENCY = "unsupported_currency"
    LIMIT_EXCEEDED = "limit_exceeded"
    ACCOUNT_FROZEN = "account_frozen"


class CardPayment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An international card payment attempt — settled or declined. Mirrors
    the ``card_transactions`` table from the product spec. The FX rate is
    frozen at the moment of the attempt and never recalculated afterwards."""

    __tablename__ = "card_transactions"

    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False, index=True
    )
    merchant_name: Mapped[str] = mapped_column(String(150), nullable=False)
    merchant_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    merchant_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    merchant_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    local_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    local_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    fees_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    total_debited: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    decline_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider_reference: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
