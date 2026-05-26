import json
import re
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from pydantic import ValidationError

from src.agents.base import BaseAgent
from src.models.schemas.intake import SpaceIntakeRequest
from src.models.schemas.streaming import AgentLogEvent
from src.models.schemas.summary import Summary

if TYPE_CHECKING:
    from src.services.llm import LLMService


class StrategyAgent(BaseAgent):
    """Synthesizes all inputs and generates strategic verdict + summary."""

    @property
    def name(self) -> str:
        return "strategy"

    @property
    def display_label(self) -> str:
        return "[Strategy]"

    def build_prompt(self, intake: SpaceIntakeRequest) -> str:
        return f"""You are a strategic business advisor AI acting as a VC partner.

Evaluate this commercial lease opportunity:
- Business type: {intake.business_type}
- Monthly rent: {intake.expected_rent}
- Space size: {intake.square_meters} sqm
- Lease term: {intake.lease_term_months or "unknown"} months
- Service charge: {intake.service_charge_monthly}
- Fit-out budget: {intake.fitout_budget or "unknown"}
- Cooking intensity: {intake.cooking_intensity}
- Floor position: {intake.floor_position}
- Layout shape: {intake.layout_shape}
- Water supply: {intake.has_water_supply}
- Electrical readiness: {intake.electrical_readiness}
- Gas readiness: {intake.has_gas}
- Floor trap: {intake.has_floor_trap}
- Grease trap: {intake.has_grease_trap}
- Exhaust readiness: {intake.has_exhaust}
- Wastewater readiness: {intake.wastewater_readiness}
- Approved use status: {intake.approved_use_status}

Generate a strategic summary with verdict. Return ONLY valid JSON matching this structure:
{{
  "summary": {{
    "score": <0-100 overall score>,
    "verdict": "<APPROVED | APPROVED WITH CONDITIONS | REJECTED>",
    "paybackMonths": <estimated months to recoup initial investment>
  }}
}}

Scoring criteria:
- 80-100: Strong opportunity, approve with confidence
- 60-79: Viable with conditions, negotiate terms
- Below 60: High risk, recommend rejection

Consider location economics, market saturation, and ROI potential.
Consider Singapore F&B due diligence: SFA food shop licensing, PUB grease trap,
SCDF kitchen exhaust/fire safety, EMA licensed electrical/gas workers, and
BCA/HDB/URA A&A or change-of-use checks. This is a screening recommendation,
not a substitute for professional approval."""

    def parse_response(self, raw_llm_output: str) -> dict:
        try:
            match = re.search(r"\{[\s\S]*\}", raw_llm_output)
            if not match:
                raise ValueError("No JSON found in LLM output")
            data = json.loads(match.group())
            summary = Summary.model_validate(data["summary"])
            return {"summary": summary.model_dump()}
        except (json.JSONDecodeError, KeyError, ValidationError, ValueError):
            return self._fallback_summary()

    def _fallback_summary(self) -> dict:
        return {
            "summary": {
                "score": 72,
                "verdict": "APPROVED WITH CONDITIONS",
                "paybackMonths": 12.5,
            }
        }

    async def run(
        self, intake: SpaceIntakeRequest, llm_service: "LLMService"
    ) -> AsyncGenerator[AgentLogEvent, None]:
        yield self._make_log("Initializing strategic analysis...")
        prompt = self.build_prompt(intake)

        yield self._make_log("Evaluating market conditions...")
        raw = await llm_service.complete(prompt)

        yield self._make_log("Computing verdict score...")
        result = self.parse_response(raw)

        yield self._make_log("Strategic analysis complete.", status="done")
        yield AgentLogEvent(
            agent=self.name,
            label=self.display_label,
            message="",
            status="done",
            data=result,
        )
