import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    InsufficientBalanceError,
    LimitExceededError,
    NotFoundError,
    ValidationError,
)
from app.modules.audit.service import AuditService
from app.modules.auth.models import User
from app.modules.cards.models import Card, CardStatus
from app.modules.compliance.service import ComplianceService
from app.modules.ledger.models import LedgerEntry
from app.modules.ledger.service import LedgerService
from app.modules.limits.service import LimitService
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import NotificationService
from app.modules.providers.registry import get_card_provider
from app.modules.wallets.service import WalletService, wallet_account_id

REQUIRED_KYC_LEVEL_FOR_CARD = 2


def card_account_id(card_id: uuid.UUID) -> str:
    return f"card:{card_id}"


class CardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ledger = LedgerService(db)
        self.wallets = WalletService(db)
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)
        self.limits = LimitService(db)
        self.compliance = ComplianceService(db)
        self.provider = get_card_provider()

    async def issue_card(self, user: User) -> Card:
        if user.kyc_level < REQUIRED_KYC_LEVEL_FOR_CARD:
            raise ForbiddenError(
                f"Niveau KYC {REQUIRED_KYC_LEVEL_FOR_CARD} requis pour créer une carte"
            )
        try:
            await self.limits.check_max_cards(user)
        except LimitExceededError:
            await self.compliance.record_limit_breach(user.id, "max_cards_per_user", {})
            raise

        wallet = await self.wallets.get_wallet_for_user(user.id)
        result = await self.provider.create_card(user.id, wallet.currency_code)

        card = Card(
            user_id=user.id,
            provider_name=self.provider.provider_name,
            provider_card_id=result.provider_card_id,
            masked_pan=result.masked_pan,
            last4=result.last4,
            brand=result.brand,
            displayed_currency=wallet.currency_code,
            status=CardStatus.ACTIVE.value,
            expiry_month=result.expiry_month,
            expiry_year=result.expiry_year,
        )
        self.db.add(card)
        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=user.id, action="card.issued", target_type="card",
            target_id=str(card.id),
        )
        await self.notifications.create(
            user.id, NotificationType.CARD_CREATED.value,
            "Carte créée", f"Votre carte virtuelle {card.masked_pan} est prête.",
        )
        return card

    async def get_card(self, card_id: uuid.UUID, user_id: uuid.UUID) -> Card:
        card = await self.db.get(Card, card_id)
        if card is None:
            raise NotFoundError("Carte introuvable")
        if card.user_id != user_id:
            raise ForbiddenError("Cette carte n'appartient pas à cet utilisateur")
        return card

    async def list_for_user(self, user_id: uuid.UUID) -> list[Card]:
        result = await self.db.execute(select(Card).where(Card.user_id == user_id))
        return list(result.scalars())

    async def freeze(self, card: Card) -> Card:
        if card.status != CardStatus.ACTIVE.value:
            raise ConflictError(f"Impossible de geler une carte au statut '{card.status}'")
        await self.provider.freeze_card(card.provider_card_id)
        card.status = CardStatus.FROZEN.value
        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=card.user_id, action="card.frozen", target_type="card",
            target_id=str(card.id),
        )
        await self.notifications.create(
            card.user_id, NotificationType.CARD_FROZEN.value,
            "Carte gelée", f"Votre carte {card.masked_pan} a été gelée.",
        )
        return card

    async def unfreeze(self, card: Card) -> Card:
        if card.status != CardStatus.FROZEN.value:
            raise ConflictError(f"Impossible de dégeler une carte au statut '{card.status}'")
        await self.provider.unfreeze_card(card.provider_card_id)
        card.status = CardStatus.ACTIVE.value
        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=card.user_id, action="card.unfrozen", target_type="card",
            target_id=str(card.id),
        )
        return card

    async def close(self, card: Card) -> Card:
        if card.status == CardStatus.CLOSED.value:
            raise ConflictError("Cette carte est déjà fermée")
        await self.provider.close_card(card.provider_card_id)
        card.status = CardStatus.CLOSED.value
        await self.db.flush()
        await self.audit.log(
            actor_type="user", actor_id=card.user_id, action="card.closed", target_type="card",
            target_id=str(card.id),
        )
        return card

    async def get_balance(self, card: Card) -> Decimal:
        balance = await self.ledger.get_account_balance(
            card_account_id(card.id), card.displayed_currency
        )
        card.cached_available_balance = balance
        await self.db.flush()
        return balance

    async def get_transactions(
        self, card: Card, limit: int = 50, offset: int = 0
    ) -> list[LedgerEntry]:
        return await self.ledger.get_account_entries(
            card_account_id(card.id), limit=limit, offset=offset
        )

    async def fund(self, card: Card, user: User, amount: Decimal, idempotency_key: str) -> Card:
        if amount <= 0:
            raise ValidationError("Le montant doit être positif")
        if card.status != CardStatus.ACTIVE.value:
            raise ConflictError(f"Impossible de recharger une carte au statut '{card.status}'")

        reference = f"card_topup:{idempotency_key}"
        if await self.ledger.get_transaction_by_reference(reference) is not None:
            return card  # already applied — replaying the same request is a no-op

        wallet = await self.wallets.get_wallet_for_user(user.id)
        wallet_balance = await self.ledger.get_account_balance(
            wallet_account_id(wallet.id), wallet.currency_code
        )
        if wallet_balance < amount:
            raise InsufficientBalanceError("Solde du wallet insuffisant")

        await self.ledger.record_transaction(
            transaction_type="CARD_TOPUP",
            reference=reference,
            entries=[
                {
                    "account_id": wallet_account_id(wallet.id),
                    "direction": "debit",
                    "amount": amount,
                    "currency": wallet.currency_code,
                },
                {
                    "account_id": card_account_id(card.id),
                    "direction": "credit",
                    "amount": amount,
                    "currency": card.displayed_currency,
                },
            ],
        )
        await self.audit.log(
            actor_type="user", actor_id=user.id, action="card.funded", target_type="card",
            target_id=str(card.id), context={"amount": str(amount)},
        )
        await self.notifications.create(
            user.id, NotificationType.CARD_FUNDED.value,
            "Carte rechargée",
            f"Votre carte {card.masked_pan} a été rechargée de {amount} {card.displayed_currency}.",
        )
        return card
