from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FxRate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Append-only FX rate history. Setting a new rate never updates a row
    in place — it inserts a new one, so every past rate stays queryable and
    a payment's frozen rate can always be traced back to what was current
    at authorization time."""

    __tablename__ = "fx_rates"

    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)  # 1 base = rate quote
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
