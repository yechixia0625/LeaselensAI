import pytest

from src.api.deps import provide_analysis_service, provide_settings
from src.config.settings import Settings


class StubAnalysisService:
    async def analyze(self, intake):
        yield 'data: {"summary": {"score": 82}}\n\n'


VALID_LOCATION = {
    "location_mode": "address",
    "latitude": "31.2304",
    "longitude": "121.4737",
    "site_label": "Selected Retail Site",
}


@pytest.fixture(autouse=True)
def analysis_dependency(app):
    async def provide_stub_analysis_service():
        return StubAnalysisService()

    app.dependency_overrides[provide_analysis_service] = provide_stub_analysis_service
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_analyze_space_is_available_at_strict_public_path(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            **VALID_LOCATION,
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


@pytest.mark.asyncio
async def test_analyze_space_rejects_pdf(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.pdf", b"%PDF", "application/pdf")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            **VALID_LOCATION,
        },
    )

    assert response.status_code == 415


@pytest.mark.asyncio
async def test_analyze_space_rejects_nonpositive_metrics(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "-1",
            "square_meters": "80",
            **VALID_LOCATION,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_space_requires_resolved_label_for_address_location(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            "location_mode": "address",
            "latitude": "31.2304",
            "longitude": "121.4737",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_space_rejects_invalid_location_coordinates(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            "location_mode": "current",
            "latitude": "95",
            "longitude": "121.4737",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_space_requires_auth_when_demo_auth_enabled(client, app):
    async def override_settings():
        return Settings(
            demo_auth_enabled=True,
            demo_auth_username="demo",
            demo_auth_password="secret-pass",
            demo_auth_secret="super-secret-signing-key",
        )

    app.dependency_overrides[provide_settings] = override_settings
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            **VALID_LOCATION,
        },
    )

    assert response.status_code == 401
