import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    InsufficientBalanceError,
    NotFoundError,
    ValidationError,
)
from app.modules.audit.service import AuditService
from app.modules.auth.models import User
from app.modules.fees.service import calculate_withdrawal_fee
from app.modules.ledger.service import LedgerService
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import NotificationService
from app.modules.providers.registry import get_payment_provider
from app.modules.wallets.service import WalletService, wallet_account_id
from app.modules.withdrawals.models import Withdrawal, WithdrawalStatus


def _provider_account_id(provider_name: str) -> str:
    return f"provider:{provider_name}"


class WithdrawalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ledger = LedgerService(db)
        self.wallets = WalletService(db)
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)

    async def initiate(self, user: User, amount: Decimal, provider_name: str) -> Withdrawal:
        if amount <= 0:
            raise ValidationError("Le montant doit être positif")

        provider = get_payment_provider(provider_name)
        if provider is None:
            raise ValidationError(f"Moyen de retrait non supporté : {provider_name}")

        wallet = await self.wallets.get_wallet_for_user(user.id)

        wallet_balance = await self.ledger.get_account_balance(
            wallet_account_id(wallet.id), wallet.currency_code
        )
        if wallet_balance < amount:
            raise InsufficientBalanceError("Solde du wallet insuffisant pour ce retrait")

        fee = calculate_withdrawal_fee(amount)
        net_amount = amount - fee

        result = await provider.initiate_payout(
            amount, wallet.currency_code, user.phone, reference=str(uuid.uuid4())
        )

        withdrawal = Withdrawal(
            user_id=user.id,
            wallet_id=wallet.id,
            amount=amount,
            fee_amount=fee,
            net_amount=net_amount,
            currency_code=wallet.currency_code,
            provider_name=provider_name,
            provider_reference=result.provider_reference,
            status=WithdrawalStatus.PENDING.value,
        )
        self.db.add(withdrawal)
        await self.db.flush()

        await self.audit.log(
            actor_type="user", actor_id=user.id, action="withdrawal.initiated",
            target_type="withdrawal", target_id=str(withdrawal.id),
            context={"amount": str(amount), "provider": provider_name},
        )
        return withdrawal

    async def get_withdrawal(
        self, withdrawal_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Withdrawal:
        withdrawal = await self.db.get(Withdrawal, withdrawal_id)
        if withdrawal is None:
            raise NotFoundError("Retrait introuvable")
        if user_id is not None and withdrawal.user_id != user_id:
            raise ForbiddenError("Ce retrait n'appartient pas à cet utilisateur")
        return withdrawal

    async def list_for_user(self, user_id: uuid.UUID) -> list[Withdrawal]:
        result = await self.db.execute(
            select(Withdrawal)
            .where(Withdrawal.user_id == user_id)
            .order_by(Withdrawal.created_at.desc())
        )
        return list(result.scalars())

    async def simulate_success(self, withdrawal_id: uuid.UUID) -> Withdrawal:
        withdrawal = await self.get_withdrawal(withdrawal_id)
        if withdrawal.status != WithdrawalStatus.PENDING.value:
            raise ConflictError(f"Ce retrait est déjà '{withdrawal.status}'")

        # Balance can move between initiate() and confirm(); the debit must
        # be re-validated right before it actually happens, not trusted from
        # the earlier check.
        wallet_balance = await self.ledger.get_account_balance(
            wallet_account_id(withdrawal.wallet_id), withdrawal.currency_code
        )
        if wallet_balance < withdrawal.amount:
            raise InsufficientBalanceError("Solde du wallet insuffisant pour confirmer ce retrait")

        await self.ledger.record_transaction(
            transaction_type="WITHDRAWAL_SUCCESS",
            reference=f"withdrawal:{withdrawal.id}",
            entries=[
                {
                    "account_id": wallet_account_id(withdrawal.wallet_id),
                    "direction": "debit",
                    "amount": withdrawal.amount,
                    "currency": withdrawal.currency_code,
                },
                {
                    "account_id": _provider_account_id(withdrawal.provider_name),
                    "direction": "credit",
                    "amount": withdrawal.net_amount,
                    "currency": withdrawal.currency_code,
                },
                {
                    "account_id": "revenue:nasrcash",
                    "direction": "credit",
                    "amount": withdrawal.fee_amount,
                    "currency": withdrawal.currency_code,
                },
            ],
            description=f"Retrait via {withdrawal.provider_name}",
        )

        withdrawal.status = WithdrawalStatus.SUCCESSFUL.value
        withdrawal.confirmed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="withdrawal.success", target_type="withdrawal",
            target_id=str(withdrawal.id),
        )
        await self.notifications.create(
            withdrawal.user_id, NotificationType.WITHDRAWAL_SUCCESSFUL.value,
            "Retrait effectué",
            f"{withdrawal.net_amount} {withdrawal.currency_code} envoyés vers "
            f"{withdrawal.provider_name}.",
        )
        return withdrawal

    async def simulate_failure(self, withdrawal_id: uuid.UUID, reason: str) -> Withdrawal:
        withdrawal = await self.get_withdrawal(withdrawal_id)
        if withdrawal.status != WithdrawalStatus.PENDING.value:
            raise ConflictError(f"Ce retrait est déjà '{withdrawal.status}'")

        withdrawal.status = WithdrawalStatus.FAILED.value
        withdrawal.failure_reason = reason
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="withdrawal.failed", target_type="withdrawal",
            target_id=str(withdrawal.id), context={"reason": reason},
        )
        await self.notifications.create(
            withdrawal.user_id, NotificationType.WITHDRAWAL_FAILED.value,
            "Retrait échoué",
            f"Votre retrait de {withdrawal.amount} {withdrawal.currency_code} a échoué : {reason}.",
        )
        return withdrawal
