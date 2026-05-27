import math

import httpx

from src.config.settings import Settings
from src.models.schemas.intake import SpaceIntakeRequest


class GeoService:
    """Server-side Google Places client for verified site and market data."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self._api_key = settings.google_places_api_key
        self._radius = settings.google_places_search_radius_meters
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url="https://places.googleapis.com/v1",
            timeout=15,
        )

    def _headers(self, field_mask: str | None = None) -> dict[str, str]:
        if not self._api_key or self._uses_placeholder_key():
            raise RuntimeError("Google Places API is not configured.")
        headers = {
            "X-Goog-Api-Key": self._api_key,
            "Content-Type": "application/json",
        }
        if field_mask:
            headers["X-Goog-FieldMask"] = field_mask
        return headers

    async def autocomplete(self, value: str, session_token: str) -> list[dict[str, str]]:
        response = await self._client.post(
            "https://places.googleapis.com/v1/places:autocomplete",
            headers=self._headers(
                "suggestions.placePrediction.placeId,suggestions.placePrediction.text.text"
            ),
            json={"input": value, "sessionToken": session_token},
        )
        response.raise_for_status()
        predictions: list[dict[str, str]] = []
        for suggestion in response.json().get("suggestions", []):
            prediction = suggestion.get("placePrediction", {})
            place_id = prediction.get("placeId")
            text = prediction.get("text", {}).get("text")
            if place_id and text:
                predictions.append({"placeId": place_id, "text": text})
        return predictions

    async def resolve(self, place_id: str, session_token: str) -> dict[str, str | float]:
        response = await self._client.get(
            f"https://places.googleapis.com/v1/places/{place_id}",
            headers=self._headers("formattedAddress,location"),
            params={"sessionToken": session_token},
        )
        response.raise_for_status()
        place = response.json()
        location = place["location"]
        return {
            "siteLabel": place["formattedAddress"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
        }

    async def nearby_map_data(self, intake: SpaceIntakeRequest) -> dict:
        response = await self._client.post(
            "https://places.googleapis.com/v1/places:searchNearby",
            headers=self._headers("places.displayName,places.location,places.primaryType"),
            json={
                "includedTypes": self._included_types(intake.business_type),
                "maxResultCount": 10,
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": intake.latitude,
                            "longitude": intake.longitude,
                        },
                        "radius": float(self._radius),
                    }
                },
            },
        )
        response.raise_for_status()
        competitors = []
        for place in response.json().get("places", []):
            location = place.get("location", {})
            lat = location.get("latitude")
            lng = location.get("longitude")
            name = place.get("displayName", {}).get("text")
            if lat is None or lng is None or not name:
                continue
            distance = round(self._distance_meters(intake.latitude, intake.longitude, lat, lng))
            competitors.append(
                {
                    "name": name,
                    "lat": lat,
                    "lng": lng,
                    "type": place.get("primaryType", "business"),
                    "distanceMeters": distance,
                    "proximityLevel": self._proximity_level(distance),
                }
            )
        return {
            "center": [intake.latitude, intake.longitude],
            "locationMode": intake.location_mode,
            "siteLabel": intake.site_label,
            "dataSource": "google_places",
            "status": "available",
            "searchRadiusMeters": self._radius,
            "competitors": competitors,
        }

    @staticmethod
    def _included_types(business_type: str) -> list[str]:
        normalized = business_type.strip().lower()
        mappings = {
            "cafe": "cafe",
            "coffee": "cafe",
            "coffee shop": "cafe",
            "bakery": "bakery",
            "restaurant": "restaurant",
            "bar": "bar",
            "bookstore": "book_store",
            "boutique": "clothing_store",
        }
        return [mappings.get(normalized, "store")]

    @staticmethod
    def _distance_meters(lat_a: float, lng_a: float, lat_b: float, lng_b: float) -> float:
        radius = 6_371_000
        phi_a = math.radians(lat_a)
        phi_b = math.radians(lat_b)
        delta_phi = math.radians(lat_b - lat_a)
        delta_lng = math.radians(lng_b - lng_a)
        value = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi_a) * math.cos(phi_b) * math.sin(delta_lng / 2) ** 2
        )
        return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))

    @staticmethod
    def _proximity_level(distance_meters: int) -> str:
        if distance_meters <= 200:
            return "HIGH"
        if distance_meters <= 350:
            return "MEDIUM"
        return "LOW"

    def _uses_placeholder_key(self) -> bool:
        normalized = self._api_key.strip().lower()
        return normalized.startswith(("replace-with", "your-")) or normalized in {
            "changeme",
            "placeholder",
        }

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()
