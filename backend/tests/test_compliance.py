import uuid
from decimal import Decimal

from app.core.config import get_settings
from app.modules.auth.models import User
from app.modules.compliance.service import ComplianceService


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
    user_id = register_resp.json()["user_id"]
    otp_code = register_resp.json()["sandbox_otp_code"]
    verify_resp = await client.post(
        "/api/v1/auth/verify-otp", json={"phone": phone, "code": otp_code}
    )
    headers = {"Authorization": f"Bearer {verify_resp.json()['access_token']}"}
    return headers, user_id


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


async def _kyc2_user(client, phone):
    headers, user_id = await _register_and_login(client, phone)
    await _complete_kyc_level(client, headers, level=1)
    await _complete_kyc_level(client, headers, level=2)
    return headers, user_id


async def _wallet_id(client, headers):
    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    return wallets_resp.json()[0]["id"]


async def _topup_and_confirm(client, headers, wallet_id, amount):
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": amount, "provider_name": "orange_money"},
    )
    assert resp.status_code == 200, resp.text
    topup_id = resp.json()["id"]
    confirm = await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")
    assert confirm.status_code == 200
    return resp.json()


async def test_large_transaction_raises_alert(client):
    # KYC0's topup_max (2,000,000) is below the compliance large-transaction
    # threshold (3,000,000), so a KYC2 user (10,000,000 ceiling) is needed to
    # actually complete a topup large enough to trigger the alert.
    headers, user_id = await _kyc2_user(client, "+224644400001")
    wallet_id = await _wallet_id(client, headers)

    await _topup_and_confirm(client, headers, wallet_id, "3500000")

    admin_headers = await _admin_headers(client)
    list_resp = await client.get(
        "/api/v1/admin/compliance/alerts",
        headers=admin_headers,
        params={"user_id": user_id},
    )
    assert list_resp.status_code == 200
    alerts = list_resp.json()
    large_tx_alerts = [a for a in alerts if a["alert_type"] == "large_transaction"]
    assert len(large_tx_alerts) == 1
    assert large_tx_alerts[0]["status"] == "open"
    assert large_tx_alerts[0]["context"]["transaction_type"] == "topup"


async def test_velocity_alert_triggers_after_repeated_transactions(client):
    headers, user_id = await _register_and_login(client, "+224644400002")
    wallet_id = await _wallet_id(client, headers)

    # Default velocity threshold is 5 transactions within the rolling window.
    for _ in range(5):
        await _topup_and_confirm(client, headers, wallet_id, "10000")

    admin_headers = await _admin_headers(client)
    list_resp = await client.get(
        "/api/v1/admin/compliance/alerts",
        headers=admin_headers,
        params={"user_id": user_id},
    )
    velocity_alerts = [a for a in list_resp.json() if a["alert_type"] == "velocity"]
    assert len(velocity_alerts) >= 1


async def test_limit_breach_attempt_raises_alert(client):
    headers, user_id = await _register_and_login(client, "+224644400003")
    wallet_id = await _wallet_id(client, headers)

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "3000000", "provider_name": "orange_money"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "limit_exceeded"

    admin_headers = await _admin_headers(client)
    list_resp = await client.get(
        "/api/v1/admin/compliance/alerts",
        headers=admin_headers,
        params={"user_id": user_id},
    )
    breach_alerts = [
        a for a in list_resp.json() if a["alert_type"] == "limit_exceeded_attempt"
    ]
    assert len(breach_alerts) == 1
    assert breach_alerts[0]["context"]["limit_type"] == "topup"


async def test_admin_can_resolve_and_dismiss_alerts(client):
    headers, user_id = await _kyc2_user(client, "+224644400004")
    wallet_id = await _wallet_id(client, headers)
    await _topup_and_confirm(client, headers, wallet_id, "3500000")

    admin_headers = await _admin_headers(client)
    list_resp = await client.get(
        "/api/v1/admin/compliance/alerts",
        headers=admin_headers,
        params={"user_id": user_id},
    )
    alert_id = list_resp.json()[0]["id"]

    resolve_resp = await client.post(
        f"/api/v1/admin/compliance/alerts/{alert_id}/resolve",
        headers=admin_headers,
        json={"resolution_notes": "Vérifié avec le client, transaction légitime."},
    )
    assert resolve_resp.status_code == 200, resolve_resp.text
    assert resolve_resp.json()["status"] == "resolved"
    assert resolve_resp.json()["resolved_at"] is not None

    # Cannot resolve twice.
    second_resp = await client.post(
        f"/api/v1/admin/compliance/alerts/{alert_id}/resolve",
        headers=admin_headers,
        json={},
    )
    assert second_resp.status_code == 409


async def test_dismiss_alert(client):
    headers, user_id = await _kyc2_user(client, "+224644400005")
    wallet_id = await _wallet_id(client, headers)
    await _topup_and_confirm(client, headers, wallet_id, "3500000")

    admin_headers = await _admin_headers(client)
    list_resp = await client.get(
        "/api/v1/admin/compliance/alerts",
        headers=admin_headers,
        params={"user_id": user_id},
    )
    alert_id = list_resp.json()[0]["id"]

    dismiss_resp = await client.post(
        f"/api/v1/admin/compliance/alerts/{alert_id}/dismiss",
        headers=admin_headers,
        json={"resolution_notes": "Faux positif."},
    )
    assert dismiss_resp.status_code == 200
    assert dismiss_resp.json()["status"] == "dismissed"


async def test_compliance_view_requires_authorized_role(client, db_session):
    from app.core.security import create_admin_access_token
    from app.modules.admin.models import AdminUser

    support_admin = AdminUser(
        email="support-compliance@nasrcash.com", password_hash="x", role="support_agent"
    )
    db_session.add(support_admin)
    await db_session.commit()

    token = create_admin_access_token(support_admin.id)
    response = await client.get(
        "/api/v1/admin/compliance/alerts",
        headers={"Authorization": f"Bearer {token.token}"},
    )
    assert response.status_code == 403


async def test_compliance_resolve_requires_resolver_role(client, db_session):
    from app.core.security import create_admin_access_token
    from app.modules.admin.models import AdminUser

    risk_analyst = AdminUser(
        email="risk-analyst@nasrcash.com", password_hash="x", role="risk_analyst"
    )
    db_session.add(risk_analyst)
    await db_session.commit()

    token = create_admin_access_token(risk_analyst.id)
    # risk_analyst can view (COMPLIANCE_VIEW_ROLES) but not resolve (COMPLIANCE_RESOLVE_ROLES).
    view_resp = await client.get(
        "/api/v1/admin/compliance/alerts",
        headers={"Authorization": f"Bearer {token.token}"},
    )
    assert view_resp.status_code == 200

    resolve_resp = await client.post(
        "/api/v1/admin/compliance/alerts/00000000-0000-0000-0000-000000000000/resolve",
        headers={"Authorization": f"Bearer {token.token}"},
        json={},
    )
    assert resolve_resp.status_code == 403


async def test_auto_freeze_triggers_on_critical_alert(client, db_session):
    headers, user_id = await _register_and_login(client, "+224644400006")

    service = ComplianceService(db_session)
    # 35,000,000 is >= 10x the 3,000,000 large-transaction threshold, which
    # raises a single CRITICAL alert (weight 15) — enough on its own to cross
    # the default auto-freeze threshold (15).
    await service.check_large_transaction(uuid.UUID(user_id), Decimal("35000000"), "topup")
    await db_session.commit()

    user = await db_session.get(User, uuid.UUID(user_id))
    assert user.status == "suspended"

    # The user's existing access token is now rejected on every endpoint.
    blocked_resp = await client.get("/api/v1/wallets", headers=headers)
    assert blocked_resp.status_code == 401


async def test_risk_score_endpoint_and_manual_unfreeze(client, db_session):
    headers, user_id = await _register_and_login(client, "+224644400007")

    service = ComplianceService(db_session)
    await service.check_large_transaction(uuid.UUID(user_id), Decimal("35000000"), "topup")
    await db_session.commit()

    admin_headers = await _admin_headers(client)
    score_resp = await client.get(
        f"/api/v1/admin/compliance/users/{user_id}/risk-score", headers=admin_headers
    )
    assert score_resp.status_code == 200, score_resp.text
    assert score_resp.json()["score"] >= 15
    assert score_resp.json()["breakdown"]["critical"] == 1

    unfreeze_resp = await client.post(
        f"/api/v1/admin/compliance/users/{user_id}/unfreeze", headers=admin_headers
    )
    assert unfreeze_resp.status_code == 200, unfreeze_resp.text
    assert unfreeze_resp.json()["status"] == "active"

    # The account works again with its original token.
    ok_resp = await client.get("/api/v1/wallets", headers=headers)
    assert ok_resp.status_code == 200

    # Unfreezing an already-active account is a conflict.
    second_unfreeze = await client.post(
        f"/api/v1/admin/compliance/users/{user_id}/unfreeze", headers=admin_headers
    )
    assert second_unfreeze.status_code == 409


async def test_compliance_report_export_is_csv(client, db_session):
    headers, user_id = await _register_and_login(client, "+224644400008")

    service = ComplianceService(db_session)
    await service.record_limit_breach(uuid.UUID(user_id), "topup", {"amount": "1"})
    await db_session.commit()

    admin_headers = await _admin_headers(client)
    report_resp = await client.get("/api/v1/admin/compliance/report", headers=admin_headers)
    assert report_resp.status_code == 200
    assert report_resp.headers["content-type"].startswith("text/csv")
    assert "limit_exceeded_attempt" in report_resp.text


async def test_frozen_account_declines_card_payment(client, db_session):
    headers, user_id = await _kyc2_user(client, "+224644400009")
    wallet_id = await _wallet_id(client, headers)
    await _topup_and_confirm(client, headers, wallet_id, "5000000")

    card_resp = await client.post("/api/v1/cards", headers=headers)
    assert card_resp.status_code == 200, card_resp.text
    card_id = card_resp.json()["id"]

    fund_resp = await client.post(
        f"/api/v1/cards/{card_id}/fund",
        headers=headers,
        json={"amount": "100000", "idempotency_key": str(uuid.uuid4())},
    )
    assert fund_resp.status_code == 200, fund_resp.text

    service = ComplianceService(db_session)
    await service.check_large_transaction(uuid.UUID(user_id), Decimal("35000000"), "manual")
    await db_session.commit()

    payment_resp = await client.post(
        f"/api/v1/sandbox/cards/{card_id}/simulate-payment",
        json={
            "merchant_name": "Amazon",
            "merchant_amount": "10",
            "merchant_currency": "USD",
        },
    )
    assert payment_resp.status_code == 200, payment_resp.text
    assert payment_resp.json()["status"] == "declined"
    assert payment_resp.json()["decline_reason"] == "account_frozen"
