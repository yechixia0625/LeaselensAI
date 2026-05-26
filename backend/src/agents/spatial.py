import json
import re
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from pydantic import ValidationError

from src.agents.base import BaseAgent
from src.models.schemas.intake import SpaceIntakeRequest
from src.models.schemas.spatial import SpatialBlueprint
from src.models.schemas.streaming import AgentLogEvent

if TYPE_CHECKING:
    from src.services.llm import LLMService


class SpatialAgent(BaseAgent):
    """Analyzes spatial layout and generates blueprint + heat zones."""

    @property
    def name(self) -> str:
        return "spatial"

    @property
    def display_label(self) -> str:
        return "[Spatial]"

    def build_prompt(self, intake: SpaceIntakeRequest) -> str:
        return f"""You are a commercial spatial analysis AI.

Analyze this commercial space for a {intake.business_type} use case.
Space size: {intake.square_meters} sqm
Target rent: {intake.expected_rent} per month
Floor position: {intake.floor_position}
Layout shape: {intake.layout_shape}
Cooking intensity: {intake.cooking_intensity}
Water supply: {intake.has_water_supply}
Floor trap: {intake.has_floor_trap}
Grease trap: {intake.has_grease_trap}
Electrical readiness: {intake.electrical_readiness}
Gas readiness: {intake.has_gas}
Exhaust readiness: {intake.has_exhaust}
Wastewater readiness: {intake.wastewater_readiness}
Exhaust route available: {intake.exhaust_route_available}

Generate a 2D spatial blueprint analysis. Return ONLY valid JSON matching this structure:
{{
  "spatialBlueprint": {{
    "aspectRatio": <float, width/height ratio>,
    "elements": [
      {{"type": "door", "x": <0-100>, "y": <0-100>, "w": <size>,
        "h": <size>, "label": "Main Entrance"}},
      {{"type": "window", "x": <0-100>, "y": <0-100>, "w": <size>,
        "h": <size>, "label": "Street Display"}}
    ],
    "heatZones": [
      {{"x": <0-100>, "y": <0-100>, "radius": <size>,
        "intensity": <0.0-1.0>, "type": "high_profit"}},
      {{"x": <0-100>, "y": <0-100>, "radius": <size>, "intensity": <0.0-1.0>, "type": "dead_zone"}}
    ],
    "flowPath": [
      {{"x": <0-100>, "y": <0-100>}},
      {{"x": <0-100>, "y": <0-100>}}
    ],
    "zoneInsights": [
      {{"x": <0-100>, "y": <0-100>, "type": "opportunity",
        "title": "<short tag>", "reason": "<why it matters>"}},
      {{"x": <0-100>, "y": <0-100>, "type": "friction",
        "title": "<short tag>", "reason": "<why it matters>"}}
    ]
  }}
}}

Consider:
- Entrance placement for maximum foot traffic visibility
- Window displays for street-facing sides
- High-profit zones near entrance and windows
- Dead zones in corners and back areas
- Optimal layout for {intake.business_type} operations
- Do not override explicit utility, gas, exhaust, floor-trap, or grease-trap inputs.
- If the photo suggests a mismatch with the user input, describe it as a risk in zoneInsights."""

    def parse_response(self, raw_llm_output: str) -> dict:
        try:
            match = re.search(r"\{[\s\S]*\}", raw_llm_output)
            if not match:
                raise ValueError("No JSON found in LLM output")
            data = json.loads(match.group())
            blueprint = SpatialBlueprint.model_validate(data["spatialBlueprint"])
            return {"spatialBlueprint": blueprint.model_dump()}
        except (json.JSONDecodeError, KeyError, ValidationError, ValueError):
            return self._fallback_blueprint()

    def _fallback_blueprint(self) -> dict:
        return {
            "spatialBlueprint": {
                "aspectRatio": 1.5,
                "elements": [
                    {"type": "door", "x": 0, "y": 40, "w": 5, "h": 20, "label": "Main Entrance"},
                    {"type": "window", "x": 0, "y": 0, "w": 5, "h": 30, "label": "Street Display"},
                ],
                "heatZones": [
                    {"x": 20, "y": 20, "radius": 15, "intensity": 0.9, "type": "high_profit"},
                    {"x": 80, "y": 80, "radius": 20, "intensity": 0.2, "type": "dead_zone"},
                ],
                "flowPath": [{"x": 5, "y": 50}, {"x": 34, "y": 50}, {"x": 62, "y": 28}],
                "zoneInsights": [
                    {
                        "x": 20,
                        "y": 50,
                        "type": "opportunity",
                        "title": "ENTRY CONVERSION",
                        "reason": "Use first-contact visibility for high-margin display.",
                    },
                    {
                        "x": 80,
                        "y": 80,
                        "type": "friction",
                        "title": "LOW EXPOSURE",
                        "reason": "Create a destination or avoid low-turn stock here.",
                    },
                ],
            }
        }

    async def run(
        self, intake: SpaceIntakeRequest, llm_service: "LLMService"
    ) -> AsyncGenerator[AgentLogEvent, None]:
        yield self._make_log("Initializing spatial matrix...")
        prompt = self.build_prompt(intake)

        yield self._make_log("Analyzing floorplan geometry...")
        raw = await llm_service.complete(
            prompt,
            image_bytes=intake.photo_bytes,
            image_content_type=intake.photo_content_type,
        )

        yield self._make_log("Computing heat zones...")
        result = self.parse_response(raw)

        yield self._make_log("Spatial analysis complete.", status="done")
        yield AgentLogEvent(
            agent=self.name,
            label=self.display_label,
            message="",
            status="done",
            data=result,
        )
