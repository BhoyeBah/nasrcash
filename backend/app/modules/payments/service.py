import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, LimitExceededError, NotFoundError, ValidationError
from app.modules.audit.service import AuditService
from app.modules.auth.models import User
from app.modules.cards.models import Card, CardStatus
from app.modules.cards.service import card_account_id
from app.modules.fees.service import calculate_payment_fee
from app.modules.fx.service import FXService
from app.modules.ledger.service import LedgerService
from app.modules.limits.service import LimitService
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import NotificationService
from app.modules.payments.models import CardPayment, DeclineReason, PaymentStatus


def settlement_account_id(provider_name: str = "visa") -> str:
    return f"settlement:{provider_name}"


REVENUE_ACCOUNT_ID = "revenue:nasrcash"


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ledger = LedgerService(db)
        self.fx = FXService(db)
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)
        self.limits = LimitService(db)

    async def get_payment(self, payment_id: uuid.UUID) -> CardPayment:
        payment = await self.db.get(CardPayment, payment_id)
        if payment is None:
            raise NotFoundError("Paiement introuvable")
        return payment

    async def list_for_card(self, card_id: uuid.UUID) -> list[CardPayment]:
        result = await self.db.execute(
            select(CardPayment)
            .where(CardPayment.card_id == card_id)
            .order_by(CardPayment.created_at.desc())
        )
        return list(result.scalars())

    async def _existing_by_reference(self, provider_reference: str) -> CardPayment | None:
        result = await self.db.execute(
            select(CardPayment).where(CardPayment.provider_reference == provider_reference)
        )
        return result.scalar_one_or_none()

    async def _decline(
        self,
        card: Card,
        merchant_name: str,
        merchant_amount: Decimal,
        merchant_currency: str,
        provider_reference: str,
        reason: str,
        fx_rate: Decimal = Decimal(0),
        local_amount: Decimal = Decimal(0),
        fees_amount: Decimal = Decimal(0),
    ) -> CardPayment:
        payment = CardPayment(
            card_id=card.id,
            merchant_name=merchant_name,
            merchant_currency=merchant_currency,
            merchant_amount=merchant_amount,
            fx_rate=fx_rate,
            local_currency=card.displayed_currency,
            local_amount=local_amount,
            fees_amount=fees_amount,
            total_debited=Decimal(0),
            status=PaymentStatus.DECLINED.value,
            decline_reason=reason,
            provider_reference=provider_reference,
        )
        self.db.add(payment)
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="payment.declined", target_type="card_payment",
            target_id=str(payment.id), context={"reason": reason},
        )
        await self.notifications.create(
            card.user_id, NotificationType.PAYMENT_DECLINED.value,
            "Paiement refusé",
            f"Paiement de {merchant_amount} {merchant_currency} chez {merchant_name} refusé "
            f"({reason}).",
        )
        return payment

    async def simulate_payment(
        self,
        card: Card,
        merchant_name: str,
        merchant_amount: Decimal,
        merchant_currency: str,
        provider_reference: str,
    ) -> CardPayment:
        if merchant_amount <= 0:
            raise ValidationError("Le montant marchand doit être positif")

        existing = await self._existing_by_reference(provider_reference)
        if existing is not None:
            return existing

        if card.status == CardStatus.FROZEN.value:
            return await self._decline(
                card, merchant_name, merchant_amount, merchant_currency, provider_reference,
                DeclineReason.CARD_FROZEN.value,
            )
        if card.status != CardStatus.ACTIVE.value:
            return await self._decline(
                card, merchant_name, merchant_amount, merchant_currency, provider_reference,
                DeclineReason.CARD_BLOCKED.value,
            )

        local_amount, fx_rate = await self.fx.convert(
            merchant_amount, merchant_currency, card.displayed_currency
        )
        fees_amount = calculate_payment_fee(local_amount)
        total_debited = local_amount + fees_amount

        card_balance = await self.ledger.get_account_balance(
            card_account_id(card.id), card.displayed_currency
        )
        if card_balance < total_debited:
            return await self._decline(
                card, merchant_name, merchant_amount, merchant_currency, provider_reference,
                DeclineReason.INSUFFICIENT_BALANCE.value,
                fx_rate=fx_rate.rate, local_amount=local_amount, fees_amount=fees_amount,
            )

        cardholder = await self.db.get(User, card.user_id)
        try:
            await self.limits.check_card_payment_daily_cap(cardholder, total_debited)
        except LimitExceededError:
            return await self._decline(
                card, merchant_name, merchant_amount, merchant_currency, provider_reference,
                DeclineReason.LIMIT_EXCEEDED.value,
                fx_rate=fx_rate.rate, local_amount=local_amount, fees_amount=fees_amount,
            )

        await self.ledger.record_transaction(
            transaction_type="CARD_PAYMENT_WITH_FX",
            reference=f"card_payment:{provider_reference}",
            entries=[
                {
                    "account_id": card_account_id(card.id),
                    "direction": "debit",
                    "amount": total_debited,
                    "currency": card.displayed_currency,
                },
                {
                    "account_id": settlement_account_id(),
                    "direction": "credit",
                    "amount": local_amount,
                    "currency": card.displayed_currency,
                },
                {
                    "account_id": REVENUE_ACCOUNT_ID,
                    "direction": "credit",
                    "amount": fees_amount,
                    "currency": card.displayed_currency,
                },
            ],
            description=f"Paiement {merchant_name}",
        )

        payment = CardPayment(
            card_id=card.id,
            merchant_name=merchant_name,
            merchant_currency=merchant_currency,
            merchant_amount=merchant_amount,
            fx_rate=fx_rate.rate,
            local_currency=card.displayed_currency,
            local_amount=local_amount,
            fees_amount=fees_amount,
            total_debited=total_debited,
            status=PaymentStatus.SETTLED.value,
            provider_reference=provider_reference,
        )
        self.db.add(payment)
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="payment.settled", target_type="card_payment",
            target_id=str(payment.id),
            context={"merchant": merchant_name, "total_debited": str(total_debited)},
        )
        await self.notifications.create(
            card.user_id, NotificationType.PAYMENT_ACCEPTED.value,
            "Paiement accepté",
            f"Paiement de {merchant_amount} {merchant_currency} chez {merchant_name} accepté "
            f"— {total_debited} {card.displayed_currency} débités.",
        )
        return payment

    async def simulate_decline(
        self,
        card: Card,
        merchant_name: str,
        merchant_amount: Decimal,
        merchant_currency: str,
        provider_reference: str,
        reason: str,
    ) -> CardPayment:
        existing = await self._existing_by_reference(provider_reference)
        if existing is not None:
            return existing
        return await self._decline(
            card, merchant_name, merchant_amount, merchant_currency, provider_reference, reason
        )

    async def simulate_refund(self, payment_id: uuid.UUID) -> CardPayment:
        payment = await self.get_payment(payment_id)
        if payment.status != PaymentStatus.SETTLED.value:
            raise ConflictError(f"Impossible de rembourser un paiement '{payment.status}'")

        await self.ledger.record_transaction(
            transaction_type="CARD_REFUND",
            reference=f"card_refund:{payment.provider_reference}",
            entries=[
                {
                    "account_id": settlement_account_id(),
                    "direction": "debit",
                    "amount": payment.local_amount,
                    "currency": payment.local_currency,
                },
                {
                    "account_id": card_account_id(payment.card_id),
                    "direction": "credit",
                    "amount": payment.local_amount,
                    "currency": payment.local_currency,
                },
            ],
            description=f"Remboursement {payment.merchant_name}",
        )

        payment.status = PaymentStatus.REFUNDED.value
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="payment.refunded", target_type="card_payment",
            target_id=str(payment.id),
        )
        return payment
