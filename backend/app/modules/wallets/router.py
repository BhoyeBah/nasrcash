import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.wallets.schemas import LedgerEntryResponse, WalletBalanceResponse, WalletResponse
from app.modules.wallets.service import WalletService

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


@router.get("", response_model=list[WalletResponse])
async def list_wallets(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = WalletService(db)
    wallet = await service.get_wallet_for_user(current_user.id)
    return [wallet]


@router.get("/{wallet_id}/balance", response_model=WalletBalanceResponse)
async def get_balance(
    wallet_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WalletService(db)
    wallet = await service.get_wallet_by_id(wallet_id, current_user.id)
    balance = await service.get_balance(wallet)
    await db.commit()
    return WalletBalanceResponse(
        wallet_id=wallet.id, currency_code=wallet.currency_code, available_balance=balance
    )


@router.get("/{wallet_id}/transactions", response_model=list[LedgerEntryResponse])
async def get_transactions(
    wallet_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WalletService(db)
    wallet = await service.get_wallet_by_id(wallet_id, current_user.id)
    return await service.get_transactions(wallet, limit=limit, offset=offset)
