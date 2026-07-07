import uuid

from app.core.config import get_settings


async def test_sandbox_endpoints_404_outside_sandbox_mode(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "sandbox_mode", False)
    response = await client.post(
        f"/api/v1/sandbox/topups/{uuid.uuid4()}/simulate-success"
    )
    assert response.status_code == 404
