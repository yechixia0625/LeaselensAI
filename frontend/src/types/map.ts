export interface Competitor {
  name: string;
  lat: number;
  lng: number;
  type: string;
  distanceMeters: number;
  proximityLevel: "HIGH" | "MEDIUM" | "LOW";
}

export interface MapData {
  center: [number, number];
  locationMode: "current" | "address";
  siteLabel?: string | null;
  dataSource: "google_places";
  status: "available" | "unavailable";
  searchRadiusMeters: number;
  competitors: Competitor[];
  message?: string | null;
}
