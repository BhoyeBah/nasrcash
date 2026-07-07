import uuid
from decimal import Decimal

from app.modules.ledger.service import LedgerService
from app.modules.wallets.service import wallet_account_id


async def _register_and_login(client, phone):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"phone": phone, "country_code": "GN", "pin": "1234"},
    )
    otp_code = register_resp.json()["sandbox_otp_code"]
    verify_resp = await client.post(
        "/api/v1/auth/verify-otp", json={"phone": phone, "code": otp_code}
    )
    return {"Authorization": f"Bearer {verify_resp.json()['access_token']}"}


async def _complete_kyc_level(client, headers, level: int):
    await client.post("/api/v1/kyc/start", headers=headers)
    await client.post(
        "/api/v1/kyc/documents",
        headers=headers,
        data={"document_type": "national_id"},
        files={"file": ("id.jpg", b"fake-id", "image/jpeg")},
    )
    await client.post(
        "/api/v1/kyc/documents",
        headers=headers,
        data={"document_type": "selfie"},
        files={"file": ("selfie.jpg", b"fake-selfie", "image/jpeg")},
    )
    if level >= 2:
        await client.post(
            "/api/v1/kyc/documents",
            headers=headers,
            data={"document_type": "proof_of_address"},
            files={"file": ("address.jpg", b"fake-address", "image/jpeg")},
        )
    await client.post("/api/v1/kyc/submit", headers=headers)


async def _card_with_funds(client, db_session, phone, funded_amount=Decimal("300000")):
    headers = await _register_and_login(client, phone)
    await _complete_kyc_level(client, headers, level=1)
    await _complete_kyc_level(client, headers, level=2)

    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]

    ledger = LedgerService(db_session)
    await ledger.record_transaction(
        transaction_type="TOPUP_SUCCESS",
        reference=f"seed-{wallet_id}",
        entries=[
            {
                "account_id": "provider:orange_money",
                "direction": "debit",
                "amount": Decimal("1000000"),
                "currency": "GNF",
            },
            {
                "account_id": wallet_account_id(wallet_id),
                "direction": "credit",
                "amount": Decimal("1000000"),
                "currency": "GNF",
            },
        ],
    )
    await db_session.commit()

    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]

    await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": str(funded_amount), "idempotency_key": f"fund-{phone}"},
    )
    return headers, card_id


async def test_payment_settles_and_debits_card_with_frozen_rate(client, db_session):
    headers, card_id = await _card_with_funds(client, db_session, "+224666666601")

    response = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Netflix",
            "merchant_amount": "10",
            "merchant_currency": "USD",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "settled"
    assert Decimal(body["fx_rate"]) == Decimal("9000.000000")
    assert Decimal(body["local_amount"]) == Decimal("90000.00")
    assert Decimal(body["fees_amount"]) == Decimal("2700.00")
    assert Decimal(body["total_debited"]) == Decimal("92700.00")

    balance_resp = await client.get(f"/api/v1/cards/{card_id}", headers=headers)
    assert balance_resp.status_code == 200

    balance_check = await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": "1", "idempotency_key": "noop-check"},
    )
    # 300000 funded - 92700 debited = 207300 remaining, then +1 = 207301
    assert Decimal(balance_check.json()["available_balance"]) == Decimal("207301.00")


async def test_payment_declines_on_insufficient_balance(client, db_session):
    headers, card_id = await _card_with_funds(
        client, db_session, "+224666666602", funded_amount=Decimal("1000")
    )

    response = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Google Ads",
            "merchant_amount": "25",
            "merchant_currency": "USD",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "declined"
    assert body["decline_reason"] == "insufficient_balance"


async def test_payment_declines_when_card_frozen(client, db_session):
    headers, card_id = await _card_with_funds(client, db_session, "+224666666603")
    await client.post(f"/api/v1/cards/{card_id}/freeze", headers=headers)

    response = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Amazon",
            "merchant_amount": "5",
            "merchant_currency": "USD",
        },
    )
    body = response.json()
    assert body["status"] == "declined"
    assert body["decline_reason"] == "card_frozen"


async def test_replaying_same_provider_reference_is_idempotent(client, db_session):
    headers, card_id = await _card_with_funds(client, db_session, "+224666666604")
    ref = str(uuid.uuid4())

    first = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Spotify",
            "merchant_amount": "5",
            "merchant_currency": "USD",
            "provider_reference": ref,
        },
    )
    second = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Spotify",
            "merchant_amount": "5",
            "merchant_currency": "USD",
            "provider_reference": ref,
        },
    )
    assert first.json()["id"] == second.json()["id"]

    payments_resp = await client.get(f"/api/v1/cards/{card_id}/payments", headers=headers)
    assert len(payments_resp.json()) == 1


async def test_refund_reverses_settled_payment(client, db_session):
    headers, card_id = await _card_with_funds(client, db_session, "+224666666605")

    pay_resp = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Netflix",
            "merchant_amount": "10",
            "merchant_currency": "USD",
        },
    )
    payment_id = pay_resp.json()["id"]

    refund_resp = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-refund",
        json={"payment_id": payment_id},
    )
    assert refund_resp.status_code == 200
    assert refund_resp.json()["status"] == "refunded"

    balance_check = await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": "0.01", "idempotency_key": "post-refund-check"},
    )
    # 300000 funded - 92700 debited + 90000 refunded (fee kept) + 0.01 = 297300.01
    assert Decimal(balance_check.json()["available_balance"]) == Decimal("297300.01")


async def test_cannot_refund_a_declined_payment(client, db_session):
    headers, card_id = await _card_with_funds(
        client, db_session, "+224666666606", funded_amount=Decimal("1000")
    )
    pay_resp = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Google Ads",
            "merchant_amount": "25",
            "merchant_currency": "USD",
        },
    )
    payment_id = pay_resp.json()["id"]

    refund_resp = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-refund",
        json={"payment_id": payment_id},
    )
    assert refund_resp.status_code == 409


async def test_simulate_decline_forces_decline_reason(client, db_session):
    headers, card_id = await _card_with_funds(client, db_session, "+224666666607")

    response = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-decline",
        json={
            "merchant_name": "Suspicious Merchant",
            "merchant_amount": "5",
            "merchant_currency": "USD",
            "reason": "risk_rejected",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "declined"
    assert response.json()["decline_reason"] == "risk_rejected"


async def test_payment_without_fx_rate_configured_fails(client, db_session):
    headers, card_id = await _card_with_funds(client, db_session, "+224666666608")

    response = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Some Merchant",
            "merchant_amount": "5",
            "merchant_currency": "JPY",
        },
    )
    assert response.status_code == 404
