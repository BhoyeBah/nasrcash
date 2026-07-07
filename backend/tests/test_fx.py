from decimal import Decimal

from app.modules.fx.service import FXService


async def test_get_current_rate_returns_seeded_rate(db_session):
    service = FXService(db_session)
    rate = await service.get_current_rate("USD", "GNF")
    assert rate.rate == Decimal("9000.000000")


async def test_set_rate_creates_new_history_row_and_becomes_current(db_session):
    service = FXService(db_session)
    await service.set_rate("USD", "GNF", Decimal("9200"))
    rate = await service.get_current_rate("USD", "GNF")
    assert rate.rate == Decimal("9200.000000")


async def test_convert_uses_current_rate(db_session):
    service = FXService(db_session)
    converted, fx_rate = await service.convert(Decimal("10"), "USD", "GNF")
    assert converted == Decimal("90000.00")
    assert fx_rate.rate == Decimal("9000.000000")


async def test_update_fx_rate_endpoint(client):
    response = await client.post(
        "/api/v1/sandbox/fx/update-rate",
        json={"base_currency": "USD", "quote_currency": "GNF", "rate": "9500"},
    )
    assert response.status_code == 200
    assert Decimal(response.json()["rate"]) == Decimal("9500.000000")
