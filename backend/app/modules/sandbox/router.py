import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.modules.cards.models import Card
from app.modules.fx.schemas import FxRateResponse, UpdateFxRateRequest
from app.modules.fx.service import FXService
from app.modules.payments.schemas import (
    CardPaymentResponse,
    SimulateDeclineRequest,
    SimulatePaymentRequest,
)
from app.modules.payments.service import PaymentService
from app.modules.sandbox.dependencies import require_sandbox_mode
from app.modules.sandbox.schemas import SimulateFailureRequest, SimulateRefundRequest
from app.modules.topups.schemas import TopupResponse
from app.modules.topups.service import TopupService

router = APIRouter(
    prefix="/api/v1/sandbox", tags=["sandbox"], dependencies=[Depends(require_sandbox_mode)]
)


async def _get_card_or_404(db: AsyncSession, card_id: uuid.UUID) -> Card:
    card = await db.get(Card, card_id)
    if card is None:
        raise NotFoundError("Carte introuvable")
    return card


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


@router.post("/cards/{card_id}/simulate-payment", response_model=CardPaymentResponse)
async def simulate_card_payment(
    card_id: uuid.UUID,
    payload: SimulatePaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    card = await _get_card_or_404(db, card_id)
    service = PaymentService(db)
    reference = payload.provider_reference or str(uuid.uuid4())
    payment = await service.simulate_payment(
        card, payload.merchant_name, payload.merchant_amount, payload.merchant_currency, reference
    )
    await db.commit()
    return payment


@router.post("/cards/{card_id}/simulate-decline", response_model=CardPaymentResponse)
async def simulate_card_decline(
    card_id: uuid.UUID,
    payload: SimulateDeclineRequest,
    db: AsyncSession = Depends(get_db),
):
    card = await _get_card_or_404(db, card_id)
    service = PaymentService(db)
    reference = payload.provider_reference or str(uuid.uuid4())
    payment = await service.simulate_decline(
        card,
        payload.merchant_name,
        payload.merchant_amount,
        payload.merchant_currency,
        reference,
        payload.reason,
    )
    await db.commit()
    return payment


@router.post("/cards/{card_id}/simulate-refund", response_model=CardPaymentResponse)
async def simulate_card_refund(
    card_id: uuid.UUID,
    payload: SimulateRefundRequest,
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)
    payment = await service.simulate_refund(payload.payment_id)
    await db.commit()
    return payment


@router.post("/fx/update-rate", response_model=FxRateResponse)
async def update_fx_rate(payload: UpdateFxRateRequest, db: AsyncSession = Depends(get_db)):
    service = FXService(db)
    fx_rate = await service.set_rate(payload.base_currency, payload.quote_currency, payload.rate)
    await db.commit()
    return fx_rate
