from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from src.api.deps import provide_analysis_service, require_demo_auth
from src.models.schemas.intake import (
    ApprovedUseStatus,
    CookingIntensity,
    FloorPosition,
    LayoutShape,
    Readiness,
    SpaceIntakeRequest,
)
from src.services.analysis import AnalysisService

router = APIRouter(tags=["analysis"])

SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


@router.post("/analyze-space")
async def analyze_space(
    photo: UploadFile = File(...),
    business_type: str = Form(..., min_length=1, max_length=100),
    expected_rent: float = Form(..., gt=0),
    square_meters: float = Form(..., gt=0),
    lease_term_months: int | None = Form(None, gt=0),
    service_charge_monthly: float = Form(0, ge=0),
    fitout_budget: float | None = Form(None, ge=0),
    cooking_intensity: CookingIntensity = Form("unknown"),
    floor_position: FloorPosition = Form("unknown"),
    layout_shape: LayoutShape = Form("unknown"),
    has_water_supply: Readiness = Form("unknown"),
    has_floor_trap: Readiness = Form("unknown"),
    has_grease_trap: Readiness = Form("unknown"),
    electrical_readiness: Readiness = Form("unknown"),
    has_gas: Readiness = Form("unknown"),
    has_exhaust: Readiness = Form("unknown"),
    wastewater_readiness: Readiness = Form("unknown"),
    approved_use_status: ApprovedUseStatus = Form("unknown"),
    rent_free_months: int = Form(0, ge=0),
    deposit_months: float = Form(0, ge=0),
    other_monthly_costs: float = Form(0, ge=0),
    utilities_monthly_estimate: float | None = Form(None, ge=0),
    staffing_monthly: float | None = Form(None, ge=0),
    marketing_monthly: float = Form(0, ge=0),
    insurance_monthly: float = Form(0, ge=0),
    license_fees: float = Form(0, ge=0),
    reinstatement_cost: float = Form(0, ge=0),
    expected_daily_customers: int | None = Form(None, gt=0),
    average_spend: float | None = Form(None, gt=0),
    gross_margin: float | None = Form(None, gt=0, le=1),
    frontage_width_m: float | None = Form(None, gt=0),
    ceiling_height_m: float | None = Form(None, gt=0),
    usable_area_ratio: float | None = Form(None, gt=0, le=1),
    storage_area_sqm: float | None = Form(None, ge=0),
    seating_capacity: int | None = Form(None, ge=0),
    loading_access: Readiness = Form("unknown"),
    toilet_access: Readiness = Form("unknown"),
    signage_visibility: Readiness = Form("unknown"),
    exhaust_route_available: Readiness = Form("unknown"),
    location_mode: Literal["current", "address"] = Form(...),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    site_label: str | None = Form(None),
    _username: str | None = Depends(require_demo_auth),
    analysis_service: AnalysisService = Depends(provide_analysis_service),
):
    """Analyze a commercial space. Returns SSE stream with agent logs and final report."""
    if photo.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only PNG, JPEG, and WebP space images are supported.",
        )

    photo_bytes = await photo.read()
    if not photo_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(photo_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="The uploaded image exceeds 10 MB.")

    try:
        intake = SpaceIntakeRequest(
            photo_bytes=photo_bytes,
            photo_filename=photo.filename,
            photo_content_type=photo.content_type,
            business_type=business_type,
            expected_rent=expected_rent,
            square_meters=square_meters,
            lease_term_months=lease_term_months,
            service_charge_monthly=service_charge_monthly,
            fitout_budget=fitout_budget,
            cooking_intensity=cooking_intensity,
            floor_position=floor_position,
            layout_shape=layout_shape,
            has_water_supply=has_water_supply,
            has_floor_trap=has_floor_trap,
            has_grease_trap=has_grease_trap,
            electrical_readiness=electrical_readiness,
            has_gas=has_gas,
            has_exhaust=has_exhaust,
            wastewater_readiness=wastewater_readiness,
            approved_use_status=approved_use_status,
            rent_free_months=rent_free_months,
            deposit_months=deposit_months,
            other_monthly_costs=other_monthly_costs,
            utilities_monthly_estimate=utilities_monthly_estimate,
            staffing_monthly=staffing_monthly,
            marketing_monthly=marketing_monthly,
            insurance_monthly=insurance_monthly,
            license_fees=license_fees,
            reinstatement_cost=reinstatement_cost,
            expected_daily_customers=expected_daily_customers,
            average_spend=average_spend,
            gross_margin=gross_margin,
            frontage_width_m=frontage_width_m,
            ceiling_height_m=ceiling_height_m,
            usable_area_ratio=usable_area_ratio,
            storage_area_sqm=storage_area_sqm,
            seating_capacity=seating_capacity,
            loading_access=loading_access,
            toilet_access=toilet_access,
            signage_visibility=signage_visibility,
            exhaust_route_available=exhaust_route_available,
            location_mode=location_mode,
            latitude=latitude,
            longitude=longitude,
            site_label=site_label,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_input=False, include_context=False),
        ) from exc

    async def event_generator():
        async for sse_line in analysis_service.analyze(intake):
            yield sse_line

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
