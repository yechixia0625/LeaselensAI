from src.models.schemas.intake import SpaceIntakeRequest
from src.services.scoring import enrich_summary, recommend_locations


def make_intake(**overrides):
    payload = {
        "photo_bytes": b"\x89PNG\r\n\x1a\n",
        "photo_filename": "space.png",
        "photo_content_type": "image/png",
        "business_type": "Cafe",
        "expected_rent": 7000,
        "square_meters": 75,
        "location_mode": "address",
        "latitude": 1.3008,
        "longitude": 103.8591,
        "site_label": "21 Haji Lane, Singapore 189214",
    }
    payload.update(overrides)
    return SpaceIntakeRequest(**payload)


def base_financial_model(**overrides):
    payload = {
        "baseRent": 7000,
        "expectedTraffic": 150,
        "conversionRate": 0.12,
        "averageSpend": 18,
        "grossMargin": 0.68,
        "fixedCostNonRent": 2500,
        "initialDecorationCost": 60000,
    }
    payload.update(overrides)
    return payload


def available_map_data():
    return {
        "status": "available",
        "competitors": [
            {
                "name": "Nearby Cafe",
                "distanceMeters": 120,
                "proximityLevel": "MEDIUM",
            }
        ],
    }


def test_short_lease_against_payback_adds_finance_warning():
    financial_model = base_financial_model(initialDecorationCost=90000)
    summary = enrich_summary(
        make_intake(
            lease_term_months=6,
            fitout_budget=90000,
            service_charge_monthly=900,
            rent_free_months=0,
        ),
        financial_model,
        available_map_data(),
        {"score": 75},
    )

    breakdown = summary["scoreBreakdown"]
    flags = breakdown["riskFlags"]
    assert breakdown["fixedScore"] <= 60
    assert any(flag["domain"] == "finance" and "lease term" in flag["message"] for flag in flags)
    assert financial_model["paybackMonths"] > 6


def test_full_cooking_without_exhaust_and_grease_trap_is_critical():
    summary = enrich_summary(
        make_intake(
            cooking_intensity="full",
            has_exhaust="no",
            has_floor_trap="no",
            has_grease_trap="no",
            wastewater_readiness="no",
            approved_use_status="needs_change_of_use",
        ),
        base_financial_model(),
        available_map_data(),
        {"score": 82},
    )

    breakdown = summary["scoreBreakdown"]
    critical_flags = [flag for flag in breakdown["riskFlags"] if flag["severity"] == "critical"]
    assert summary["verdict"] == "HIGH RISK - VERIFY BEFORE SIGNING"
    assert any(flag["blocking"] for flag in critical_flags)
    assert any("exhaust" in flag["message"].lower() for flag in critical_flags)
    assert any("grease" in flag["message"].lower() for flag in critical_flags)


def test_unknown_building_services_lower_confidence_without_blocking():
    summary = enrich_summary(
        make_intake(
            cooking_intensity="light",
            expected_daily_customers=420,
            average_spend=28,
            staffing_monthly=6000,
            has_water_supply="unknown",
            has_floor_trap="unknown",
            has_grease_trap="unknown",
            electrical_readiness="unknown",
            has_exhaust="unknown",
            wastewater_readiness="unknown",
        ),
        base_financial_model(),
        available_map_data(),
        {"score": 70},
    )

    breakdown = summary["scoreBreakdown"]
    assert breakdown["confidence"] == "MEDIUM"
    assert any(flag["severity"] == "info" for flag in breakdown["riskFlags"])
    assert not any(flag["blocking"] for flag in breakdown["riskFlags"])
    assert breakdown["components"][1]["key"] == "building_services_readiness"


def test_declared_daily_customers_are_not_multiplied_by_conversion_rate():
    financial_model = base_financial_model(conversionRate=0.12)
    enrich_summary(
        make_intake(
            expected_daily_customers=100,
            average_spend=20,
            gross_margin=0.5,
            fitout_budget=0,
            staffing_monthly=0,
            utilities_monthly_estimate=0,
        ),
        financial_model,
        available_map_data(),
        {"score": 70},
    )

    assert financial_model["expectedTraffic"] == 100
    assert financial_model["conversionRate"] == 1.0
    assert financial_model["demandBasis"] == "paying_customers"


def test_llm_score_does_not_change_deterministic_total():
    low = enrich_summary(make_intake(), base_financial_model(), available_map_data(), {"score": 0})
    high = enrich_summary(
        make_intake(), base_financial_model(), available_map_data(), {"score": 100}
    )

    assert low["score"] == high["score"]
    assert low["scoreBreakdown"]["maxFixedScore"] == 100
    assert low["scoreBreakdown"]["maxLlmScore"] == 0


def test_llm_financial_guesses_do_not_change_benchmark_based_score():
    baseline_model = base_financial_model()
    inflated_model = base_financial_model(
        expectedTraffic=5000,
        conversionRate=0.8,
        averageSpend=200,
        grossMargin=0.95,
        fixedCostNonRent=1,
        initialDecorationCost=1,
    )

    baseline = enrich_summary(make_intake(), baseline_model, available_map_data(), {"score": 70})
    inflated = enrich_summary(make_intake(), inflated_model, available_map_data(), {"score": 70})

    assert baseline["score"] == inflated["score"]
    assert baseline_model["expectedTraffic"] == inflated_model["expectedTraffic"]
    assert baseline_model["averageSpend"] == inflated_model["averageSpend"]


def test_non_fnb_does_not_receive_fnb_utility_risk_flags():
    summary = enrich_summary(
        make_intake(
            business_type="Boutique",
            cooking_intensity="none",
            has_floor_trap="unknown",
            has_grease_trap="unknown",
            has_exhaust="unknown",
            has_gas="unknown",
            wastewater_readiness="unknown",
        ),
        base_financial_model(),
        available_map_data(),
        {"score": 70},
    )

    messages = [flag["message"].lower() for flag in summary["scoreBreakdown"]["riskFlags"]]
    assert not any(
        "grease" in message or "exhaust" in message or "floor trap" in message
        for message in messages
    )


def test_static_candidate_pool_is_not_exposed_as_location_recommendations():
    locations = recommend_locations(make_intake(), available_map_data(), {"score": 72})

    assert locations == []


def test_fallback_financial_estimates_lower_confidence():
    summary = enrich_summary(
        make_intake(
            business_type="Boutique",
            cooking_intensity="none",
            electrical_readiness="yes",
            layout_shape="regular",
            signage_visibility="yes",
            loading_access="yes",
            toilet_access="yes",
            approved_use_status="confirmed",
        ),
        base_financial_model(
            estimateStatus="fallback",
            expectedTraffic=1000,
            conversionRate=0.5,
            averageSpend=100,
        ),
        available_map_data(),
        {"score": 70},
    )

    assert summary["scoreBreakdown"]["confidence"] == "LOW"
    assert any(
        "fallback benchmarks" in flag["message"]
        for flag in summary["scoreBreakdown"]["riskFlags"]
    )
