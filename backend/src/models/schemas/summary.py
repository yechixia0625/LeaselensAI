from typing import Literal

from pydantic import BaseModel, Field


class ScoreEvidence(BaseModel):
    label: str
    value: str
    source: str | None = None


class ScoreComponent(BaseModel):
    key: str
    label: str
    score: float = Field(ge=0)
    maxScore: int = Field(gt=0)
    rationale: str
    evidence: list[ScoreEvidence] = Field(default_factory=list)
    assumptionsUsed: list[str] = Field(default_factory=list)


class RiskFlag(BaseModel):
    domain: str
    severity: Literal["critical", "warning", "info"]
    message: str
    source: str | None = None
    blocking: bool = False


class ScoreBreakdown(BaseModel):
    fixedScore: int = Field(ge=0, le=60)
    maxFixedScore: int = 60
    llmScore: int = Field(ge=0, le=40)
    maxLlmScore: int = 40
    totalScore: int = Field(ge=0, le=100)
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    components: list[ScoreComponent]
    riskFlags: list[RiskFlag] = Field(default_factory=list)


class Summary(BaseModel):
    score: int = Field(ge=0, le=100)
    verdict: str
    paybackMonths: float
    scoreBreakdown: ScoreBreakdown | None = None
