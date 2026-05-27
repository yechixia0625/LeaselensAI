export interface FinancialModel {
  baseRent: number;
  expectedTraffic: number;
  conversionRate: number;
  demandBasis: "estimated_foot_traffic" | "paying_customers";
  estimateStatus: "user_inputs" | "benchmark" | "fallback";
  averageSpend: number;
  grossMargin: number;
  fixedCostNonRent: number;
  initialDecorationCost: number;
  effectiveMonthlyRent: number;
  totalMonthlyOccupancyCost: number;
  monthlyOperatingCost: number;
  breakEvenRevenue: number;
  setupCapitalRequired: number;
  leaseRunwayMonths: number;
  paybackMonths: number;
}
