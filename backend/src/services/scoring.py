from typing import Any

from src.models.schemas.intake import SpaceIntakeRequest

FNB_TERMS = ("cafe", "coffee", "bakery", "restaurant", "bar", "food", "bistro")

INDUSTRY_PROFILES = {
    "cafe": {
        "ideal_min": 35,
        "ideal_max": 120,
        "rent_psf": 16,
        "traffic": 135,
        "spend": 18,
        "margin": 0.68,
        "staffing": 10_000,
        "utilities": 850,
        "fitout": 60_000,
    },
    "coffee": {
        "ideal_min": 35,
        "ideal_max": 120,
        "rent_psf": 16,
        "traffic": 135,
        "spend": 18,
        "margin": 0.68,
        "staffing": 9_000,
        "utilities": 750,
        "fitout": 55_000,
    },
    "coffee shop": {
        "ideal_min": 35,
        "ideal_max": 120,
        "rent_psf": 16,
        "traffic": 135,
        "spend": 18,
        "margin": 0.68,
        "staffing": 9_000,
        "utilities": 750,
        "fitout": 55_000,
    },
    "bakery": {
        "ideal_min": 45,
        "ideal_max": 140,
        "rent_psf": 14,
        "traffic": 110,
        "spend": 16,
        "margin": 0.62,
        "staffing": 11_000,
        "utilities": 1_100,
        "fitout": 75_000,
    },
    "restaurant": {
        "ideal_min": 70,
        "ideal_max": 220,
        "rent_psf": 18,
        "traffic": 100,
        "spend": 32,
        "margin": 0.58,
        "staffing": 18_000,
        "utilities": 1_800,
        "fitout": 130_000,
    },
    "bar": {
        "ideal_min": 60,
        "ideal_max": 180,
        "rent_psf": 17,
        "traffic": 80,
        "spend": 38,
        "margin": 0.7,
        "staffing": 16_000,
        "utilities": 1_400,
        "fitout": 110_000,
    },
    "bookstore": {
        "ideal_min": 80,
        "ideal_max": 260,
        "rent_psf": 12,
        "traffic": 80,
        "spend": 24,
        "margin": 0.45,
        "staffing": 6_000,
        "utilities": 500,
        "fitout": 45_000,
    },
    "boutique": {
        "ideal_min": 45,
        "ideal_max": 160,
        "rent_psf": 19,
        "traffic": 75,
        "spend": 65,
        "margin": 0.55,
        "staffing": 7_000,
        "utilities": 450,
        "fitout": 65_000,
    },
}


def enrich_summary(
    intake: SpaceIntakeRequest,
    financial_model: dict[str, Any],
    map_data: dict[str, Any],
    _llm_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build a traceable score from structured inputs and verified map availability."""
    metrics = _financial_metrics(intake, financial_model)
    flags: list[dict[str, Any]] = []
    if financial_model.get("estimateStatus") == "fallback":
        _add_flag(
            flags,
            "finance",
            "warning",
            "Financial estimates use fallback benchmarks because model output was unavailable.",
            "fallback_financial_model",
        )
    elif financial_model.get("estimateStatus") == "benchmark":
        _add_flag(
            flags,
            "finance",
            "info",
            "Missing financial inputs were filled using industry benchmark assumptions.",
            "industry_benchmark",
        )
    components = [
        _finance_component(intake, metrics, flags),
        _building_component(intake, flags),
        _regulatory_component(intake, flags),
        _location_component(intake, map_data, flags),
    ]
    component_score = sum(component["score"] for component in components)
    fixed_score = int(_clamp(round(component_score / 60 * 100), 0, 100))
    llm_score = 0
    total_score = fixed_score
    blocking = any(flag["blocking"] for flag in flags if flag["severity"] == "critical")
    return {
        "score": total_score,
        "verdict": _verdict(total_score, blocking),
        "paybackMonths": metrics["paybackMonths"],
        "scoreBreakdown": {
            "fixedScore": fixed_score,
            "maxFixedScore": 100,
            "llmScore": llm_score,
            "maxLlmScore": 0,
            "totalScore": total_score,
            "confidence": _confidence(map_data, flags),
            "components": components,
            "riskFlags": flags,
        },
    }


def recommend_locations(
    _intake: SpaceIntakeRequest,
    _map_data: dict[str, Any],
    _summary: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return no alternatives until candidate-specific market data is queried."""
    return []


def _financial_metrics(
    intake: SpaceIntakeRequest,
    financial_model: dict[str, Any],
) -> dict[str, float]:
    profile = _industry_profile(intake.business_type)
    if intake.expected_daily_customers is not None:
        traffic = intake.expected_daily_customers
        conversion = 1.0
        demand_basis = "paying_customers"
    else:
        traffic = int(profile["traffic"])
        conversion = 0.08
        demand_basis = "estimated_foot_traffic"
    spend = intake.average_spend or profile["spend"]
    margin = intake.gross_margin or profile["margin"]
    rent = intake.expected_rent
    lease_term = float(intake.lease_term_months or 36)
    rent_free = min(float(intake.rent_free_months), max(lease_term - 1, 0))
    effective_rent = rent * (lease_term - rent_free) / lease_term if lease_term > 0 else rent
    using_detailed_costs = (
        intake.utilities_monthly_estimate is not None or intake.staffing_monthly is not None
    )
    if using_detailed_costs:
        utilities = intake.utilities_monthly_estimate
        if utilities is None:
            utilities = float(profile["utilities"])
        staffing = intake.staffing_monthly
        if staffing is None:
            staffing = float(profile["staffing"])
        base_non_rent_operating = utilities + staffing
    else:
        utilities = 0.0
        staffing = 0.0
        base_non_rent_operating = profile["utilities"] + profile["staffing"]
    fitout = intake.fitout_budget
    if fitout is None:
        fitout = profile["fitout"]

    supplied_financial_inputs = all(
        value is not None
        for value in (
            intake.expected_daily_customers,
            intake.average_spend,
            intake.gross_margin,
            intake.utilities_monthly_estimate,
            intake.staffing_monthly,
            intake.fitout_budget,
        )
    )
    if financial_model.get("estimateStatus") != "fallback":
        financial_model["estimateStatus"] = (
            "user_inputs" if supplied_financial_inputs else "benchmark"
        )

    total_occupancy = (
        effective_rent + intake.service_charge_monthly + intake.other_monthly_costs
    )
    monthly_operating_cost = (
        total_occupancy
        + base_non_rent_operating
        + intake.marketing_monthly
        + intake.insurance_monthly
    )
    gross_revenue = traffic * 30 * conversion * spend
    gross_profit = gross_revenue * margin
    net_profit = gross_profit - monthly_operating_cost
    rent_pressure = total_occupancy / gross_revenue if gross_revenue > 0 else 1
    break_even_revenue = monthly_operating_cost / margin if margin > 0 else 999_999
    setup_capital = (
        fitout
        + rent * intake.deposit_months
        + intake.license_fees
        + intake.reinstatement_cost
    )
    payback_months = _payback_months(setup_capital, net_profit)
    lease_runway = lease_term - payback_months if payback_months < 999 else -lease_term

    financial_model.update(
        {
            "baseRent": rent,
            "expectedTraffic": int(traffic),
            "conversionRate": conversion,
            "demandBasis": demand_basis,
            "averageSpend": spend,
            "grossMargin": margin,
            "fixedCostNonRent": round(monthly_operating_cost - total_occupancy, 2),
            "initialDecorationCost": fitout,
            "effectiveMonthlyRent": round(effective_rent, 2),
            "totalMonthlyOccupancyCost": round(total_occupancy, 2),
            "monthlyOperatingCost": round(monthly_operating_cost, 2),
            "breakEvenRevenue": round(break_even_revenue, 2),
            "setupCapitalRequired": round(setup_capital, 2),
            "leaseRunwayMonths": round(lease_runway, 1),
            "paybackMonths": payback_months,
        }
    )
    return {
        "grossRevenue": gross_revenue,
        "grossProfit": gross_profit,
        "netProfit": net_profit,
        "rentPressure": rent_pressure,
        "breakEvenRevenue": break_even_revenue,
        "paybackMonths": payback_months,
        "leaseTermMonths": lease_term,
        "leaseRunwayMonths": lease_runway,
    }


def _finance_component(
    intake: SpaceIntakeRequest,
    metrics: dict[str, float],
    flags: list[dict[str, Any]],
) -> dict[str, Any]:
    rent_pressure = metrics["rentPressure"]
    gross_revenue = metrics["grossRevenue"]
    net_profit = metrics["netProfit"]
    profit_margin = net_profit / gross_revenue if gross_revenue > 0 else -1
    lease_term = metrics["leaseTermMonths"]
    payback = metrics["paybackMonths"]
    break_even_ratio = (
        metrics["breakEvenRevenue"] / gross_revenue if gross_revenue > 0 else 9
    )
    using_detailed_costs = (
        intake.utilities_monthly_estimate is not None or intake.staffing_monthly is not None
    )

    score = 0.0
    score += _clamp((0.42 - rent_pressure) / 0.27 * 8, 0, 8)
    score += _clamp((profit_margin + 0.05) / 0.25 * 6, 0, 6)
    score += _clamp((1.15 - break_even_ratio) / 0.55 * 5, 0, 5)
    payback_ratio = payback / lease_term if lease_term > 0 else 9
    score += _clamp((0.9 - payback_ratio) / 0.55 * 5, 0, 5)

    assumptions = []
    if intake.lease_term_months is None:
        assumptions.append("Lease term defaulted to 36 months.")
    if intake.fitout_budget is None:
        assumptions.append("Fit-out budget defaulted from industry benchmark.")
    if intake.utilities_monthly_estimate is None and using_detailed_costs:
        assumptions.append("Utilities estimate defaulted from industry benchmark.")
    if intake.staffing_monthly is None and using_detailed_costs:
        assumptions.append("Staffing estimate defaulted from industry benchmark.")

    if rent_pressure > 0.3:
        _add_flag(
            flags,
            "finance",
            "warning",
            "Occupancy cost exceeds 30% of projected gross revenue.",
            "fixed_finance_agent",
        )
    if net_profit <= 0:
        _add_flag(
            flags,
            "finance",
            "critical",
            "Projected monthly net profit is negative under current assumptions.",
            "fixed_finance_agent",
        )
    if payback > lease_term * 0.7:
        _add_flag(
            flags,
            "finance",
            "warning",
            "Estimated payback is too close to or longer than the lease term.",
            "fixed_finance_agent",
        )

    return {
        "key": "finance_and_lease_economics",
        "label": "Finance and lease economics",
        "score": round(score, 1),
        "maxScore": 24,
        "rationale": "Uses effective rent, all-in occupancy cost, break-even revenue, and payback.",
        "evidence": [
            {
                "label": "Rent pressure",
                "value": f"{rent_pressure * 100:.1f}%",
                "source": "fixed_finance_agent",
            },
            {
                "label": "Net profit",
                "value": f"S${net_profit:,.0f}/mo",
                "source": "fixed_finance_agent",
            },
            {
                "label": "Payback",
                "value": f"{payback:g} months",
                "source": "fixed_finance_agent",
            },
        ],
        "assumptionsUsed": assumptions,
    }


def _building_component(
    intake: SpaceIntakeRequest,
    flags: list[dict[str, Any]],
) -> dict[str, Any]:
    is_fnb = _is_fnb(intake.business_type)
    full_cooking = intake.cooking_intensity == "full"
    light_or_full = intake.cooking_intensity in {"light", "full"}
    if is_fnb:
        checks = [
            ("Water supply", intake.has_water_supply, 2.0, "SFA food shop licensing readiness"),
            ("Electrical readiness", intake.electrical_readiness, 2.0, "EMA licensed worker check"),
            ("Floor trap", intake.has_floor_trap, 2.0, "PUB used-water readiness"),
            ("Wastewater readiness", intake.wastewater_readiness, 2.0, "PUB sanitary readiness"),
            (
                "Grease trap",
                intake.has_grease_trap,
                3.0 if light_or_full else 1.0,
                "PUB grease trap",
            ),
            (
                "Kitchen exhaust",
                intake.has_exhaust,
                3.0 if full_cooking else 1.0,
                "SCDF kitchen exhaust",
            ),
            ("Gas readiness", intake.has_gas, 1.0 if full_cooking else 0.5, "EMA gas worker check"),
            ("Layout shape", _layout_status(intake.layout_shape), 1.0, "architectural fit"),
        ]
    else:
        checks = [
            ("Electrical readiness", intake.electrical_readiness, 4.0, "electrical readiness"),
            ("Layout shape", _layout_status(intake.layout_shape), 4.0, "architectural fit"),
            ("Signage visibility", intake.signage_visibility, 4.0, "retail visibility"),
            ("Loading access", intake.loading_access, 2.0, "operating access"),
            ("Toilet access", intake.toilet_access, 2.0, "customer amenity"),
        ]
    score = 0.0
    assumptions = []
    for label, status, weight, source in checks:
        score += _readiness_points(status, weight)
        if status == "unknown":
            assumptions.append(f"{label} is unknown.")
            _add_flag(
                flags,
                "building",
                "info",
                f"{label} should be verified before signing.",
                source,
            )
        if status == "no" and is_fnb and label in {"Water supply", "Electrical readiness"}:
            _add_flag(
                flags,
                "building",
                "critical",
                f"{label} is missing for an F&B concept.",
                source,
                blocking=True,
            )

    if full_cooking and intake.has_exhaust == "no":
        _add_flag(
            flags,
            "building",
            "critical",
            "Full cooking requires a viable kitchen exhaust route before lease commitment.",
            "SCDF Fire Code kitchen exhaust screening",
            blocking=True,
        )
    if full_cooking and intake.has_floor_trap == "no" and intake.has_grease_trap == "no":
        _add_flag(
            flags,
            "building",
            "critical",
            "Full cooking lacks both floor trap and grease trap readiness.",
            "PUB grease trap and sanitary screening",
            blocking=True,
        )
    if full_cooking and intake.exhaust_route_available == "no":
        _add_flag(
            flags,
            "building",
            "warning",
            "No clear exhaust route was declared; landlord and QP review are needed.",
            "SCDF kitchen exhaust screening",
        )
    if intake.floor_position == "basement" and full_cooking:
        _add_flag(
            flags,
            "building",
            "warning",
            "Basement F&B can add exhaust and loading constraints.",
            "architectural fit",
        )

    return {
        "key": "building_services_readiness",
        "label": "Building services readiness",
        "score": round(_clamp(score, 0, 16), 1),
        "maxScore": 16,
        "rationale": "Checks water, power, gas, wastewater, grease trap, and exhaust readiness.",
        "evidence": [
            {
                "label": "Cooking intensity",
                "value": intake.cooking_intensity,
                "source": "user_input",
            },
            {"label": "Exhaust", "value": intake.has_exhaust, "source": "user_input"},
            {"label": "Grease trap", "value": intake.has_grease_trap, "source": "user_input"},
            {"label": "Floor trap", "value": intake.has_floor_trap, "source": "user_input"},
        ],
        "assumptionsUsed": assumptions,
    }


def _regulatory_component(
    intake: SpaceIntakeRequest,
    flags: list[dict[str, Any]],
) -> dict[str, Any]:
    score = 0.0
    assumptions = []
    if intake.approved_use_status == "confirmed":
        score += 3.0
    elif intake.approved_use_status == "unknown":
        score += 1.5
        assumptions.append("Approved use is unknown.")
        _add_flag(
            flags,
            "regulatory",
            "info",
            "Confirm approved use and landlord consent before signing.",
            "URA/HDB change-use screening",
        )
    else:
        _add_flag(
            flags,
            "regulatory",
            "warning",
            "Declared use may require change-of-use or landlord approval.",
            "URA/HDB change-use screening",
        )

    is_fnb = _is_fnb(intake.business_type)
    if is_fnb and intake.cooking_intensity != "none":
        if intake.has_grease_trap == "yes":
            score += 1.5
        elif intake.has_grease_trap == "unknown":
            score += 0.7
        if intake.has_exhaust == "yes":
            score += 1.5
        elif intake.has_exhaust == "unknown":
            score += 0.7
        _add_flag(
            flags,
            "regulatory",
            "info",
            "Food shop licensing, PUB grease trap, and SCDF exhaust checks remain screening items.",
            "SFA/PUB/SCDF screening",
        )
    else:
        score += 2.0

    if intake.fitout_budget and intake.fitout_budget > 50_000:
        _add_flag(
            flags,
            "regulatory",
            "info",
            "High fit-out budget may involve A&A, fire safety, or reinstatement review.",
            "BCA/HDB A&A screening",
        )
    score += 1.5 if intake.electrical_readiness == "yes" else 0.8
    if is_fnb:
        score += 1.0 if intake.has_gas in {"yes", "unknown"} else 0.3

    return {
        "key": "regulatory_and_approval_risk",
        "label": "Regulatory and approval risk",
        "score": round(_clamp(score, 0, 8), 1),
        "maxScore": 8,
        "rationale": "Screens approved use, food licensing, PUB, SCDF, EMA, and A&A risks.",
        "evidence": [
            {
                "label": "Approved use",
                "value": intake.approved_use_status,
                "source": "user_input",
            },
            {
                "label": "Screening only",
                "value": "Verify with landlord, QP, PE, LEW, SFA, PUB, SCDF, BCA/HDB/URA.",
                "source": "professional_caution",
            },
        ],
        "assumptionsUsed": assumptions,
    }


def _location_component(
    intake: SpaceIntakeRequest,
    map_data: dict[str, Any],
    flags: list[dict[str, Any]],
) -> dict[str, Any]:
    in_singapore = 1.15 <= intake.latitude <= 1.48 and 103.55 <= intake.longitude <= 104.1
    available = map_data.get("status") == "available"
    competitors = map_data.get("competitors", [])
    high_proximity = sum(1 for item in competitors if item.get("proximityLevel") == "HIGH")
    count = len(competitors)
    score = 0.0
    score += 4 if in_singapore else 1
    score += 2 if intake.site_label else 1
    score += 2 if available else 0.5
    if count == 0:
        score += 2
    elif count <= 3:
        score += 4
    elif count <= 7:
        score += 3
    else:
        score += 1.5
    score -= min(high_proximity, 3) * 0.7

    if not in_singapore:
        _add_flag(
            flags,
            "market",
            "warning",
            "Selected coordinates are outside the Singapore screening range.",
            "fixed_market_agent",
        )
    if not available:
        _add_flag(
            flags,
            "market",
            "info",
            "Live nearby-place data is unavailable; market score uses fallback assumptions.",
            "google_places",
        )

    return {
        "key": "location_and_competition_fit",
        "label": "Location and competition fit",
        "score": round(_clamp(score, 0, 12), 1),
        "maxScore": 12,
        "rationale": "Keeps location demand and nearby competition as a market validation signal.",
        "evidence": [
            {
                "label": "Selected site",
                "value": intake.site_label or "Current GPS coordinate",
                "source": "onemap_or_google_places",
            },
            {
                "label": "Nearby same-category places",
                "value": str(count),
                "source": "google_places",
            },
            {
                "label": "Locations within high proximity band",
                "value": str(high_proximity),
                "source": "google_places",
            },
        ],
        "assumptionsUsed": [],
    }


def _industry_profile(business_type: str) -> dict[str, float]:
    normalized = business_type.strip().lower()
    return INDUSTRY_PROFILES.get(
        normalized,
        {
            "ideal_min": 40,
            "ideal_max": 180,
            "rent_psf": 15,
            "traffic": 100,
            "spend": 30,
            "margin": 0.6,
            "staffing": 8_000,
            "utilities": 650,
            "fitout": 55_000,
        },
    )


def _is_fnb(business_type: str) -> bool:
    normalized = business_type.strip().lower()
    return any(term in normalized for term in FNB_TERMS)


def _layout_status(layout_shape: str) -> str:
    if layout_shape in {"regular", "corner"}:
        return "yes"
    if layout_shape == "unknown":
        return "unknown"
    return "no"


def _readiness_points(status: str, weight: float) -> float:
    if status == "yes":
        return weight
    if status == "unknown":
        return weight * 0.55
    return 0.0


def _payback_months(initial_cost: float, monthly_net_profit: float) -> float:
    if monthly_net_profit <= 0:
        return 999.0
    return round(initial_cost / monthly_net_profit, 1)


def _confidence(map_data: dict[str, Any], flags: list[dict[str, Any]]) -> str:
    if any(flag["severity"] == "critical" for flag in flags):
        return "LOW"
    if any(flag.get("source") == "fallback_financial_model" for flag in flags):
        return "LOW"
    unknown_flags = sum(1 for flag in flags if flag["severity"] == "info")
    if map_data.get("status") != "available":
        return "LOW"
    if unknown_flags > 0:
        return "MEDIUM"
    return "HIGH"


def _verdict(score: int, blocking: bool = False) -> str:
    if blocking:
        return "HIGH RISK - VERIFY BEFORE SIGNING"
    if score >= 80:
        return "APPROVED"
    if score >= 60:
        return "APPROVED WITH CONDITIONS"
    return "REJECTED"


def _add_flag(
    flags: list[dict[str, Any]],
    domain: str,
    severity: str,
    message: str,
    source: str | None = None,
    blocking: bool = False,
) -> None:
    candidate = {
        "domain": domain,
        "severity": severity,
        "message": message,
        "source": source,
        "blocking": blocking,
    }
    if candidate not in flags:
        flags.append(candidate)




def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
