import pytest

from src.api.deps import provide_settings
from src.config.settings import Settings


@pytest.fixture(autouse=True)
def demo_auth_settings(app):
    async def override_settings():
        return Settings(
            demo_auth_enabled=True,
            demo_auth_username="demo",
            demo_auth_password="secret-pass",
            demo_auth_secret="super-secret-signing-key",
        )

    app.dependency_overrides[provide_settings] = override_settings
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_sets_cookie(client):
    response = await client.post(
        "/api/auth/login",
        json={"username": "demo", "password": "secret-pass"},
    )

    assert response.status_code == 200
    assert response.json()["authenticated"] is True
    assert "set-cookie" in response.headers
    assert "leaselens_demo_session=" in response.headers["set-cookie"]


@pytest.mark.asyncio
async def test_login_rejects_bad_password(client):
    response = await client.post(
        "/api/auth/login",
        json={"username": "demo", "password": "wrong"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_session_reports_authenticated(client):
    login = await client.post(
        "/api/auth/login",
        json={"username": "demo", "password": "secret-pass"},
    )

    response = await client.get("/api/auth/session", cookies=login.cookies)

    assert response.status_code == 200
    assert response.json()["authenticated"] is True
    assert response.json()["username"] == "demo"


@pytest.mark.asyncio
async def test_session_reports_unauthenticated_without_cookie(client):
    response = await client.get("/api/auth/session")

    assert response.status_code == 200
    assert response.json() == {
        "authenticated": False,
        "username": None,
        "authEnabled": True,
    }
