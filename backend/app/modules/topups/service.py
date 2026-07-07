import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.modules.audit.service import AuditService
from app.modules.auth.models import User
from app.modules.fees.service import calculate_topup_fee
from app.modules.ledger.service import LedgerService
from app.modules.providers.registry import get_payment_provider
from app.modules.topups.models import Topup, TopupStatus
from app.modules.wallets.service import WalletService, wallet_account_id


def _provider_account_id(provider_name: str) -> str:
    return f"provider:{provider_name}"


class TopupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ledger = LedgerService(db)
        self.wallets = WalletService(db)
        self.audit = AuditService(db)

    async def initiate(self, user: User, amount: Decimal, provider_name: str) -> Topup:
        if amount <= 0:
            raise ValidationError("Le montant doit être positif")

        provider = get_payment_provider(provider_name)
        if provider is None:
            raise ValidationError(f"Moyen de recharge non supporté : {provider_name}")

        wallet = await self.wallets.get_wallet_for_user(user.id)

        fee = calculate_topup_fee(amount)
        net_amount = amount - fee

        result = await provider.initiate_topup(
            amount, wallet.currency_code, user.phone, reference=str(uuid.uuid4())
        )

        topup = Topup(
            user_id=user.id,
            wallet_id=wallet.id,
            amount=amount,
            fee_amount=fee,
            net_amount=net_amount,
            currency_code=wallet.currency_code,
            provider_name=provider_name,
            provider_reference=result.provider_reference,
            status=TopupStatus.PENDING.value,
        )
        self.db.add(topup)
        await self.db.flush()

        await self.audit.log(
            actor_type="user", actor_id=user.id, action="topup.initiated",
            target_type="topup", target_id=str(topup.id),
            context={"amount": str(amount), "provider": provider_name},
        )
        return topup

    async def get_topup(self, topup_id: uuid.UUID, user_id: uuid.UUID | None = None) -> Topup:
        topup = await self.db.get(Topup, topup_id)
        if topup is None:
            raise NotFoundError("Recharge introuvable")
        if user_id is not None and topup.user_id != user_id:
            raise ForbiddenError("Cette recharge n'appartient pas à cet utilisateur")
        return topup

    async def list_for_user(self, user_id: uuid.UUID) -> list[Topup]:
        result = await self.db.execute(
            select(Topup).where(Topup.user_id == user_id).order_by(Topup.created_at.desc())
        )
        return list(result.scalars())

    async def simulate_success(self, topup_id: uuid.UUID) -> Topup:
        topup = await self.get_topup(topup_id)
        if topup.status != TopupStatus.PENDING.value:
            raise ConflictError(f"Cette recharge est déjà '{topup.status}'")

        await self.ledger.record_transaction(
            transaction_type="TOPUP_SUCCESS",
            reference=f"topup:{topup.id}",
            entries=[
                {
                    "account_id": _provider_account_id(topup.provider_name),
                    "direction": "debit",
                    "amount": topup.amount,
                    "currency": topup.currency_code,
                },
                {
                    "account_id": wallet_account_id(topup.wallet_id),
                    "direction": "credit",
                    "amount": topup.net_amount,
                    "currency": topup.currency_code,
                },
                {
                    "account_id": "revenue:nasrcash",
                    "direction": "credit",
                    "amount": topup.fee_amount,
                    "currency": topup.currency_code,
                },
            ],
            description=f"Topup via {topup.provider_name}",
        )

        topup.status = TopupStatus.SUCCESSFUL.value
        topup.confirmed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="topup.success", target_type="topup",
            target_id=str(topup.id),
        )
        return topup

    async def simulate_failure(self, topup_id: uuid.UUID, reason: str) -> Topup:
        topup = await self.get_topup(topup_id)
        if topup.status != TopupStatus.PENDING.value:
            raise ConflictError(f"Cette recharge est déjà '{topup.status}'")

        topup.status = TopupStatus.FAILED.value
        topup.failure_reason = reason
        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="topup.failed", target_type="topup",
            target_id=str(topup.id), context={"reason": reason},
        )
        return topup
