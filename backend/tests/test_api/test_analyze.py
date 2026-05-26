import pytest

from src.api.deps import provide_analysis_service, provide_settings
from src.config.settings import Settings


class StubAnalysisService:
    seen_intake = None

    async def analyze(self, intake):
        StubAnalysisService.seen_intake = intake
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
        StubAnalysisService.seen_intake = None
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


@pytest.mark.asyncio
async def test_analyze_space_parses_v2_lease_and_building_fields(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            "lease_term_months": "18",
            "service_charge_monthly": "850",
            "fitout_budget": "70000",
            "cooking_intensity": "full",
            "floor_position": "ground",
            "layout_shape": "regular",
            "has_water_supply": "yes",
            "has_floor_trap": "no",
            "has_grease_trap": "no",
            "electrical_readiness": "yes",
            "has_gas": "unknown",
            "has_exhaust": "no",
            "wastewater_readiness": "no",
            "approved_use_status": "needs_change_of_use",
            "rent_free_months": "2",
            "deposit_months": "3",
            "other_monthly_costs": "1200",
            "utilities_monthly_estimate": "900",
            "staffing_monthly": "12000",
            "marketing_monthly": "700",
            "insurance_monthly": "250",
            "license_fees": "900",
            "reinstatement_cost": "15000",
            "expected_daily_customers": "140",
            "average_spend": "18",
            "gross_margin": "0.68",
            "frontage_width_m": "6",
            "ceiling_height_m": "3.2",
            "usable_area_ratio": "0.78",
            "storage_area_sqm": "8",
            "seating_capacity": "32",
            "loading_access": "yes",
            "toilet_access": "yes",
            "signage_visibility": "yes",
            "exhaust_route_available": "no",
            **VALID_LOCATION,
        },
    )

    assert response.status_code == 200
    intake = StubAnalysisService.seen_intake
    assert intake.lease_term_months == 18
    assert intake.service_charge_monthly == 850
    assert intake.fitout_budget == 70000
    assert intake.cooking_intensity == "full"
    assert intake.has_exhaust == "no"
    assert intake.approved_use_status == "needs_change_of_use"
    assert intake.expected_daily_customers == 140
    assert intake.frontage_width_m == 6


@pytest.mark.asyncio
async def test_analyze_space_rejects_invalid_v2_enums(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            "lease_term_months": "18",
            "cooking_intensity": "deep-fry-all-day",
            **VALID_LOCATION,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_space_rejects_zero_lease_term(client):
    response = await client.post(
        "/api/analyze-space",
        files={"photo": ("unit.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        data={
            "business_type": "Cafe",
            "expected_rent": "5200",
            "square_meters": "80",
            "lease_term_months": "0",
            **VALID_LOCATION,
        },
    )

    assert response.status_code == 422
