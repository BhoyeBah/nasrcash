from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.countries.models import Country

# Guinea is the pilot market. Adding a new market later is a data change here,
# never a code change in business logic.
SEED_COUNTRIES = [
    {
        "code": "GN",
        "name": "Guinée",
        "currency_code": "GNF",
        "phone_prefix": "+224",
        "is_active": True,
    },
]


async def seed_countries(db: AsyncSession) -> None:
    for country in SEED_COUNTRIES:
        stmt = insert(Country).values(**country).on_conflict_do_nothing(index_elements=["code"])
        await db.execute(stmt)
    await db.flush()
