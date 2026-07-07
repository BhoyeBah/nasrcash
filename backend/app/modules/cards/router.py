import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.cards.schemas import CardBalanceResponse, CardFundRequest, CardResponse
from app.modules.cards.service import CardService
from app.modules.payments.schemas import CardPaymentResponse
from app.modules.payments.service import PaymentService
from app.modules.wallets.schemas import LedgerEntryResponse

router = APIRouter(prefix="/api/v1/cards", tags=["cards"])


@router.post("", response_model=CardResponse)
async def issue_card(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = CardService(db)
    card = await service.issue_card(current_user)
    await db.commit()
    return card


@router.get("", response_model=list[CardResponse])
async def list_cards(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = CardService(db)
    return await service.list_for_user(current_user.id)


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    return await service.get_card(card_id, current_user.id)


@router.post("/{card_id}/fund", response_model=CardBalanceResponse)
async def fund_card(
    card_id: uuid.UUID,
    payload: CardFundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    card = await service.get_card(card_id, current_user.id)
    await service.fund(card, current_user, payload.amount, payload.idempotency_key)
    balance = await service.get_balance(card)
    await db.commit()
    return CardBalanceResponse(
        card_id=card.id, currency_code=card.displayed_currency, available_balance=balance
    )


@router.post("/{card_id}/freeze", response_model=CardResponse)
async def freeze_card(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    card = await service.get_card(card_id, current_user.id)
    await service.freeze(card)
    await db.commit()
    return card


@router.post("/{card_id}/unfreeze", response_model=CardResponse)
async def unfreeze_card(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    card = await service.get_card(card_id, current_user.id)
    await service.unfreeze(card)
    await db.commit()
    return card


@router.post("/{card_id}/close", response_model=CardResponse)
async def close_card(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    card = await service.get_card(card_id, current_user.id)
    await service.close(card)
    await db.commit()
    return card


@router.get("/{card_id}/transactions", response_model=list[LedgerEntryResponse])
async def get_card_transactions(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CardService(db)
    card = await service.get_card(card_id, current_user.id)
    return await service.get_transactions(card)


@router.get("/{card_id}/payments", response_model=list[CardPaymentResponse])
async def get_card_payments(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    card_service = CardService(db)
    card = await card_service.get_card(card_id, current_user.id)
    payment_service = PaymentService(db)
    return await payment_service.list_for_card(card.id)
