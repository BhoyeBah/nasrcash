from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LimitType(StrEnum):
    TOPUP_MIN = "topup_min"
    TOPUP_MAX = "topup_max"
    WALLET_DAILY_TOPUP_CAP = "wallet_daily_topup_cap"
    WITHDRAWAL_DAILY_CAP = "withdrawal_daily_cap"
    CARD_PAYMENT_DAILY_CAP = "card_payment_daily_cap"
    MAX_CARDS_PER_USER = "max_cards_per_user"


# Limit types expressed as a monetary bound vs. a plain count.
AMOUNT_LIMIT_TYPES = {
    LimitType.TOPUP_MIN,
    LimitType.TOPUP_MAX,
    LimitType.WALLET_DAILY_TOPUP_CAP,
    LimitType.WITHDRAWAL_DAILY_CAP,
    LimitType.CARD_PAYMENT_DAILY_CAP,
}
COUNT_LIMIT_TYPES = {LimitType.MAX_CARDS_PER_USER}


class LimitRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A configurable plafond (cahier des charges §14.9).

    ``country_code`` and ``kyc_level`` are nullable — null means "applies to
    everyone unless a more specific rule exists". Nothing about a market's
    limits is hardcoded in business logic; it is all data here.
    """

    __tablename__ = "limit_rules"

    country_code: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("countries.code"), nullable=True
    )
    kyc_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limit_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    max_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    max_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
