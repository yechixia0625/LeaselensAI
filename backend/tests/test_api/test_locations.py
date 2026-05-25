import pytest

from src.api.deps import provide_geo_service, provide_settings
from src.config.settings import Settings


class StubGeoService:
    async def autocomplete(self, value: str, session_token: str):
        assert value == "Market Street"
        assert session_token == "session-token-1"
        return [{"placeId": "place-1", "text": "Market Street, Test City"}]

    async def resolve(self, place_id: str, session_token: str):
        assert place_id == "place-1"
        assert session_token == "session-token-1"
        return {
            "siteLabel": "Market Street, Test City",
            "latitude": 31.2304,
            "longitude": 121.4737,
        }


@pytest.fixture(autouse=True)
def location_dependency(app):
    async def provide_stub_geo_service():
        return StubGeoService()

    app.dependency_overrides[provide_geo_service] = provide_stub_geo_service
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_location_autocomplete_returns_sanitized_predictions(client):
    response = await client.post(
        "/api/locations/autocomplete",
        json={"input": "Market Street", "sessionToken": "session-token-1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "predictions": [{"placeId": "place-1", "text": "Market Street, Test City"}]
    }


@pytest.mark.asyncio
async def test_location_resolution_returns_selected_coordinate(client):
    response = await client.post(
        "/api/locations/resolve",
        json={"placeId": "place-1", "sessionToken": "session-token-1"},
    )

    assert response.status_code == 200
    assert response.json()["latitude"] == 31.2304
    assert "api" not in response.json()


@pytest.mark.asyncio
async def test_location_autocomplete_requires_auth_when_demo_auth_enabled(client, app):
    async def override_settings():
        return Settings(
            demo_auth_enabled=True,
            demo_auth_username="demo",
            demo_auth_password="secret-pass",
            demo_auth_secret="super-secret-signing-key",
        )

    app.dependency_overrides[provide_settings] = override_settings
    response = await client.post(
        "/api/locations/autocomplete",
        json={"input": "Market Street", "sessionToken": "session-token-1"},
    )

    assert response.status_code == 401
