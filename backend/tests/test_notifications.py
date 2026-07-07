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


async def test_account_created_notification_exists_after_registration(client):
    headers = await _register_and_login(client, "+224677777701")
    response = await client.get("/api/v1/notifications", headers=headers)
    assert response.status_code == 200
    types = [n["type"] for n in response.json()]
    assert "account_created" in types


async def test_topup_success_creates_notification(client):
    headers = await _register_and_login(client, "+224677777702")
    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]

    topup_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "50000", "provider_name": "orange_money"},
    )
    topup_id = topup_resp.json()["id"]
    await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")

    response = await client.get("/api/v1/notifications", headers=headers)
    types = [n["type"] for n in response.json()]
    assert "topup_received" in types


async def test_unread_count_and_mark_read(client):
    headers = await _register_and_login(client, "+224677777703")
    unread_resp = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert unread_resp.json()["unread_count"] >= 1

    list_resp = await client.get("/api/v1/notifications", headers=headers)
    notification_id = list_resp.json()[0]["id"]

    mark_resp = await client.post(
        f"/api/v1/notifications/{notification_id}/read", headers=headers
    )
    assert mark_resp.status_code == 200
    assert mark_resp.json()["read_at"] is not None


async def test_cannot_mark_another_users_notification_read(client):
    headers_a = await _register_and_login(client, "+224677777704")
    headers_b = await _register_and_login(client, "+224677777705")

    list_resp = await client.get("/api/v1/notifications", headers=headers_a)
    notification_id = list_resp.json()[0]["id"]

    response = await client.post(
        f"/api/v1/notifications/{notification_id}/read", headers=headers_b
    )
    assert response.status_code == 403


async def test_notifications_require_auth(client):
    response = await client.get("/api/v1/notifications")
    assert response.status_code == 401
