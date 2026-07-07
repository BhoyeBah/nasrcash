import uuid
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CardStatus(StrEnum):
    REQUESTED = "requested"
    ISSUING = "issuing"
    ACTIVE = "active"
    FROZEN = "frozen"
    BLOCKED = "blocked"
    CLOSED = "closed"
    EXPIRED = "expired"
    FAILED = "failed"


class Card(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A virtual card. Only masked PAN/last4 are ever stored — the
    CardProvider interface never hands NasrCash a full PAN or CVV to begin
    with (see app.modules.providers.card_provider)."""

    __tablename__ = "cards"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_card_id: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    masked_pan: Mapped[str] = mapped_column(String(30), nullable=False)
    last4: Mapped[str] = mapped_column(String(4), nullable=False)
    brand: Mapped[str] = mapped_column(String(20), nullable=False)
    displayed_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=CardStatus.ACTIVE.value, nullable=False
    )
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expiry_month: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_year: Mapped[int] = mapped_column(Integer, nullable=False)
    cached_available_balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal(0), nullable=False
    )
