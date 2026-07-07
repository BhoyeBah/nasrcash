from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.fx.models import FxRate


class FXService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_rate(self, base_currency: str, quote_currency: str) -> FxRate:
        result = await self.db.execute(
            select(FxRate)
            .where(
                FxRate.base_currency == base_currency,
                FxRate.quote_currency == quote_currency,
                FxRate.is_active.is_(True),
            )
            .order_by(FxRate.created_at.desc())
            .limit(1)
        )
        rate = result.scalar_one_or_none()
        if rate is None:
            raise NotFoundError(
                f"Aucun taux de change configuré pour {base_currency}/{quote_currency}"
            )
        return rate

    async def set_rate(self, base_currency: str, quote_currency: str, rate: Decimal) -> FxRate:
        if rate <= 0:
            raise ValidationError("Le taux de change doit être positif")
        fx_rate = FxRate(base_currency=base_currency, quote_currency=quote_currency, rate=rate)
        self.db.add(fx_rate)
        await self.db.flush()
        return fx_rate

    async def convert(
        self, amount: Decimal, base_currency: str, quote_currency: str
    ) -> tuple[Decimal, FxRate]:
        """Converts and returns the FxRate actually used, so the caller can
        freeze it onto the transaction record — a payment's rate must never
        be recalculated after the fact."""
        fx_rate = await self.get_current_rate(base_currency, quote_currency)
        converted = (amount * fx_rate.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return converted, fx_rate
