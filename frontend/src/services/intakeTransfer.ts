export type Readiness = "yes" | "no" | "unknown";
export type CookingIntensity = "none" | "light" | "full";
export type FloorPosition = "basement" | "ground" | "upper" | "mall" | "unknown";
export type LayoutShape = "regular" | "narrow" | "corner" | "irregular" | "unknown";
export type ApprovedUseStatus = "confirmed" | "needs_change_of_use" | "unknown";

export interface AnalysisIntake {
  businessType: string;
  expectedRent: number;
  squareMeters: number;
  leaseTermMonths: number;
  serviceChargeMonthly: number;
  fitoutBudget: number;
  cookingIntensity: CookingIntensity;
  floorPosition: FloorPosition;
  layoutShape: LayoutShape;
  hasWaterSupply: Readiness;
  hasFloorTrap: Readiness;
  hasGreaseTrap: Readiness;
  electricalReadiness: Readiness;
  hasGas: Readiness;
  hasExhaust: Readiness;
  wastewaterReadiness: Readiness;
  approvedUseStatus: ApprovedUseStatus;
  rentFreeMonths?: number;
  depositMonths?: number;
  otherMonthlyCosts?: number;
  utilitiesMonthlyEstimate?: number;
  staffingMonthly?: number;
  marketingMonthly?: number;
  insuranceMonthly?: number;
  licenseFees?: number;
  reinstatementCost?: number;
  expectedDailyCustomers?: number;
  averageSpend?: number;
  grossMargin?: number;
  frontageWidthM?: number;
  ceilingHeightM?: number;
  usableAreaRatio?: number;
  storageAreaSqm?: number;
  seatingCapacity?: number;
  loadingAccess?: Readiness;
  toiletAccess?: Readiness;
  signageVisibility?: Readiness;
  exhaustRouteAvailable?: Readiness;
  location: SiteLocation;
}

export interface SiteLocation {
  mode: "current" | "address";
  latitude: number;
  longitude: number;
  siteLabel?: string;
}

export interface PendingAnalysis {
  file: File;
  intake: AnalysisIntake;
}

let pendingAnalysis: PendingAnalysis | null = null;

export function storePendingAnalysis(analysis: PendingAnalysis): void {
  pendingAnalysis = analysis;
}

export function getPendingAnalysis(): PendingAnalysis | null {
  return pendingAnalysis;
}
