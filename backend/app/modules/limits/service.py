import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import LimitExceededError, NotFoundError, ValidationError
from app.modules.auth.models import User
from app.modules.cards.models import Card, CardStatus
from app.modules.limits.models import AMOUNT_LIMIT_TYPES, COUNT_LIMIT_TYPES, LimitRule, LimitType
from app.modules.payments.models import CardPayment, PaymentStatus
from app.modules.topups.models import Topup, TopupStatus
from app.modules.withdrawals.models import Withdrawal, WithdrawalStatus

# Rolling 24h window rather than a calendar-day reset — avoids having to
# reason about which timezone "midnight" means for a given country.
ROLLING_WINDOW = timedelta(hours=24)


class LimitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_rule(
        self, limit_type: LimitType, country_code: str, kyc_level: int
    ) -> LimitRule | None:
        result = await self.db.execute(
            select(LimitRule).where(
                LimitRule.limit_type == limit_type.value,
                LimitRule.is_active.is_(True),
                or_(LimitRule.country_code.is_(None), LimitRule.country_code == country_code),
                or_(LimitRule.kyc_level.is_(None), LimitRule.kyc_level == kyc_level),
            )
        )
        rules = list(result.scalars())
        if not rules:
            return None
        # Most specific match wins: country+level > country-only > level-only > global.
        return max(rules, key=lambda r: (r.country_code is not None) + (r.kyc_level is not None))

    async def check_topup_amount(self, user: User, amount: Decimal) -> None:
        min_rule = await self._get_rule(LimitType.TOPUP_MIN, user.country_code, user.kyc_level)
        if min_rule and min_rule.max_amount is not None and amount < min_rule.max_amount:
            raise ValidationError(
                f"Le montant minimum de recharge est {min_rule.max_amount} GNF"
            )

        max_rule = await self._get_rule(LimitType.TOPUP_MAX, user.country_code, user.kyc_level)
        if max_rule and max_rule.max_amount is not None and amount > max_rule.max_amount:
            raise LimitExceededError(
                f"Le montant maximum de recharge est {max_rule.max_amount} GNF"
            )

    async def check_wallet_daily_topup_cap(self, user: User, additional_amount: Decimal) -> None:
        rule = await self._get_rule(
            LimitType.WALLET_DAILY_TOPUP_CAP, user.country_code, user.kyc_level
        )
        if rule is None or rule.max_amount is None:
            return

        since = datetime.now(timezone.utc) - ROLLING_WINDOW
        result = await self.db.execute(
            select(func.coalesce(func.sum(Topup.net_amount), 0)).where(
                Topup.user_id == user.id,
                Topup.status == TopupStatus.SUCCESSFUL.value,
                Topup.confirmed_at >= since,
            )
        )
        already = Decimal(result.scalar_one())
        if already + additional_amount > rule.max_amount:
            raise LimitExceededError(
                f"Plafond de recharge glissant sur 24h dépassé "
                f"({rule.max_amount} GNF, déjà {already} GNF)"
            )

    async def check_withdrawal_daily_cap(self, user: User, additional_amount: Decimal) -> None:
        rule = await self._get_rule(
            LimitType.WITHDRAWAL_DAILY_CAP, user.country_code, user.kyc_level
        )
        if rule is None or rule.max_amount is None:
            return

        since = datetime.now(timezone.utc) - ROLLING_WINDOW
        result = await self.db.execute(
            select(func.coalesce(func.sum(Withdrawal.amount), 0)).where(
                Withdrawal.user_id == user.id,
                Withdrawal.status == WithdrawalStatus.SUCCESSFUL.value,
                Withdrawal.confirmed_at >= since,
            )
        )
        already = Decimal(result.scalar_one())
        if already + additional_amount > rule.max_amount:
            raise LimitExceededError(
                f"Plafond de retrait glissant sur 24h dépassé "
                f"({rule.max_amount} GNF, déjà {already} GNF)"
            )

    async def check_card_payment_daily_cap(self, user: User, additional_amount: Decimal) -> None:
        rule = await self._get_rule(
            LimitType.CARD_PAYMENT_DAILY_CAP, user.country_code, user.kyc_level
        )
        if rule is None or rule.max_amount is None:
            return

        since = datetime.now(timezone.utc) - ROLLING_WINDOW
        result = await self.db.execute(
            select(func.coalesce(func.sum(CardPayment.total_debited), 0))
            .join(Card, Card.id == CardPayment.card_id)
            .where(
                Card.user_id == user.id,
                CardPayment.status == PaymentStatus.SETTLED.value,
                CardPayment.created_at >= since,
            )
        )
        already = Decimal(result.scalar_one())
        if already + additional_amount > rule.max_amount:
            raise LimitExceededError(
                f"Plafond de paiement carte glissant sur 24h dépassé "
                f"({rule.max_amount} GNF, déjà {already} GNF)"
            )

    async def check_max_cards(self, user: User) -> None:
        rule = await self._get_rule(LimitType.MAX_CARDS_PER_USER, user.country_code, user.kyc_level)
        if rule is None or rule.max_count is None:
            return

        result = await self.db.execute(
            select(func.count()).select_from(Card).where(
                Card.user_id == user.id, Card.status != CardStatus.CLOSED.value
            )
        )
        current_count = result.scalar_one()
        if current_count >= rule.max_count:
            raise LimitExceededError(
                f"Nombre maximum de cartes atteint ({rule.max_count})"
            )

    # --- admin management (CRUD over the rules themselves) ---

    async def list_rules(self, active_only: bool = False) -> list[LimitRule]:
        query = select(LimitRule).order_by(LimitRule.limit_type, LimitRule.created_at.desc())
        if active_only:
            query = query.where(LimitRule.is_active.is_(True))
        result = await self.db.execute(query)
        return list(result.scalars())

    async def create_rule(
        self,
        limit_type: str,
        country_code: str | None,
        kyc_level: int | None,
        max_amount: Decimal | None,
        max_count: int | None,
    ) -> LimitRule:
        if limit_type not in {t.value for t in LimitType}:
            raise ValidationError(f"Type de plafond invalide : {limit_type}")
        if limit_type in {t.value for t in AMOUNT_LIMIT_TYPES} and max_amount is None:
            raise ValidationError("max_amount est requis pour ce type de plafond")
        if limit_type in {t.value for t in COUNT_LIMIT_TYPES} and max_count is None:
            raise ValidationError("max_count est requis pour ce type de plafond")

        rule = LimitRule(
            limit_type=limit_type,
            country_code=country_code,
            kyc_level=kyc_level,
            max_amount=max_amount,
            max_count=max_count,
        )
        self.db.add(rule)
        await self.db.flush()
        return rule

    async def deactivate_rule(self, rule_id: uuid.UUID) -> LimitRule:
        rule = await self.db.get(LimitRule, rule_id)
        if rule is None:
            raise NotFoundError("Règle de plafond introuvable")
        rule.is_active = False
        await self.db.flush()
        return rule
