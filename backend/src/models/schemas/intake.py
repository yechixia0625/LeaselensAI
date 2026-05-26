from typing import Literal

from pydantic import BaseModel, Field, model_validator

Readiness = Literal["yes", "no", "unknown"]
CookingIntensity = Literal["none", "light", "full", "unknown"]
FloorPosition = Literal["basement", "ground", "upper", "mall", "unknown"]
LayoutShape = Literal["regular", "narrow", "corner", "irregular", "unknown"]
ApprovedUseStatus = Literal["confirmed", "needs_change_of_use", "unknown"]


class SpaceIntakeRequest(BaseModel):
    """Parsed from multipart form-data."""

    photo_bytes: bytes
    photo_filename: str | None = None
    photo_content_type: str
    business_type: str = Field(..., min_length=1, max_length=100)
    expected_rent: float = Field(..., gt=0)
    square_meters: float = Field(..., gt=0)
    location_mode: Literal["current", "address"]
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    site_label: str | None = None

    lease_term_months: int | None = Field(None, gt=0)
    service_charge_monthly: float = Field(0, ge=0)
    fitout_budget: float | None = Field(None, ge=0)
    cooking_intensity: CookingIntensity = "unknown"
    floor_position: FloorPosition = "unknown"
    layout_shape: LayoutShape = "unknown"
    has_water_supply: Readiness = "unknown"
    has_floor_trap: Readiness = "unknown"
    has_grease_trap: Readiness = "unknown"
    electrical_readiness: Readiness = "unknown"
    has_gas: Readiness = "unknown"
    has_exhaust: Readiness = "unknown"
    wastewater_readiness: Readiness = "unknown"
    approved_use_status: ApprovedUseStatus = "unknown"

    rent_free_months: int = Field(0, ge=0)
    deposit_months: float = Field(0, ge=0)
    other_monthly_costs: float = Field(0, ge=0)
    utilities_monthly_estimate: float | None = Field(None, ge=0)
    staffing_monthly: float | None = Field(None, ge=0)
    marketing_monthly: float = Field(0, ge=0)
    insurance_monthly: float = Field(0, ge=0)
    license_fees: float = Field(0, ge=0)
    reinstatement_cost: float = Field(0, ge=0)
    expected_daily_customers: int | None = Field(None, gt=0)
    average_spend: float | None = Field(None, gt=0)
    gross_margin: float | None = Field(None, gt=0, le=1)

    frontage_width_m: float | None = Field(None, gt=0)
    ceiling_height_m: float | None = Field(None, gt=0)
    usable_area_ratio: float | None = Field(None, gt=0, le=1)
    storage_area_sqm: float | None = Field(None, ge=0)
    seating_capacity: int | None = Field(None, ge=0)
    loading_access: Readiness = "unknown"
    toilet_access: Readiness = "unknown"
    signage_visibility: Readiness = "unknown"
    exhaust_route_available: Readiness = "unknown"

    @model_validator(mode="after")
    def require_address_label(self) -> "SpaceIntakeRequest":
        if self.location_mode == "address" and not (self.site_label or "").strip():
            raise ValueError("Address location requires a selected site label.")
        return self
