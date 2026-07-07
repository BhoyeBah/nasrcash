from decimal import Decimal

from app.modules.ledger.service import LedgerService
from app.modules.wallets.service import wallet_account_id


async def _registered_user_headers(client, phone="+224633333301"):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"phone": phone, "country_code": "GN", "pin": "1234"},
    )
    otp_code = register_resp.json()["sandbox_otp_code"]
    verify_resp = await client.post(
        "/api/v1/auth/verify-otp", json={"phone": phone, "code": otp_code}
    )
    access_token = verify_resp.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


async def test_wallet_is_auto_created_on_registration(client):
    headers = await _registered_user_headers(client)
    response = await client.get("/api/v1/wallets", headers=headers)
    assert response.status_code == 200
    wallets = response.json()
    assert len(wallets) == 1
    assert wallets[0]["currency_code"] == "GNF"
    assert wallets[0]["country_code"] == "GN"
    assert wallets[0]["status"] == "active"


async def test_wallet_balance_starts_at_zero(client):
    headers = await _registered_user_headers(client, phone="+224633333302")
    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert balance_resp.status_code == 200
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("0")


async def test_wallet_balance_reflects_ledger_credit(client, db_session):
    headers = await _registered_user_headers(client, phone="+224633333303")
    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]

    ledger = LedgerService(db_session)
    await ledger.record_transaction(
        transaction_type="TOPUP_SUCCESS",
        reference="manual-credit-1",
        entries=[
            {
                "account_id": "provider:orange_money",
                "direction": "debit",
                "amount": Decimal("250000"),
                "currency": "GNF",
            },
            {
                "account_id": wallet_account_id(wallet_id),
                "direction": "credit",
                "amount": Decimal("250000"),
                "currency": "GNF",
            },
        ],
    )
    await db_session.commit()

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert balance_resp.json()["available_balance"] == "250000.00"

    tx_resp = await client.get(f"/api/v1/wallets/{wallet_id}/transactions", headers=headers)
    assert len(tx_resp.json()) == 1
    assert tx_resp.json()[0]["direction"] == "credit"


async def test_cannot_access_another_users_wallet(client):
    headers_a = await _registered_user_headers(client, phone="+224633333304")
    headers_b = await _registered_user_headers(client, phone="+224633333305")

    wallets_resp = await client.get("/api/v1/wallets", headers=headers_a)
    wallet_id = wallets_resp.json()[0]["id"]

    response = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers_b)
    assert response.status_code == 403
