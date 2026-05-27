import asyncio
import json
import time

import pytest

from src.models.schemas.intake import SpaceIntakeRequest
from src.pipeline.orchestrator import AnalysisOrchestrator


class FakeGeo:
    async def nearby_map_data(self, intake):
        return {
            "center": [intake.latitude, intake.longitude],
            "locationMode": intake.location_mode,
            "siteLabel": intake.site_label,
            "dataSource": "google_places",
            "status": "available",
            "searchRadiusMeters": 500,
            "competitors": [
                {
                    "name": "Verified Cafe",
                    "lat": intake.latitude + 0.001,
                    "lng": intake.longitude,
                    "type": "cafe",
                    "distanceMeters": 111,
                    "proximityLevel": "HIGH",
                }
            ],
        }


class FailingGeo:
    async def nearby_map_data(self, intake):
        raise RuntimeError("Places unavailable")


class FastLLM:
    async def complete(self, prompt: str, system: str = "", **kwargs) -> str:
        if "spatial blueprint" in prompt:
            return """{"spatialBlueprint":{"aspectRatio":1.5,"elements":[],
            "heatZones":[]}}"""
        if "financial model" in prompt:
            return """{"financialModel":{"baseRent":5200,"expectedTraffic":120,
            "conversionRate":0.08,"averageSpend":35,"grossMargin":0.65,
            "fixedCostNonRent":2000,"initialDecorationCost":45000}}"""
        return """{"summary":{"score":82,"verdict":"APPROVED WITH CONDITIONS",
        "paybackMonths":9.2}}"""


class OverconfidentLLM(FastLLM):
    async def complete(self, prompt: str, system: str = "", **kwargs) -> str:
        if "strategic summary" in prompt:
            return """{"summary":{"score":100,"verdict":"APPROVED",
            "paybackMonths":6.0}}"""
        return await super().complete(prompt, system, **kwargs)


@pytest.fixture
def fake_intake():
    return SpaceIntakeRequest(
        photo_bytes=b"\x89PNG\r\n\x1a\n",
        photo_filename="space.png",
        photo_content_type="image/png",
        business_type="Cafe",
        expected_rent=5200,
        square_meters=80,
        location_mode="address",
        latitude=1.3008,
        longitude=103.8591,
        site_label="21 Haji Lane, Singapore 189214",
        lease_term_months=36,
        service_charge_monthly=450,
        fitout_budget=50000,
        cooking_intensity="light",
        floor_position="ground",
        layout_shape="regular",
        has_water_supply="yes",
        has_floor_trap="yes",
        has_grease_trap="yes",
        electrical_readiness="yes",
        has_gas="unknown",
        has_exhaust="yes",
        wastewater_readiness="yes",
        approved_use_status="confirmed",
        expected_daily_customers=260,
        average_spend=22,
        gross_margin=0.68,
    )


async def collect_chunks(orchestrator, intake):
    return [chunk async for chunk in orchestrator.run(intake)]


@pytest.mark.asyncio
async def test_report_is_last_raw_sse_data_frame(fake_intake):
    chunks = await asyncio.wait_for(
        collect_chunks(AnalysisOrchestrator(FastLLM(), FakeGeo()), fake_intake), timeout=0.5
    )
    payloads = [json.loads(chunk.split("data: ", 1)[1]) for chunk in chunks]

    assert chunks[-1].startswith("data: ")
    assert payloads[-1]["summary"]["verdict"] == "APPROVED"
    assert "event" not in payloads[-1]
    assert payloads[-1]["mapData"]["competitors"][0]["name"] == "Verified Cafe"
    assert all(payload["event"] == "agent_log" for payload in payloads[:-1])


@pytest.mark.asyncio
async def test_agents_finish_without_idle_timeout(fake_intake):
    start = time.monotonic()
    await asyncio.wait_for(
        collect_chunks(AnalysisOrchestrator(FastLLM(), FakeGeo()), fake_intake), timeout=0.5
    )

    assert time.monotonic() - start < 0.5


@pytest.mark.asyncio
async def test_places_failure_returns_unavailable_market_without_fake_competitors(fake_intake):
    chunks = await collect_chunks(AnalysisOrchestrator(FastLLM(), FailingGeo()), fake_intake)
    payload = json.loads(chunks[-1].split("data: ", 1)[1])

    assert payload["mapData"]["status"] == "unavailable"
    assert payload["mapData"]["competitors"] == []


@pytest.mark.asyncio
async def test_report_includes_fixed_llm_score_breakdown_and_recommendations(fake_intake):
    chunks = await collect_chunks(AnalysisOrchestrator(FastLLM(), FakeGeo()), fake_intake)
    payload = json.loads(chunks[-1].split("data: ", 1)[1])

    breakdown = payload["summary"]["scoreBreakdown"]
    assert breakdown["maxFixedScore"] == 100
    assert breakdown["maxLlmScore"] == 0
    assert 0 <= breakdown["fixedScore"] <= 100
    assert breakdown["llmScore"] == 0
    assert payload["summary"]["score"] == breakdown["totalScore"]
    assert sum(component["maxScore"] for component in breakdown["components"]) == 60
    assert payload["recommendedLocations"] == []


@pytest.mark.asyncio
async def test_strategy_llm_score_does_not_change_traceable_total(fake_intake):
    chunks = await collect_chunks(AnalysisOrchestrator(OverconfidentLLM(), FakeGeo()), fake_intake)
    payload = json.loads(chunks[-1].split("data: ", 1)[1])

    assert payload["summary"]["scoreBreakdown"]["llmScore"] == 0
    assert payload["summary"]["score"] <= 100
