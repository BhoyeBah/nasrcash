from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees.models import FeeRule, FeeType

# Sandbox starting rates — same values as the original MVP flat-rate
# settings, now expressed as data instead of code so they can be edited
# live via the admin /fees endpoints.
SEED_RULES = [
    {"fee_type": FeeType.TOPUP.value, "rate": "0.02"},
    {"fee_type": FeeType.WITHDRAWAL.value, "rate": "0.015"},
    {"fee_type": FeeType.PAYMENT.value, "rate": "0.03"},
]


async def seed_fee_rules(db: AsyncSession) -> None:
    for rule in SEED_RULES:
        db.add(FeeRule(**rule))
    await db.flush()
