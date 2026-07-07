from app.modules.providers.payment_provider import MockPaymentProvider, PaymentProvider

# Guinea pilot mobile money providers. Adding a new one (or a new country's
# providers) is a data change here, never a change to TopupService.
PAYMENT_PROVIDERS: dict[str, PaymentProvider] = {
    "orange_money": MockPaymentProvider("orange_money"),
    "mtn_momo": MockPaymentProvider("mtn_momo"),
    "moov_money": MockPaymentProvider("moov_money"),
}


def get_payment_provider(name: str) -> PaymentProvider | None:
    return PAYMENT_PROVIDERS.get(name)
