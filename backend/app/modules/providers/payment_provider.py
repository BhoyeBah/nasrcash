import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderTopupResult:
    provider_reference: str
    status: str  # "pending" | "successful" | "failed"


class PaymentProvider(Protocol):
    """Mobile Money / cash-in provider abstraction.

    Business logic (``TopupService``) only ever talks to this interface —
    never to a specific provider SDK. Swapping Orange Money's sandbox
    adapter for its production one is a wiring change, not a rewrite.
    """

    async def initiate_topup(
        self, amount, currency: str, phone: str, reference: str
    ) -> ProviderTopupResult: ...

    async def check_status(self, provider_reference: str) -> str: ...

    async def handle_webhook(self, payload: dict) -> dict: ...


class MockPaymentProvider:
    """Sandbox stand-in for Orange Money / MTN MoMo / Moov Money.

    Nothing is actually sent anywhere — it immediately hands back a
    ``pending`` reference. The real state transition happens through the
    ``/api/v1/sandbox/topups/*`` endpoints, standing in for the provider's
    webhook until a real partner integration exists.
    """

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    async def initiate_topup(
        self, amount, currency: str, phone: str, reference: str
    ) -> ProviderTopupResult:
        return ProviderTopupResult(
            provider_reference=f"{self.provider_name}:{uuid.uuid4()}", status="pending"
        )

    async def check_status(self, provider_reference: str) -> str:
        return "pending"

    async def handle_webhook(self, payload: dict) -> dict:
        return payload
