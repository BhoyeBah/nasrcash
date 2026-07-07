import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.topups.schemas import TopupRequest, TopupResponse
from app.modules.topups.service import TopupService
from app.modules.wallets.service import WalletService

router = APIRouter(prefix="/api/v1", tags=["topups"])


@router.post("/wallets/{wallet_id}/topup", response_model=TopupResponse)
async def create_topup(
    wallet_id: uuid.UUID,
    payload: TopupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership check: a wallet's topup can only be initiated by its owner.
    await WalletService(db).get_wallet_by_id(wallet_id, current_user.id)

    service = TopupService(db)
    topup = await service.initiate(current_user, payload.amount, payload.provider_name)
    await db.commit()
    return topup


@router.get("/topups", response_model=list[TopupResponse])
async def list_topups(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = TopupService(db)
    return await service.list_for_user(current_user.id)


@router.get("/topups/{topup_id}", response_model=TopupResponse)
async def get_topup(
    topup_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TopupService(db)
    return await service.get_topup(topup_id, current_user.id)
