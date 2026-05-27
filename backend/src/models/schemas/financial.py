from typing import Literal

from pydantic import BaseModel, Field


class FinancialModel(BaseModel):
    baseRent: float
    expectedTraffic: int
    conversionRate: float = Field(ge=0.0, le=1.0)
    demandBasis: Literal["estimated_foot_traffic", "paying_customers"] = "estimated_foot_traffic"
    estimateStatus: Literal["user_inputs", "benchmark", "fallback"] = "benchmark"
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
