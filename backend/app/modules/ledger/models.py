import uuid
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EntryDirection(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class LedgerTransaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One balanced business event (a topup, a card funding, a payment...).

    ``reference`` is the idempotency key: replaying the same business
    operation must resolve to the same row, never create a second one.
    """

    __tablename__ = "ledger_transactions"

    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class LedgerEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single debit or credit line. Entries are append-only: never
    updated or deleted once written — corrections are new transactions."""

    __tablename__ = "ledger_entries"

    ledger_transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ledger_transactions.id"), nullable=False, index=True
    )
    # Conventional string account id: "wallet:<uuid>", "card:<uuid>",
    # "provider:orange_money", "revenue:nasrcash", "settlement:<provider>", ...
    account_id: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
