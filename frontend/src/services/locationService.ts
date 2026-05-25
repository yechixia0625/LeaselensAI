import { UnauthorizedError } from "./authService";
import type { SiteLocation } from "./intakeTransfer";

export interface LocationPrediction {
  placeId: string;
  text: string;
}

export class LocationService {
  static async autocomplete(input: string, sessionToken: string): Promise<LocationPrediction[]> {
    const response = await fetch("/api/locations/autocomplete", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input, sessionToken }),
    });
    if (response.status === 401) throw new UnauthorizedError();
    if (!response.ok) throw new Error(`Address search failed: HTTP ${response.status}`);
    const result = (await response.json()) as { predictions: LocationPrediction[] };
    return result.predictions;
  }

  static async resolve(placeId: string, sessionToken: string): Promise<SiteLocation> {
    const response = await fetch("/api/locations/resolve", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ placeId, sessionToken }),
    });
    if (response.status === 401) throw new UnauthorizedError();
    if (!response.ok) throw new Error(`Address resolution failed: HTTP ${response.status}`);
    const location = (await response.json()) as {
      siteLabel: string;
      latitude: number;
      longitude: number;
    };
    return { mode: "address", ...location };
  }
}
