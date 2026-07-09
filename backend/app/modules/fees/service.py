import uuid
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.fees.models import FeeRule, FeeType

# Fallback rates if no fee_rules row matches at all (should only happen if
# the seed migration was skipped) — kept in sync with the original MVP
# flat-rate defaults so behavior never silently becomes "free".
_FALLBACK_RATES = {
    FeeType.TOPUP: Decimal("0.02"),
    FeeType.WITHDRAWAL: Decimal("0.015"),
    FeeType.PAYMENT: Decimal("0.03"),
}


class FeeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_rule(
        self,
        fee_type: FeeType,
        country_code: str | None,
        provider_name: str | None,
        kyc_level: int | None,
    ) -> FeeRule | None:
        result = await self.db.execute(
            select(FeeRule).where(
                FeeRule.fee_type == fee_type.value,
                FeeRule.is_active.is_(True),
                or_(FeeRule.country_code.is_(None), FeeRule.country_code == country_code),
                or_(FeeRule.provider_name.is_(None), FeeRule.provider_name == provider_name),
                or_(FeeRule.kyc_level.is_(None), FeeRule.kyc_level == kyc_level),
            )
        )
        rules = list(result.scalars())
        if not rules:
            return None
        # Most specific match wins: more non-null scoping fields beats fewer.
        return max(
            rules,
            key=lambda r: (
                (r.country_code is not None)
                + (r.provider_name is not None)
                + (r.kyc_level is not None)
            ),
        )

    async def _calculate(
        self,
        fee_type: FeeType,
        amount: Decimal,
        country_code: str | None,
        provider_name: str | None,
        kyc_level: int | None,
    ) -> Decimal:
        rule = await self._get_rule(fee_type, country_code, provider_name, kyc_level)
        if rule is None:
            rate = _FALLBACK_RATES[fee_type]
            fixed = Decimal(0)
        else:
            rate = rule.rate or Decimal(0)
            fixed = rule.fixed_amount

        fee = (amount * rate) + fixed
        return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def calculate_topup_fee(
        self, amount: Decimal, country_code: str | None = None,
        provider_name: str | None = None, kyc_level: int | None = None,
    ) -> Decimal:
        return await self._calculate(FeeType.TOPUP, amount, country_code, provider_name, kyc_level)

    async def calculate_withdrawal_fee(
        self, amount: Decimal, country_code: str | None = None,
        provider_name: str | None = None, kyc_level: int | None = None,
    ) -> Decimal:
        return await self._calculate(
            FeeType.WITHDRAWAL, amount, country_code, provider_name, kyc_level
        )

    async def calculate_payment_fee(
        self, amount: Decimal, country_code: str | None = None,
        provider_name: str | None = None, kyc_level: int | None = None,
    ) -> Decimal:
        return await self._calculate(FeeType.PAYMENT, amount, country_code, provider_name, kyc_level)

    # --- admin management (CRUD over the rules themselves) ---

    async def list_rules(self, active_only: bool = False) -> list[FeeRule]:
        query = select(FeeRule).order_by(FeeRule.fee_type, FeeRule.created_at.desc())
        if active_only:
            query = query.where(FeeRule.is_active.is_(True))
        result = await self.db.execute(query)
        return list(result.scalars())

    async def create_rule(
        self,
        fee_type: str,
        country_code: str | None,
        provider_name: str | None,
        kyc_level: int | None,
        rate: Decimal | None,
        fixed_amount: Decimal | None,
    ) -> FeeRule:
        if fee_type not in {t.value for t in FeeType}:
            raise ValidationError(f"Type de frais invalide : {fee_type}")
        if rate is None and (fixed_amount is None or fixed_amount == 0):
            raise ValidationError("Un taux ou un montant fixe est requis")

        rule = FeeRule(
            fee_type=fee_type,
            country_code=country_code,
            provider_name=provider_name,
            kyc_level=kyc_level,
            rate=rate,
            fixed_amount=fixed_amount or Decimal(0),
        )
        self.db.add(rule)
        await self.db.flush()
        return rule

    async def deactivate_rule(self, rule_id: uuid.UUID) -> FeeRule:
        rule = await self.db.get(FeeRule, rule_id)
        if rule is None:
            raise NotFoundError("Règle de frais introuvable")
        rule.is_active = False
        await self.db.flush()
        return rule
