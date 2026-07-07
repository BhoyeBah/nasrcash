from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Country(TimestampMixin, Base):
    """Per-country configuration. Nothing about a market is hardcoded in
    business logic — new countries are added here, not in code."""

    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)  # ISO 3166-1 alpha-2, e.g. "GN"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217, e.g. "GNF"
    phone_prefix: Mapped[str] = mapped_column(String(5), nullable=False)  # e.g. "+224"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
