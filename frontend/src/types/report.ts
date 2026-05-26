import type { FinancialModel } from "./financial";
import type { MapData } from "./map";
import type { SpatialBlueprint } from "./spatial";

export interface Summary {
  score: number; // 0-100
  verdict: string;
  paybackMonths: number;
  scoreBreakdown?: ScoreBreakdown | null;
}

export interface ScoreEvidence {
  label: string;
  value: string;
  source?: string | null;
}

export interface ScoreComponent {
  key: string;
  label: string;
  score: number;
  maxScore: number;
  rationale: string;
  evidence: ScoreEvidence[];
  assumptionsUsed?: string[];
}

export interface RiskFlag {
  domain: string;
  severity: "critical" | "warning" | "info";
  message: string;
  source?: string | null;
  blocking: boolean;
}

export interface ScoreBreakdown {
  fixedScore: number;
  maxFixedScore: number;
  llmScore: number;
  maxLlmScore: number;
  totalScore: number;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  components: ScoreComponent[];
  riskFlags: RiskFlag[];
}

export interface SourceLink {
  label: string;
  url: string;
}

export interface CandidateLocation {
  name: string;
  address: string;
  country: "Singapore";
  area: string;
  lat: number;
  lng: number;
  score: number;
  rentBenchmark: string;
  estimatedMonthlyRent: number;
  nearbySignals: string[];
  pros: string[];
  cons: string[];
  sourceLinks: SourceLink[];
}

export interface LeaseLensReport {
  summary: Summary;
  spatialBlueprint: SpatialBlueprint;
  financialModel: FinancialModel;
  mapData: MapData;
  recommendedLocations: CandidateLocation[];
}
