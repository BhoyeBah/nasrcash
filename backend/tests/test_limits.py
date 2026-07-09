from app.core.config import get_settings


async def _admin_headers(client):
    settings = get_settings()
    response = await client.post(
        "/api/v1/admin/auth/login",
        json={
            "email": settings.admin_bootstrap_email,
            "password": settings.admin_bootstrap_password,
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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


async def _wallet_id(client, headers):
    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    return wallets_resp.json()[0]["id"]


async def test_topup_below_minimum_is_rejected(client):
    headers = await _register_and_login(client, "+224622200001")
    wallet_id = await _wallet_id(client, headers)

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "500", "provider_name": "orange_money"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"


async def test_topup_above_default_maximum_is_rejected(client):
    headers = await _register_and_login(client, "+224622200002")
    wallet_id = await _wallet_id(client, headers)

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "3000000", "provider_name": "orange_money"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "limit_exceeded"


async def test_kyc2_user_gets_higher_topup_ceiling(client):
    headers = await _kyc2_user_headers(client, "+224622200003")
    wallet_id = await _wallet_id(client, headers)

    # Above the KYC0 default (2,000,000) but within the KYC2 override (10,000,000).
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "3000000", "provider_name": "orange_money"},
    )
    assert response.status_code == 200, response.text


async def test_wallet_daily_topup_cap_blocks_cumulative_excess(client):
    headers = await _register_and_login(client, "+224622200004")
    wallet_id = await _wallet_id(client, headers)

    async def _topup_and_confirm(amount):
        resp = await client.post(
            f"/api/v1/wallets/{wallet_id}/topup",
            headers=headers,
            json={"amount": amount, "provider_name": "orange_money"},
        )
        assert resp.status_code == 200, resp.text
        topup_id = resp.json()["id"]
        confirm = await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")
        assert confirm.status_code == 200

    await _topup_and_confirm("1500000")
    await _topup_and_confirm("1400000")  # cumulative 2,900,000 — still under 3,000,000 cap

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "200000", "provider_name": "orange_money"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "limit_exceeded"


async def test_withdrawal_daily_cap_blocks_cumulative_excess(client):
    headers = await _register_and_login(client, "+224622200005")
    wallet_id = await _wallet_id(client, headers)

    # Fund the wallet well above the withdrawal cap (via two topups, each
    # under the per-transaction topup max) so the withdrawal is blocked by
    # the withdrawal cap itself, not by insufficient balance.
    for amount in ("2000000", "900000"):
        topup_resp = await client.post(
            f"/api/v1/wallets/{wallet_id}/topup",
            headers=headers,
            json={"amount": amount, "provider_name": "orange_money"},
        )
        topup_id = topup_resp.json()["id"]
        confirm = await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")
        assert confirm.status_code == 200

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "2100000", "provider_name": "orange_money"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "limit_exceeded"


async def test_max_cards_per_user_is_enforced(client):
    headers = await _kyc2_user_headers(client, "+224622200006")

    for _ in range(3):
        resp = await client.post("/api/v1/cards", headers=headers)
        assert resp.status_code == 200, resp.text

    response = await client.post("/api/v1/cards", headers=headers)
    assert response.status_code == 422
    assert response.json()["error_code"] == "limit_exceeded"


async def test_card_payment_daily_cap_declines_over_limit(client):
    headers = await _kyc2_user_headers(client, "+224622200007")
    wallet_id = await _wallet_id(client, headers)

    topup_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "6000000", "provider_name": "orange_money"},
    )
    topup_id = topup_resp.json()["id"]
    await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")

    card_resp = await client.post("/api/v1/cards", headers=headers)
    card_id = card_resp.json()["id"]
    await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": "5880000", "idempotency_key": "fund-limits-test"},
    )

    # 600 USD @ 9000 GNF/USD = 5,400,000 local + 3% fee = 5,562,000 total,
    # above the KYC2 card_payment_daily_cap default of 5,000,000.
    response = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Big Purchase Inc",
            "merchant_amount": "600",
            "merchant_currency": "USD",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "declined"
    assert body["decline_reason"] == "limit_exceeded"


async def test_admin_can_list_and_create_and_deactivate_limit_rules(client):
    admin_headers = await _admin_headers(client)

    list_resp = await client.get("/api/v1/admin/limits", headers=admin_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 9  # the seeded defaults

    create_resp = await client.post(
        "/api/v1/admin/limits",
        headers=admin_headers,
        json={"limit_type": "topup_min", "country_code": "GN", "max_amount": "2000"},
    )
    assert create_resp.status_code == 200, create_resp.text
    rule_id = create_resp.json()["id"]

    deactivate_resp = await client.post(
        f"/api/v1/admin/limits/{rule_id}/deactivate", headers=admin_headers
    )
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.json()["is_active"] is False


async def test_admin_create_limit_rule_requires_finance_role(client, db_session):
    from app.core.security import create_admin_access_token
    from app.modules.admin.models import AdminUser

    support_admin = AdminUser(
        email="support-limits@nasrcash.com", password_hash="x", role="support_agent"
    )
    db_session.add(support_admin)
    await db_session.commit()

    token = create_admin_access_token(support_admin.id)
    response = await client.post(
        "/api/v1/admin/limits",
        headers={"Authorization": f"Bearer {token.token}"},
        json={"limit_type": "topup_min", "max_amount": "500"},
    )
    assert response.status_code == 403
