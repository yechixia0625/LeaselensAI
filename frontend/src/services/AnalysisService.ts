import type { LeaseLensReport } from "@/types/report";
import { UnauthorizedError } from "./authService";
import type { AnalysisIntake } from "./intakeTransfer";

export const ANALYSIS_API_PATH = "/api/analyze-space";

export class AnalysisService {
  static createFormData(file: File, intake: AnalysisIntake): FormData {
    const formData = new FormData();
    formData.append("photo", file);
    formData.append("business_type", intake.businessType);
    formData.append("expected_rent", String(intake.expectedRent));
    formData.append("square_meters", String(intake.squareMeters));
    formData.append("lease_term_months", String(intake.leaseTermMonths));
    formData.append("service_charge_monthly", String(intake.serviceChargeMonthly));
    formData.append("fitout_budget", String(intake.fitoutBudget));
    formData.append("cooking_intensity", intake.cookingIntensity);
    formData.append("floor_position", intake.floorPosition);
    formData.append("layout_shape", intake.layoutShape);
    formData.append("has_water_supply", intake.hasWaterSupply);
    formData.append("has_floor_trap", intake.hasFloorTrap);
    formData.append("has_grease_trap", intake.hasGreaseTrap);
    formData.append("electrical_readiness", intake.electricalReadiness);
    formData.append("has_gas", intake.hasGas);
    formData.append("has_exhaust", intake.hasExhaust);
    formData.append("wastewater_readiness", intake.wastewaterReadiness);
    formData.append("approved_use_status", intake.approvedUseStatus);
    appendOptionalNumber(formData, "rent_free_months", intake.rentFreeMonths);
    appendOptionalNumber(formData, "deposit_months", intake.depositMonths);
    appendOptionalNumber(formData, "other_monthly_costs", intake.otherMonthlyCosts);
    appendOptionalNumber(
      formData,
      "utilities_monthly_estimate",
      intake.utilitiesMonthlyEstimate
    );
    appendOptionalNumber(formData, "staffing_monthly", intake.staffingMonthly);
    appendOptionalNumber(formData, "marketing_monthly", intake.marketingMonthly);
    appendOptionalNumber(formData, "insurance_monthly", intake.insuranceMonthly);
    appendOptionalNumber(formData, "license_fees", intake.licenseFees);
    appendOptionalNumber(formData, "reinstatement_cost", intake.reinstatementCost);
    appendOptionalNumber(
      formData,
      "expected_daily_customers",
      intake.expectedDailyCustomers
    );
    appendOptionalNumber(formData, "average_spend", intake.averageSpend);
    appendOptionalNumber(formData, "gross_margin", intake.grossMargin);
    appendOptionalNumber(formData, "frontage_width_m", intake.frontageWidthM);
    appendOptionalNumber(formData, "ceiling_height_m", intake.ceilingHeightM);
    appendOptionalNumber(formData, "usable_area_ratio", intake.usableAreaRatio);
    appendOptionalNumber(formData, "storage_area_sqm", intake.storageAreaSqm);
    appendOptionalNumber(formData, "seating_capacity", intake.seatingCapacity);
    if (intake.loadingAccess) formData.append("loading_access", intake.loadingAccess);
    if (intake.toiletAccess) formData.append("toilet_access", intake.toiletAccess);
    if (intake.signageVisibility) {
      formData.append("signage_visibility", intake.signageVisibility);
    }
    if (intake.exhaustRouteAvailable) {
      formData.append("exhaust_route_available", intake.exhaustRouteAvailable);
    }
    formData.append("location_mode", intake.location.mode);
    formData.append("latitude", String(intake.location.latitude));
    formData.append("longitude", String(intake.location.longitude));
    if (intake.location.siteLabel) {
      formData.append("site_label", intake.location.siteLabel);
    }
    return formData;
  }

  /**
   * Submit analysis via POST with multipart form data.
   * Returns a ReadableStream for SSE consumption.
   */
  static async submitAnalysis(formData: FormData): Promise<Response> {
    const response = await fetch(ANALYSIS_API_PATH, {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    if (response.status === 401) {
      throw new UnauthorizedError();
    }
    if (!response.ok) {
      throw new Error(`Analysis request failed: ${response.status}`);
    }

    return response;
  }

  /**
   * Fetch a saved report by ID.
   */
  static async getReport(id: string): Promise<LeaseLensReport> {
    const res = await fetch(`/api/v1/reports/${id}`);
    if (!res.ok) throw new Error(`Report fetch failed: ${res.status}`);
    return res.json();
  }
}

function appendOptionalNumber(formData: FormData, key: string, value?: number): void {
  if (value !== undefined && Number.isFinite(value)) {
    formData.append(key, String(value));
  }
}
