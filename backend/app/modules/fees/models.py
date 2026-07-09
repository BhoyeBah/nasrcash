from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FeeType(StrEnum):
    TOPUP = "topup"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"


class FeeRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A configurable frais rule (cahier des charges §14.8).

    ``country_code``, ``provider_name`` and ``kyc_level`` are all nullable —
    null means "applies to everyone unless a more specific rule exists".
    Nothing about pricing is hardcoded in business logic; it is all data
    here, just like ``LimitRule``.
    """

    __tablename__ = "fee_rules"

    country_code: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("countries.code"), nullable=True
    )
    provider_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    kyc_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fee_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)  # fraction, e.g. 0.02
    fixed_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=Decimal(0), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
