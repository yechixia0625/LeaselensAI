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
