from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.limits.models import LimitRule, LimitType

# Sandbox starting plafonds for the pilot market — updatable at any time via
# the admin /limits endpoints, never hardcoded into business logic. Amounts
# are in GNF, the pilot currency.
SEED_RULES = [
    # Global defaults (kyc_level=None applies to everyone unless overridden).
    {"limit_type": LimitType.TOPUP_MIN.value, "max_amount": "1000"},
    {"limit_type": LimitType.TOPUP_MAX.value, "max_amount": "2000000"},
    {"limit_type": LimitType.WALLET_DAILY_TOPUP_CAP.value, "max_amount": "3000000"},
    {"limit_type": LimitType.WITHDRAWAL_DAILY_CAP.value, "max_amount": "2000000"},
    {"limit_type": LimitType.MAX_CARDS_PER_USER.value, "max_count": 3},
    # KYC level 2 overrides — higher trust, higher ceilings.
    {"limit_type": LimitType.TOPUP_MAX.value, "kyc_level": 2, "max_amount": "10000000"},
    {"limit_type": LimitType.WALLET_DAILY_TOPUP_CAP.value, "kyc_level": 2, "max_amount": "15000000"},
    {"limit_type": LimitType.WITHDRAWAL_DAILY_CAP.value, "kyc_level": 2, "max_amount": "10000000"},
    {"limit_type": LimitType.CARD_PAYMENT_DAILY_CAP.value, "kyc_level": 2, "max_amount": "5000000"},
]


async def seed_limit_rules(db: AsyncSession) -> None:
    for rule in SEED_RULES:
        db.add(LimitRule(**rule))
    await db.flush()
