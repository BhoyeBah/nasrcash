from decimal import Decimal


async def _registered_user(client, phone="+224644444401"):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"phone": phone, "country_code": "GN", "pin": "1234"},
    )
    otp_code = register_resp.json()["sandbox_otp_code"]
    verify_resp = await client.post(
        "/api/v1/auth/verify-otp", json={"phone": phone, "code": otp_code}
    )
    access_token = verify_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    wallets_resp = await client.get("/api/v1/wallets", headers=headers)
    wallet_id = wallets_resp.json()[0]["id"]
    return headers, wallet_id


async def test_initiate_topup_computes_fee(client):
    headers, wallet_id = await _registered_user(client)
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "500000", "provider_name": "orange_money"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "pending"
    assert Decimal(body["fee_amount"]) == Decimal("10000.00")
    assert Decimal(body["net_amount"]) == Decimal("490000.00")


async def test_initiate_topup_rejects_unknown_provider(client):
    headers, wallet_id = await _registered_user(client, phone="+224644444402")
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "500000", "provider_name": "unknown_provider"},
    )
    assert response.status_code == 422


async def test_initiate_topup_rejects_non_positive_amount(client):
    headers, wallet_id = await _registered_user(client, phone="+224644444403")
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "0", "provider_name": "orange_money"},
    )
    assert response.status_code == 422


async def test_simulate_success_credits_wallet(client):
    headers, wallet_id = await _registered_user(client, phone="+224644444404")
    topup_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "500000", "provider_name": "orange_money"},
    )
    topup_id = topup_resp.json()["id"]

    sim_resp = await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")
    assert sim_resp.status_code == 200, sim_resp.text
    assert sim_resp.json()["status"] == "successful"

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("490000.00")


async def test_simulate_success_twice_is_rejected_and_does_not_double_credit(client):
    headers, wallet_id = await _registered_user(client, phone="+224644444405")
    topup_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "100000", "provider_name": "mtn_momo"},
    )
    topup_id = topup_resp.json()["id"]

    first = await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")
    assert first.status_code == 200
    second = await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")
    assert second.status_code == 409

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("98000.00")


async def test_simulate_failure_marks_topup_failed_and_no_credit(client):
    headers, wallet_id = await _registered_user(client, phone="+224644444406")
    topup_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "50000", "provider_name": "moov_money"},
    )
    topup_id = topup_resp.json()["id"]

    fail_resp = await client.post(
        f"/api/v1/sandbox/topups/{topup_id}/simulate-failure",
        json={"reason": "insufficient_funds"},
    )
    assert fail_resp.status_code == 200
    assert fail_resp.json()["status"] == "failed"

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("0")


async def test_cannot_topup_someone_elses_wallet(client):
    headers_a, wallet_id_a = await _registered_user(client, phone="+224644444407")
    headers_b, _ = await _registered_user(client, phone="+224644444408")

    response = await client.post(
        f"/api/v1/wallets/{wallet_id_a}/topup",
        headers=headers_b,
        json={"amount": "10000", "provider_name": "orange_money"},
    )
    assert response.status_code == 403


async def test_list_and_get_topup(client):
    headers, wallet_id = await _registered_user(client, phone="+224644444409")
    await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": "20000", "provider_name": "orange_money"},
    )
    list_resp = await client.get("/api/v1/topups", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    topup_id = list_resp.json()[0]["id"]
    get_resp = await client.get(f"/api/v1/topups/{topup_id}", headers=headers)
    assert get_resp.status_code == 200
