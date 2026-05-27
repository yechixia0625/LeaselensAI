from typing import Literal

from pydantic import BaseModel, Field


class Competitor(BaseModel):
    name: str
    lat: float
    lng: float
    type: str
    distanceMeters: int
    proximityLevel: str = Field(..., pattern="^(HIGH|MEDIUM|LOW)$")


class MapData(BaseModel):
    center: tuple[float, float]
    locationMode: Literal["current", "address"]
    siteLabel: str | None = None
    dataSource: Literal["google_places"]
    status: Literal["available", "unavailable"]
    searchRadiusMeters: int
    competitors: list[Competitor]
    message: str | None = None
