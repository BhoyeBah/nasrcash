from decimal import Decimal


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


async def _kyc2_user_headers(client, phone):
    headers = await _register_and_login(client, phone)
    await _complete_kyc_level(client, headers, level=1)
    await _complete_kyc_level(client, headers, level=2)
    return headers


async def _fund_wallet(client, db_session, headers, wallet_amount=Decimal("1000000")):
    from app.modules.ledger.service import LedgerService
    from app.modules.wallets.service import wallet_account_id

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
                "amount": wallet_amount,
                "currency": "GNF",
            },
            {
                "account_id": wallet_account_id(wallet_id),
                "direction": "credit",
                "amount": wallet_amount,
                "currency": "GNF",
            },
        ],
    )
    await db_session.commit()
    return wallet_id


async def test_card_issuance_blocked_below_kyc2(client):
    headers = await _register_and_login(client, "+224655555501")
    response = await client.post("/api/v1/cards", headers=headers)
    assert response.status_code == 403


async def test_card_issuance_blocked_at_kyc1(client):
    headers = await _register_and_login(client, "+224655555502")
    await _complete_kyc_level(client, headers, level=1)
    response = await client.post("/api/v1/cards", headers=headers)
    assert response.status_code == 403


async def test_card_issuance_succeeds_at_kyc2(client):
    headers = await _kyc2_user_headers(client, "+224655555503")
    response = await client.post("/api/v1/cards", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "active"
    assert body["last4"] in body["masked_pan"]
    assert "4242" not in body["masked_pan"] or "*" in body["masked_pan"]


async def test_get_card_balance_starts_at_zero(client):
    headers = await _kyc2_user_headers(client, "+224655555512")
    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]

    response = await client.get(f"/api/v1/cards/{card_id}/balance", headers=headers)
    assert response.status_code == 200
    assert Decimal(response.json()["available_balance"]) == Decimal("0")


async def test_card_never_exposes_full_pan(client):
    headers = await _kyc2_user_headers(client, "+224655555504")
    response = await client.post("/api/v1/cards", headers=headers)
    body = response.json()
    assert "cvv" not in body
    assert body["masked_pan"].count("*") >= 4


async def test_fund_card_from_wallet(client, db_session):
    headers = await _kyc2_user_headers(client, "+224655555505")
    await _fund_wallet(client, db_session, headers)

    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]

    fund_resp = await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": "300000", "idempotency_key": "fund-1"},
    )
    assert fund_resp.status_code == 200, fund_resp.text
    assert Decimal(fund_resp.json()["available_balance"]) == Decimal("300000")

    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]
    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("700000")

    card_balance_resp = await client.get(f"/api/v1/cards/{card_id}/balance", headers=headers)
    assert card_balance_resp.status_code == 200
    assert Decimal(card_balance_resp.json()["available_balance"]) == Decimal("300000")


async def test_fund_card_insufficient_wallet_balance(client):
    headers = await _kyc2_user_headers(client, "+224655555506")
    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]

    response = await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": "300000", "idempotency_key": "fund-2"},
    )
    assert response.status_code == 402


async def test_fund_card_idempotent_retry_does_not_double_debit(client, db_session):
    headers = await _kyc2_user_headers(client, "+224655555507")
    await _fund_wallet(client, db_session, headers)
    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]

    for _ in range(2):
        fund_resp = await client.post(
            f"/api/v1/cards/{card_id}/fund",
            headers=headers,
            json={"amount": "200000", "idempotency_key": "same-key"},
        )
        assert fund_resp.status_code == 200

    assert Decimal(fund_resp.json()["available_balance"]) == Decimal("200000")


async def test_freeze_then_unfreeze_card(client):
    headers = await _kyc2_user_headers(client, "+224655555508")
    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]

    freeze_resp = await client.post(f"/api/v1/cards/{card_id}/freeze", headers=headers)
    assert freeze_resp.status_code == 200
    assert freeze_resp.json()["status"] == "frozen"

    fund_while_frozen = await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": "1000", "idempotency_key": "x"},
    )
    assert fund_while_frozen.status_code == 409

    unfreeze_resp = await client.post(f"/api/v1/cards/{card_id}/unfreeze", headers=headers)
    assert unfreeze_resp.status_code == 200
    assert unfreeze_resp.json()["status"] == "active"


async def test_close_card_is_terminal(client):
    headers = await _kyc2_user_headers(client, "+224655555509")
    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]

    close_resp = await client.post(f"/api/v1/cards/{card_id}/close", headers=headers)
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "closed"

    second_close = await client.post(f"/api/v1/cards/{card_id}/close", headers=headers)
    assert second_close.status_code == 409


async def test_cannot_access_another_users_card(client):
    headers_a = await _kyc2_user_headers(client, "+224655555510")
    headers_b = await _kyc2_user_headers(client, "+224655555511")

    card_resp = await client.post("/api/v1/cards", headers=headers_a)
    card_id = card_resp.json()["id"]

    response = await client.get(f"/api/v1/cards/{card_id}", headers=headers_b)
    assert response.status_code == 403
