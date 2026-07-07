import random
import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderCardResult:
    provider_card_id: str
    masked_pan: str
    last4: str
    brand: str
    expiry_month: int
    expiry_year: int


class CardProvider(Protocol):
    """Card-issuing abstraction. The interface itself never exposes a full
    PAN or CVV to NasrCash's backend — only a masked representation and an
    opaque provider token, exactly as a real issuer's card-creation webhook
    would. Full card data is handled by the provider's own SDK/iframe."""

    async def create_card(self, user_id: uuid.UUID, currency: str) -> ProviderCardResult: ...

    async def freeze_card(self, provider_card_id: str) -> None: ...

    async def unfreeze_card(self, provider_card_id: str) -> None: ...

    async def close_card(self, provider_card_id: str) -> None: ...


class MockCardProvider:
    """Sandbox stand-in for a real card-issuing partner (Visa/Mastercard
    program manager). Generates a plausible-looking masked card — never a
    real, chargeable card — and never returns a usable PAN or CVV."""

    def __init__(self, provider_name: str = "mock_card_provider"):
        self.provider_name = provider_name

    async def create_card(self, user_id: uuid.UUID, currency: str) -> ProviderCardResult:
        last4 = f"{random.randint(0, 9999):04d}"
        return ProviderCardResult(
            provider_card_id=f"{self.provider_name}:{uuid.uuid4()}",
            masked_pan=f"4242 **** **** {last4}",
            last4=last4,
            brand="visa",
            expiry_month=random.randint(1, 12),
            expiry_year=2029,
        )

    async def freeze_card(self, provider_card_id: str) -> None:
        return None

    async def unfreeze_card(self, provider_card_id: str) -> None:
        return None

    async def close_card(self, provider_card_id: str) -> None:
        return None
