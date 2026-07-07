import uuid
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WalletStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    CLOSED = "closed"


class Wallet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One local-currency wallet per user. Balance columns below are a cache
    refreshed from the ledger on read — the ledger remains the source of
    truth (see app.modules.ledger.service.LedgerService)."""

    __tablename__ = "wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True
    )
    country_code: Mapped[str] = mapped_column(
        String(2), ForeignKey("countries.code"), nullable=False
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=WalletStatus.ACTIVE.value, nullable=False)
    cached_available_balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal(0), nullable=False
    )
    cached_pending_balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal(0), nullable=False
    )
    cached_blocked_balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2), default=Decimal(0), nullable=False
    )
