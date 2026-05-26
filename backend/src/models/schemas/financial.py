from pydantic import BaseModel, Field


class FinancialModel(BaseModel):
    baseRent: float
    expectedTraffic: int
    conversionRate: float = Field(ge=0.0, le=1.0)
    averageSpend: float
    grossMargin: float = Field(ge=0.0, le=1.0)
    fixedCostNonRent: float
    initialDecorationCost: float
    effectiveMonthlyRent: float = 0
    totalMonthlyOccupancyCost: float = 0
    monthlyOperatingCost: float = 0
    breakEvenRevenue: float = 0
    setupCapitalRequired: float = 0
    leaseRunwayMonths: float = 0
    paybackMonths: float = 999
