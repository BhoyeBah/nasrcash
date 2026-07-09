from decimal import ROUND_HALF_UP, Decimal

from app.core.config import get_settings

settings = get_settings()


def calculate_topup_fee(amount: Decimal) -> Decimal:
    rate = Decimal(settings.topup_fee_percent)
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_payment_fee(amount: Decimal) -> Decimal:
    rate = Decimal(settings.payment_fee_percent)
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_withdrawal_fee(amount: Decimal) -> Decimal:
    rate = Decimal(settings.withdrawal_fee_percent)
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
