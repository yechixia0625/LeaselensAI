import json
import re
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from pydantic import ValidationError

from src.agents.base import BaseAgent
from src.models.schemas.financial import FinancialModel
from src.models.schemas.intake import SpaceIntakeRequest
from src.models.schemas.streaming import AgentLogEvent

if TYPE_CHECKING:
    from src.services.llm import LLMService


class FinanceAgent(BaseAgent):
    """Analyzes financial viability and generates financial model."""

    @property
    def name(self) -> str:
        return "finance"

    @property
    def display_label(self) -> str:
        return "[Finance]"

    def build_prompt(self, intake: SpaceIntakeRequest) -> str:
        return f"""You are a commercial real estate financial analyst AI.

Analyze the financial viability of this commercial lease:
- Business type: {intake.business_type}
- Monthly rent: {intake.expected_rent}
- Space size: {intake.square_meters} sqm
- Lease term: {intake.lease_term_months or "unknown"} months
- Rent-free period: {intake.rent_free_months} months
- Service charge: {intake.service_charge_monthly} per month
- Other monthly costs: {intake.other_monthly_costs}
- Utilities estimate: {intake.utilities_monthly_estimate or "unknown"}
- Staffing estimate: {intake.staffing_monthly or "unknown"}
- Fit-out budget: {intake.fitout_budget or "unknown"}
- Expected daily customers: {intake.expected_daily_customers or "unknown"}
- Average spend: {intake.average_spend or "unknown"}
- Gross margin: {intake.gross_margin or "unknown"}

Generate a financial model. Return ONLY valid JSON matching this structure:
{{
  "financialModel": {{
    "baseRent": <monthly rent>,
    "expectedTraffic": <daily foot traffic estimate>,
    "conversionRate": <0.0-1.0, expected visitor to customer rate>,
    "averageSpend": <average transaction amount>,
    "grossMargin": <0.0-1.0, gross profit margin>,
    "fixedCostNonRent": <monthly non-rent fixed costs>,
    "initialDecorationCost": <one-time setup/renovation cost>
  }}
}}

Consider industry benchmarks for {intake.business_type} businesses.
When the user supplied a financial assumption above, preserve it instead of overwriting it.
Be realistic with traffic and conversion estimates."""

    def parse_response(self, raw_llm_output: str, intake: SpaceIntakeRequest) -> dict:
        try:
            match = re.search(r"\{[\s\S]*\}", raw_llm_output)
            if not match:
                raise ValueError("No JSON found in LLM output")
            data = json.loads(match.group())
            model = FinancialModel.model_validate(data["financialModel"])
            return {"financialModel": model.model_dump()}
        except (json.JSONDecodeError, KeyError, ValidationError, ValueError):
            return self._fallback_financial(intake)

    def _fallback_financial(self, intake: SpaceIntakeRequest) -> dict:
        return {
            "financialModel": {
                "baseRent": intake.expected_rent,
                "expectedTraffic": 120,
                "conversionRate": 0.08,
                "averageSpend": 35,
                "grossMargin": 0.65,
                "fixedCostNonRent": 2000,
                "initialDecorationCost": 45000,
                "estimateStatus": "fallback",
            }
        }

    async def run(
        self, intake: SpaceIntakeRequest, llm_service: "LLMService"
    ) -> AsyncGenerator[AgentLogEvent, None]:
        yield self._make_log("Loading financial models...")
        prompt = self.build_prompt(intake)

        yield self._make_log("Analyzing revenue potential...")
        raw = await llm_service.complete(prompt)

        yield self._make_log("Computing cost structures...")
        result = self.parse_response(raw, intake)

        yield self._make_log("Financial analysis complete.", status="done")
        yield AgentLogEvent(
            agent=self.name,
            label=self.display_label,
            message="",
            status="done",
            data=result,
        )
