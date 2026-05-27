export interface ProfitInput {
  expectedTraffic: number;
  averageSpend: number;
  conversionRate: number;
  demandBasis: "estimated_foot_traffic" | "paying_customers";
  grossMargin: number;
  baseRent: number;
  fixedCostNonRent: number;
}

export interface ProfitResult {
  grossRevenue: number;
  netRevenue: number;
  netProfit: number;
  profitMargin: number;
  isCritical: boolean;
}

/**
 * Core profit formula:
 * A declared paying-customer count is already converted; estimated foot traffic
 * is converted using the supplied conversion rate.
 */
export function calculateProfit(input: ProfitInput): ProfitResult {
  const monthlyTraffic = input.expectedTraffic * 30;
  const payingCustomers =
    input.demandBasis === "paying_customers"
      ? monthlyTraffic
      : monthlyTraffic * input.conversionRate;
  const grossRevenue = payingCustomers * input.averageSpend;
  const netRevenue = grossRevenue * input.grossMargin;
  const netProfit = netRevenue - input.baseRent - input.fixedCostNonRent;

  return {
    grossRevenue,
    netRevenue,
    netProfit,
    profitMargin: grossRevenue > 0 ? netProfit / grossRevenue : 0,
    isCritical: netProfit < 0,
  };
}
