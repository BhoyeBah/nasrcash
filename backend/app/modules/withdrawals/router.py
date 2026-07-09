import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.wallets.service import WalletService
from app.modules.withdrawals.schemas import WithdrawalRequest, WithdrawalResponse
from app.modules.withdrawals.service import WithdrawalService

router = APIRouter(prefix="/api/v1", tags=["withdrawals"])


@router.post("/wallets/{wallet_id}/withdrawals", response_model=WithdrawalResponse)
async def create_withdrawal(
    wallet_id: uuid.UUID,
    payload: WithdrawalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership check: a wallet's withdrawal can only be initiated by its owner.
    await WalletService(db).get_wallet_by_id(wallet_id, current_user.id)

    service = WithdrawalService(db)
    withdrawal = await service.initiate(current_user, payload.amount, payload.provider_name)
    await db.commit()
    return withdrawal


@router.get("/withdrawals", response_model=list[WithdrawalResponse])
async def list_withdrawals(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = WithdrawalService(db)
    return await service.list_for_user(current_user.id)


@router.get("/withdrawals/{withdrawal_id}", response_model=WithdrawalResponse)
async def get_withdrawal(
    withdrawal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WithdrawalService(db)
    return await service.get_withdrawal(withdrawal_id, current_user.id)
