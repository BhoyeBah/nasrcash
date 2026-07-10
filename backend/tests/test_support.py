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


async def test_user_can_create_and_list_own_tickets(client):
    headers = await _register_and_login(client, "+224666600001")

    create_resp = await client.post(
        "/api/v1/support/tickets",
        headers=headers,
        json={"subject": "Recharge non reçue", "category": "topup", "message": "Ma recharge n'apparaît pas."},
    )
    assert create_resp.status_code == 200, create_resp.text
    ticket_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "open"

    list_resp = await client.get("/api/v1/support/tickets", headers=headers)
    assert list_resp.status_code == 200
    assert any(t["id"] == ticket_id for t in list_resp.json())

    detail_resp = await client.get(f"/api/v1/support/tickets/{ticket_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert len(detail_resp.json()["messages"]) == 1
    assert detail_resp.json()["messages"][0]["sender_type"] == "user"


async def test_ticket_create_rejects_invalid_category(client):
    headers = await _register_and_login(client, "+224666600002")
    response = await client.post(
        "/api/v1/support/tickets",
        headers=headers,
        json={"subject": "Test", "category": "not_a_category", "message": "..."},
    )
    assert response.status_code == 422


async def test_user_cannot_view_another_users_ticket(client):
    headers_a = await _register_and_login(client, "+224666600003")
    headers_b = await _register_and_login(client, "+224666600004")

    create_resp = await client.post(
        "/api/v1/support/tickets",
        headers=headers_a,
        json={"subject": "Privé", "category": "general", "message": "Confidentiel"},
    )
    ticket_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/support/tickets/{ticket_id}", headers=headers_b)
    assert response.status_code == 403


async def test_admin_reply_moves_ticket_to_in_progress_and_notifies_user(client):
    headers = await _register_and_login(client, "+224666600005")
    create_resp = await client.post(
        "/api/v1/support/tickets",
        headers=headers,
        json={"subject": "Carte bloquée", "category": "card", "message": "Ma carte ne marche plus."},
    )
    ticket_id = create_resp.json()["id"]

    admin_headers = await _admin_headers(client)
    list_resp = await client.get("/api/v1/admin/support/tickets", headers=admin_headers)
    assert list_resp.status_code == 200
    assert any(t["id"] == ticket_id for t in list_resp.json())

    reply_resp = await client.post(
        f"/api/v1/admin/support/tickets/{ticket_id}/messages",
        headers=admin_headers,
        json={"body": "Nous regardons votre demande."},
    )
    assert reply_resp.status_code == 200, reply_resp.text
    assert reply_resp.json()["sender_type"] == "admin"

    ticket_resp = await client.get(f"/api/v1/admin/support/tickets/{ticket_id}", headers=admin_headers)
    assert ticket_resp.json()["ticket"]["status"] == "in_progress"
    assert len(ticket_resp.json()["messages"]) == 2

    unread_resp = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert unread_resp.json()["unread_count"] >= 1


async def test_user_reply_reopens_in_progress_ticket(client):
    headers = await _register_and_login(client, "+224666600006")
    create_resp = await client.post(
        "/api/v1/support/tickets",
        headers=headers,
        json={"subject": "Question", "category": "general", "message": "Bonjour"},
    )
    ticket_id = create_resp.json()["id"]

    admin_headers = await _admin_headers(client)
    await client.post(
        f"/api/v1/admin/support/tickets/{ticket_id}/messages",
        headers=admin_headers,
        json={"body": "Pouvez-vous préciser ?"},
    )

    reply_resp = await client.post(
        f"/api/v1/support/tickets/{ticket_id}/messages",
        headers=headers,
        json={"body": "Voici plus de détails."},
    )
    assert reply_resp.status_code == 200

    detail_resp = await client.get(f"/api/v1/support/tickets/{ticket_id}", headers=headers)
    assert detail_resp.json()["ticket"]["status"] == "open"
    assert len(detail_resp.json()["messages"]) == 3


async def test_admin_can_resolve_and_close_ticket(client):
    headers = await _register_and_login(client, "+224666600007")
    create_resp = await client.post(
        "/api/v1/support/tickets",
        headers=headers,
        json={"subject": "Test", "category": "general", "message": "..."},
    )
    ticket_id = create_resp.json()["id"]

    admin_headers = await _admin_headers(client)
    resolve_resp = await client.post(
        f"/api/v1/admin/support/tickets/{ticket_id}/resolve", headers=admin_headers
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "resolved"

    close_resp = await client.post(
        f"/api/v1/admin/support/tickets/{ticket_id}/close", headers=admin_headers
    )
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "closed"

    # No more replies once closed.
    reply_resp = await client.post(
        f"/api/v1/support/tickets/{ticket_id}/messages",
        headers=headers,
        json={"body": "encore un message"},
    )
    assert reply_resp.status_code == 409


async def test_support_endpoints_require_authorized_role(client, db_session):
    auditor = AdminUser(email="auditor-support@nasrcash.com", password_hash="x", role="auditor")
    db_session.add(auditor)
    await db_session.commit()
    token = create_admin_access_token(auditor.id)

    response = await client.get(
        "/api/v1/admin/support/tickets", headers={"Authorization": f"Bearer {token.token}"}
    )
    assert response.status_code == 403
