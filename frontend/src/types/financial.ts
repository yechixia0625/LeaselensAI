export interface FinancialModel {
  baseRent: number;
  expectedTraffic: number;
  conversionRate: number;
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
