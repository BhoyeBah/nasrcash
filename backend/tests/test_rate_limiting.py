async def test_login_endpoint_is_rate_limited_per_ip(client):
    await client.post(
        "/api/v1/auth/register",
        json={"phone": "+224699999901", "country_code": "GN", "pin": "1234"},
    )

    responses = []
    for _ in range(11):
        response = await client.post(
            "/api/v1/auth/login", json={"phone": "+224699999901", "pin": "wrong"}
        )
        responses.append(response.status_code)

    assert 429 in responses


async def test_register_endpoint_is_rate_limited_per_ip(client):
    responses = []
    for i in range(6):
        response = await client.post(
            "/api/v1/auth/register",
            json={"phone": f"+22469999991{i}", "country_code": "GN", "pin": "1234"},
        )
        responses.append(response.status_code)

    assert 429 in responses
