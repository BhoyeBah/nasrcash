from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fx.models import FxRate

# Sandbox starting rate for the pilot market — updatable at any time via
# POST /api/v1/sandbox/fx/update-rate, never hardcoded into business logic.
SEED_RATES = [
    {"base_currency": "USD", "quote_currency": "GNF", "rate": "9000"},
    {"base_currency": "EUR", "quote_currency": "GNF", "rate": "9700"},
]


async def seed_fx_rates(db: AsyncSession) -> None:
    for entry in SEED_RATES:
        db.add(FxRate(**entry))
    await db.flush()
