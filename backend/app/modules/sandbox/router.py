import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.sandbox.dependencies import require_sandbox_mode
from app.modules.sandbox.schemas import SimulateFailureRequest
from app.modules.topups.schemas import TopupResponse
from app.modules.topups.service import TopupService

router = APIRouter(
    prefix="/api/v1/sandbox", tags=["sandbox"], dependencies=[Depends(require_sandbox_mode)]
)


@router.post("/topups/{topup_id}/simulate-success", response_model=TopupResponse)
async def simulate_topup_success(topup_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = TopupService(db)
    topup = await service.simulate_success(topup_id)
    await db.commit()
    return topup


@router.post("/topups/{topup_id}/simulate-failure", response_model=TopupResponse)
async def simulate_topup_failure(
    topup_id: uuid.UUID,
    payload: SimulateFailureRequest,
    db: AsyncSession = Depends(get_db),
):
    service = TopupService(db)
    topup = await service.simulate_failure(topup_id, payload.reason)
    await db.commit()
    return topup
