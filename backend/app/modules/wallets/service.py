import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.ledger.models import LedgerEntry
from app.modules.ledger.service import LedgerService
from app.modules.wallets.models import Wallet


def wallet_account_id(wallet_id: uuid.UUID) -> str:
    return f"wallet:{wallet_id}"


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ledger = LedgerService(db)

    async def create_wallet_for_user(
        self, user_id: uuid.UUID, country_code: str, currency_code: str
    ) -> Wallet:
        wallet = Wallet(user_id=user_id, country_code=country_code, currency_code=currency_code)
        self.db.add(wallet)
        await self.db.flush()
        return wallet

    async def get_wallet_for_user(self, user_id: uuid.UUID) -> Wallet:
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = result.scalar_one_or_none()
        if wallet is None:
            raise NotFoundError("Aucun wallet trouvé pour cet utilisateur")
        return wallet

    async def get_wallet_by_id(self, wallet_id: uuid.UUID, user_id: uuid.UUID) -> Wallet:
        wallet = await self.db.get(Wallet, wallet_id)
        if wallet is None:
            raise NotFoundError("Wallet introuvable")
        if wallet.user_id != user_id:
            raise ForbiddenError("Ce wallet n'appartient pas à cet utilisateur")
        return wallet

    async def get_balance(self, wallet: Wallet) -> Decimal:
        balance = await self.ledger.get_account_balance(
            wallet_account_id(wallet.id), wallet.currency_code
        )
        wallet.cached_available_balance = balance
        await self.db.flush()
        return balance

    async def get_transactions(
        self, wallet: Wallet, limit: int = 50, offset: int = 0
    ) -> list[LedgerEntry]:
        return await self.ledger.get_account_entries(
            wallet_account_id(wallet.id), limit=limit, offset=offset
        )
