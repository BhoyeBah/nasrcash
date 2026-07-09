import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WithdrawalStatus(StrEnum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"


class Withdrawal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A wallet-to-Mobile-Money payout — the mirror image of a Topup.

    ``amount`` is debited from the wallet in full; ``net_amount`` (amount
    minus fee) is what actually reaches the user's Mobile Money account.
    """

    __tablename__ = "withdrawals"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)  # gross, debited
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)  # paid out
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_reference: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=WithdrawalStatus.PENDING.value, nullable=False
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
