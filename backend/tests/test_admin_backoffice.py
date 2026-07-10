from app.core.config import get_settings
from app.core.security import create_admin_access_token
from app.modules.admin.models import AdminUser


async def _admin_headers(client):
    settings = get_settings()
    response = await client.post(
        "/api/v1/admin/auth/login",
        json={"email": settings.admin_bootstrap_email, "password": settings.admin_bootstrap_password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _admin_headers_for_role(db_session, role: str, email: str) -> dict:
    admin = AdminUser(email=email, password_hash="x", role=role)
    db_session.add(admin)
    await db_session.commit()
    token = create_admin_access_token(admin.id)
    return {"Authorization": f"Bearer {token.token}"}


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


async def _kyc2_user_with_card(client, phone):
    headers = await _register_and_login(client, phone)
    await _complete_kyc_level(client, headers, level=1)
    await _complete_kyc_level(client, headers, level=2)
    card_resp = await client.post("/api/v1/cards", headers=headers)
    assert card_resp.status_code == 200, card_resp.text
    return headers, card_resp.json()["id"]


# --- cards ---


async def test_admin_can_block_and_unblock_a_card(client):
    _, card_id = await _kyc2_user_with_card(client, "+224655500001")
    admin_headers = await _admin_headers(client)

    list_resp = await client.get("/api/v1/admin/cards", headers=admin_headers)
    assert list_resp.status_code == 200
    assert any(c["id"] == card_id for c in list_resp.json())

    block_resp = await client.post(f"/api/v1/admin/cards/{card_id}/block", headers=admin_headers)
    assert block_resp.status_code == 200, block_resp.text
    assert block_resp.json()["status"] == "blocked"

    # Blocking an already-blocked card is a conflict.
    second_block = await client.post(f"/api/v1/admin/cards/{card_id}/block", headers=admin_headers)
    assert second_block.status_code == 409

    unblock_resp = await client.post(f"/api/v1/admin/cards/{card_id}/unblock", headers=admin_headers)
    assert unblock_resp.status_code == 200
    assert unblock_resp.json()["status"] == "active"


async def test_block_card_requires_cards_write_role(client, db_session):
    _, card_id = await _kyc2_user_with_card(client, "+224655500002")
    headers = await _admin_headers_for_role(db_session, "auditor", "auditor-cards@nasrcash.com")

    response = await client.post(f"/api/v1/admin/cards/{card_id}/block", headers=headers)
    assert response.status_code == 403


# --- FX rates ---


async def test_admin_can_list_and_create_fx_rates(client):
    admin_headers = await _admin_headers(client)

    list_resp = await client.get("/api/v1/admin/fx-rates", headers=admin_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 2  # seeded USD/GNF, EUR/GNF

    create_resp = await client.post(
        "/api/v1/admin/fx-rates",
        headers=admin_headers,
        json={"base_currency": "GBP", "quote_currency": "GNF", "rate": "11500"},
    )
    assert create_resp.status_code == 200, create_resp.text
    assert create_resp.json()["base_currency"] == "GBP"

    updated_list = await client.get("/api/v1/admin/fx-rates", headers=admin_headers)
    assert any(r["base_currency"] == "GBP" for r in updated_list.json())


async def test_create_fx_rate_requires_finance_role(client, db_session):
    headers = await _admin_headers_for_role(db_session, "support_agent", "support-fx@nasrcash.com")
    response = await client.post(
        "/api/v1/admin/fx-rates",
        headers=headers,
        json={"base_currency": "GBP", "quote_currency": "GNF", "rate": "11500"},
    )
    assert response.status_code == 403


# --- audit logs ---


async def test_admin_can_list_audit_logs(client):
    await _register_and_login(client, "+224655500003")

    admin_headers = await _admin_headers(client)
    response = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

    filtered = await client.get(
        "/api/v1/admin/audit-logs", headers=admin_headers, params={"actor_type": "user"}
    )
    assert filtered.status_code == 200
    assert all(entry["actor_type"] == "user" for entry in filtered.json())


async def test_audit_logs_require_authorized_role(client, db_session):
    headers = await _admin_headers_for_role(
        db_session, "operations_agent", "ops-audit@nasrcash.com"
    )
    response = await client.get("/api/v1/admin/audit-logs", headers=headers)
    assert response.status_code == 403


# --- accounting export ---


async def test_accounting_export_is_csv(client):
    headers = await _register_and_login(client, "+224655500004")
    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]
    topup_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "10000", "provider_name": "orange_money"},
    )
    await client.post(f"/api/v1/sandbox/topups/{topup_resp.json()['id']}/simulate-success")

    admin_headers = await _admin_headers(client)
    response = await client.get("/api/v1/admin/accounting/export", headers=admin_headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "ledger_transaction_id" in response.text


async def test_accounting_export_requires_authorized_role(client, db_session):
    headers = await _admin_headers_for_role(
        db_session, "support_agent", "support-accounting@nasrcash.com"
    )
    response = await client.get("/api/v1/admin/accounting/export", headers=headers)
    assert response.status_code == 403


# --- admin account management ---


async def test_super_admin_can_manage_admin_accounts(client):
    admin_headers = await _admin_headers(client)

    create_resp = await client.post(
        "/api/v1/admin/accounts",
        headers=admin_headers,
        json={
            "email": "new-ops@nasrcash.com",
            "password": "SuperSecret123!",
            "role": "operations_agent",
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    account_id = create_resp.json()["id"]
    assert create_resp.json()["role"] == "operations_agent"

    list_resp = await client.get("/api/v1/admin/accounts", headers=admin_headers)
    assert any(a["id"] == account_id for a in list_resp.json())

    role_resp = await client.post(
        f"/api/v1/admin/accounts/{account_id}/role",
        headers=admin_headers,
        json={"role": "compliance_officer"},
    )
    assert role_resp.status_code == 200
    assert role_resp.json()["role"] == "compliance_officer"

    deactivate_resp = await client.post(
        f"/api/v1/admin/accounts/{account_id}/active",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.json()["is_active"] is False


async def test_create_admin_account_rejects_duplicate_email(client):
    admin_headers = await _admin_headers(client)
    settings = get_settings()

    response = await client.post(
        "/api/v1/admin/accounts",
        headers=admin_headers,
        json={
            "email": settings.admin_bootstrap_email,
            "password": "SuperSecret123!",
            "role": "operations_agent",
        },
    )
    assert response.status_code == 409


async def test_admin_account_management_requires_super_admin(client, db_session):
    headers = await _admin_headers_for_role(
        db_session, "compliance_officer", "compliance-mgmt@nasrcash.com"
    )
    response = await client.get("/api/v1/admin/accounts", headers=headers)
    assert response.status_code == 403
