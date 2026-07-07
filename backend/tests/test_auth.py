async def _register(client, phone="+224600000001", pin="1234"):
    response = await client.post(
        "/api/v1/auth/register",
        json={"phone": phone, "country_code": "GN", "pin": pin},
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_register_returns_sandbox_otp(client):
    body = await _register(client)
    assert body["phone"] == "+224600000001"
    assert body["sandbox_otp_code"] is not None
    assert len(body["sandbox_otp_code"]) == 6


async def test_register_rejects_duplicate_phone(client):
    await _register(client)
    response = await client.post(
        "/api/v1/auth/register",
        json={"phone": "+224600000001", "country_code": "GN", "pin": "1234"},
    )
    assert response.status_code == 409


async def test_register_rejects_unknown_country(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"phone": "+224600000002", "country_code": "SN", "pin": "1234"},
    )
    assert response.status_code == 422


async def test_verify_otp_then_login_flow(client):
    body = await _register(client)
    otp_code = body["sandbox_otp_code"]

    verify_resp = await client.post(
        "/api/v1/auth/verify-otp",
        json={"phone": "+224600000001", "code": otp_code},
    )
    assert verify_resp.status_code == 200, verify_resp.text
    tokens = verify_resp.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    login_resp = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000001", "pin": "1234"}
    )
    assert login_resp.status_code == 200
    assert login_resp.json()["access_token"]


async def test_verify_otp_wrong_code_rejected(client):
    await _register(client)
    response = await client.post(
        "/api/v1/auth/verify-otp",
        json={"phone": "+224600000001", "code": "000000"},
    )
    assert response.status_code == 422


async def test_login_wrong_pin_rejected(client):
    await _register(client)
    response = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000001", "pin": "9999"}
    )
    assert response.status_code == 401


async def test_login_locks_account_after_max_attempts(client):
    await _register(client, phone="+224600000003")
    for _ in range(5):
        response = await client.post(
            "/api/v1/auth/login", json={"phone": "+224600000003", "pin": "0000"}
        )
        assert response.status_code == 401

    # Even the correct PIN is now rejected because the account is locked.
    response = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000003", "pin": "1234"}
    )
    assert response.status_code == 403


async def test_refresh_rotates_token_and_old_one_is_revoked(client):
    body = await _register(client, phone="+224600000004")
    login_resp = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000004", "pin": "1234"}
    )
    old_refresh = login_resp.json()["refresh_token"]

    refresh_resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
    )
    assert refresh_resp.status_code == 200
    new_refresh = refresh_resp.json()["refresh_token"]
    assert new_refresh != old_refresh

    reuse_resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
    )
    assert reuse_resp.status_code == 401


async def test_logout_revokes_refresh_token(client):
    await _register(client, phone="+224600000005")
    login_resp = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000005", "pin": "1234"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )
    assert logout_resp.status_code == 200

    refresh_resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 401


async def test_change_pin_requires_current_pin(client):
    await _register(client, phone="+224600000006")
    login_resp = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000006", "pin": "1234"}
    )
    access_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    bad_resp = await client.post(
        "/api/v1/auth/change-pin",
        json={"current_pin": "0000", "new_pin": "5678"},
        headers=headers,
    )
    assert bad_resp.status_code == 401

    good_resp = await client.post(
        "/api/v1/auth/change-pin",
        json={"current_pin": "1234", "new_pin": "5678"},
        headers=headers,
    )
    assert good_resp.status_code == 200

    login_new_pin = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000006", "pin": "5678"}
    )
    assert login_new_pin.status_code == 200


async def test_forgot_pin_and_reset_pin_flow(client):
    await _register(client, phone="+224600000007")
    forgot_resp = await client.post(
        "/api/v1/auth/forgot-pin", json={"phone": "+224600000007"}
    )
    assert forgot_resp.status_code == 200
    otp_code = forgot_resp.json()["sandbox_otp_code"]
    assert otp_code is not None

    reset_resp = await client.post(
        "/api/v1/auth/reset-pin",
        json={"phone": "+224600000007", "code": otp_code, "new_pin": "4321"},
    )
    assert reset_resp.status_code == 200

    login_resp = await client.post(
        "/api/v1/auth/login", json={"phone": "+224600000007", "pin": "4321"}
    )
    assert login_resp.status_code == 200


async def test_forgot_pin_unknown_phone_does_not_leak(client):
    response = await client.post(
        "/api/v1/auth/forgot-pin", json={"phone": "+224699999999"}
    )
    assert response.status_code == 200
    assert response.json()["sandbox_otp_code"] is None


async def test_get_current_user_requires_bearer_token(client):
    response = await client.post(
        "/api/v1/auth/change-pin", json={"current_pin": "1234", "new_pin": "5678"}
    )
    assert response.status_code == 401
