from decimal import Decimal

from app.core.config import get_settings
from app.modules.fees.service import FeeService


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


async def test_default_topup_fee_matches_seeded_rate(db_session):
    service = FeeService(db_session)
    fee = await service.calculate_topup_fee(Decimal("500000"), country_code="GN")
    assert fee == Decimal("10000.00")  # 2% seeded default


async def test_provider_specific_fee_overrides_global_default(client, db_session):
    admin_headers = await _admin_headers(client)

    # Give orange_money a cheaper topup rate than the 2% global default.
    create_resp = await client.post(
        "/api/v1/admin/fees",
        headers=admin_headers,
        json={"fee_type": "topup", "provider_name": "orange_money", "rate": "0.01"},
    )
    assert create_resp.status_code == 200, create_resp.text

    headers = await _register_and_login(client, "+224633300001")
    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "500000", "provider_name": "orange_money"},
    )
    assert response.status_code == 200, response.text
    assert Decimal(response.json()["fee_amount"]) == Decimal("5000.00")  # 1% override

    # A different provider is unaffected by the override.
    response_other = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "500000", "provider_name": "mtn_momo"},
    )
    assert Decimal(response_other.json()["fee_amount"]) == Decimal("10000.00")


async def test_fixed_amount_fee_component_is_applied(db_session):
    service = FeeService(db_session)
    # Scope the new rule to a specific country so it strictly outranks the
    # global 1.5% default in specificity — the outcome is then unambiguous.
    await service.create_rule(
        fee_type="withdrawal", country_code="GN", provider_name=None, kyc_level=None,
        rate=Decimal("0.01"), fixed_amount=Decimal("500"),
    )
    fee = await service.calculate_withdrawal_fee(Decimal("200000"), country_code="GN")
    assert fee == Decimal("2500.00")  # 200000 * 0.01 + 500

    # A different country still falls back to the unscoped 1.5% global default.
    fee_other_country = await service.calculate_withdrawal_fee(
        Decimal("200000"), country_code="CI"
    )
    assert fee_other_country == Decimal("3000.00")  # 200000 * 0.015


async def test_admin_list_and_deactivate_fee_rule(client):
    admin_headers = await _admin_headers(client)

    list_resp = await client.get("/api/v1/admin/fees", headers=admin_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 3  # the seeded defaults

    create_resp = await client.post(
        "/api/v1/admin/fees",
        headers=admin_headers,
        json={"fee_type": "payment", "kyc_level": 2, "rate": "0.025"},
    )
    assert create_resp.status_code == 200
    rule_id = create_resp.json()["id"]

    deactivate_resp = await client.post(
        f"/api/v1/admin/fees/{rule_id}/deactivate", headers=admin_headers
    )
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.json()["is_active"] is False


async def test_create_fee_rule_requires_finance_role(client, db_session):
    from app.core.security import create_admin_access_token
    from app.modules.admin.models import AdminUser

    support_admin = AdminUser(
        email="support-fees@nasrcash.com", password_hash="x", role="support_agent"
    )
    db_session.add(support_admin)
    await db_session.commit()

    token = create_admin_access_token(support_admin.id)
    response = await client.post(
        "/api/v1/admin/fees",
        headers={"Authorization": f"Bearer {token.token}"},
        json={"fee_type": "topup", "rate": "0.05"},
    )
    assert response.status_code == 403


async def test_create_fee_rule_rejects_invalid_type(client):
    admin_headers = await _admin_headers(client)
    response = await client.post(
        "/api/v1/admin/fees",
        headers=admin_headers,
        json={"fee_type": "not_a_real_type", "rate": "0.02"},
    )
    assert response.status_code == 422
