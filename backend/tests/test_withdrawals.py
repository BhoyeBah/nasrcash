from decimal import Decimal


async def _registered_user(client, phone="+224611111401"):
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


async def _fund_wallet(client, headers, wallet_id, amount="1000000"):
    topup_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/topup",
        headers=headers,
        json={"amount": amount, "provider_name": "orange_money"},
    )
    topup_id = topup_resp.json()["id"]
    await client.post(f"/api/v1/sandbox/topups/{topup_id}/simulate-success")


async def test_initiate_withdrawal_computes_fee(client):
    headers, wallet_id = await _registered_user(client)
    await _fund_wallet(client, headers, wallet_id)

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "200000", "provider_name": "orange_money"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "pending"
    assert Decimal(body["fee_amount"]) == Decimal("3000.00")
    assert Decimal(body["net_amount"]) == Decimal("197000.00")


async def test_initiate_withdrawal_rejects_unknown_provider(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111402")
    await _fund_wallet(client, headers, wallet_id)

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "200000", "provider_name": "unknown_provider"},
    )
    assert response.status_code == 422


async def test_initiate_withdrawal_rejects_non_positive_amount(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111403")
    await _fund_wallet(client, headers, wallet_id)

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "0", "provider_name": "orange_money"},
    )
    assert response.status_code == 422


async def test_initiate_withdrawal_rejects_insufficient_balance(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111404")
    # No funding — wallet balance is 0.
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "50000", "provider_name": "orange_money"},
    )
    assert response.status_code == 402


async def test_simulate_success_debits_wallet(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111405")
    await _fund_wallet(client, headers, wallet_id)

    withdrawal_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "300000", "provider_name": "orange_money"},
    )
    withdrawal_id = withdrawal_resp.json()["id"]

    sim_resp = await client.post(f"/api/v1/sandbox/withdrawals/{withdrawal_id}/simulate-success")
    assert sim_resp.status_code == 200, sim_resp.text
    assert sim_resp.json()["status"] == "successful"

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    # funded 1000000 (net after 2% topup fee = 980000) - 300000 withdrawn
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("680000.00")


async def test_simulate_success_twice_is_rejected_and_does_not_double_debit(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111406")
    await _fund_wallet(client, headers, wallet_id)

    withdrawal_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "100000", "provider_name": "mtn_momo"},
    )
    withdrawal_id = withdrawal_resp.json()["id"]

    first = await client.post(f"/api/v1/sandbox/withdrawals/{withdrawal_id}/simulate-success")
    assert first.status_code == 200
    second = await client.post(f"/api/v1/sandbox/withdrawals/{withdrawal_id}/simulate-success")
    assert second.status_code == 409

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("880000.00")


async def test_simulate_failure_marks_withdrawal_failed_and_no_debit(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111407")
    await _fund_wallet(client, headers, wallet_id)

    withdrawal_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "50000", "provider_name": "moov_money"},
    )
    withdrawal_id = withdrawal_resp.json()["id"]

    fail_resp = await client.post(
        f"/api/v1/sandbox/withdrawals/{withdrawal_id}/simulate-failure",
        json={"reason": "provider_timeout"},
    )
    assert fail_resp.status_code == 200
    assert fail_resp.json()["status"] == "failed"

    balance_resp = await client.get(f"/api/v1/wallets/{wallet_id}/balance", headers=headers)
    assert Decimal(balance_resp.json()["available_balance"]) == Decimal("980000.00")


async def test_cannot_withdraw_from_someone_elses_wallet(client):
    headers_a, wallet_id_a = await _registered_user(client, phone="+224611111408")
    headers_b, _ = await _registered_user(client, phone="+224611111409")
    await _fund_wallet(client, headers_a, wallet_id_a)

    response = await client.post(
        f"/api/v1/wallets/{wallet_id_a}/withdrawals",
        headers=headers_b,
        json={"amount": "10000", "provider_name": "orange_money"},
    )
    assert response.status_code == 403


async def test_list_and_get_withdrawal(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111410")
    await _fund_wallet(client, headers, wallet_id)

    await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "20000", "provider_name": "orange_money"},
    )
    list_resp = await client.get("/api/v1/withdrawals", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    withdrawal_id = list_resp.json()[0]["id"]
    get_resp = await client.get(f"/api/v1/withdrawals/{withdrawal_id}", headers=headers)
    assert get_resp.status_code == 200


async def test_withdrawal_success_creates_notification(client):
    headers, wallet_id = await _registered_user(client, phone="+224611111411")
    await _fund_wallet(client, headers, wallet_id)

    withdrawal_resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/withdrawals",
        headers=headers,
        json={"amount": "50000", "provider_name": "orange_money"},
    )
    withdrawal_id = withdrawal_resp.json()["id"]
    await client.post(f"/api/v1/sandbox/withdrawals/{withdrawal_id}/simulate-success")

    notif_resp = await client.get("/api/v1/notifications", headers=headers)
    types = [n["type"] for n in notif_resp.json()]
    assert "withdrawal_successful" in types
