async def _registered_user_headers(client, phone="+224622222201"):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"phone": phone, "country_code": "GN", "pin": "1234"},
    )
    otp_code = register_resp.json()["sandbox_otp_code"]
    verify_resp = await client.post(
        "/api/v1/auth/verify-otp", json={"phone": phone, "code": otp_code}
    )
    access_token = verify_resp.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


async def test_kyc_status_before_start_is_empty(client):
    headers = await _registered_user_headers(client)
    response = await client.get("/api/v1/kyc/status", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["profile"] is None
    assert body["current_kyc_level"] == 0


async def test_kyc_start_creates_level_1_draft(client):
    headers = await _registered_user_headers(client, phone="+224622222202")
    response = await client.post("/api/v1/kyc/start", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["level_requested"] == 1
    assert body["status"] == "draft"


async def test_kyc_start_twice_returns_same_draft(client):
    headers = await _registered_user_headers(client, phone="+224622222203")
    first = await client.post("/api/v1/kyc/start", headers=headers)
    second = await client.post("/api/v1/kyc/start", headers=headers)
    assert first.json()["id"] == second.json()["id"]


async def test_submit_without_documents_fails(client):
    headers = await _registered_user_headers(client, phone="+224622222204")
    await client.post("/api/v1/kyc/start", headers=headers)
    response = await client.post("/api/v1/kyc/submit", headers=headers)
    assert response.status_code == 422


async def test_full_kyc_level_1_flow_auto_approves_in_sandbox(client):
    headers = await _registered_user_headers(client, phone="+224622222205")
    await client.post("/api/v1/kyc/start", headers=headers)

    id_resp = await client.post(
        "/api/v1/kyc/documents",
        headers=headers,
        data={"document_type": "national_id"},
        files={"file": ("id.jpg", b"fake-id-bytes", "image/jpeg")},
    )
    assert id_resp.status_code == 200, id_resp.text

    selfie_resp = await client.post(
        "/api/v1/kyc/documents",
        headers=headers,
        data={"document_type": "selfie"},
        files={"file": ("selfie.jpg", b"fake-selfie-bytes", "image/jpeg")},
    )
    assert selfie_resp.status_code == 200

    submit_resp = await client.post("/api/v1/kyc/submit", headers=headers)
    assert submit_resp.status_code == 200, submit_resp.text
    body = submit_resp.json()
    assert body["status"] == "approved"

    status_resp = await client.get("/api/v1/kyc/status", headers=headers)
    assert status_resp.json()["current_kyc_level"] == 1
    assert len(status_resp.json()["documents"]) == 2


async def test_submit_missing_identity_document_fails(client):
    headers = await _registered_user_headers(client, phone="+224622222206")
    await client.post("/api/v1/kyc/start", headers=headers)
    await client.post(
        "/api/v1/kyc/documents",
        headers=headers,
        data={"document_type": "selfie"},
        files={"file": ("selfie.jpg", b"fake-selfie-bytes", "image/jpeg")},
    )
    response = await client.post("/api/v1/kyc/submit", headers=headers)
    assert response.status_code == 422


async def test_upload_document_requires_active_session(client):
    headers = await _registered_user_headers(client, phone="+224622222207")
    response = await client.post(
        "/api/v1/kyc/documents",
        headers=headers,
        data={"document_type": "selfie"},
        files={"file": ("selfie.jpg", b"fake-selfie-bytes", "image/jpeg")},
    )
    assert response.status_code == 422


async def test_kyc_endpoints_require_auth(client):
    response = await client.post("/api/v1/kyc/start")
    assert response.status_code == 401
