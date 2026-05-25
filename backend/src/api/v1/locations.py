import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import provide_geo_service, require_demo_auth
from src.models.schemas.location import (
    AutocompleteRequest,
    AutocompleteResponse,
    ResolvedLocation,
    ResolveLocationRequest,
)
from src.services.geo import GeoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_location(
    request: AutocompleteRequest,
    _username: str | None = Depends(require_demo_auth),
    geo: GeoService = Depends(provide_geo_service),
) -> AutocompleteResponse:
    try:
        predictions = await geo.autocomplete(request.input, request.sessionToken)
        return AutocompleteResponse(predictions=predictions)
    except (RuntimeError, ValueError, httpx.HTTPError) as exc:
        logger.exception("Autocomplete failed for input=%r", request.input)
        raise HTTPException(status_code=503, detail="Location search is unavailable.") from exc


@router.post("/resolve", response_model=ResolvedLocation)
async def resolve_location(
    request: ResolveLocationRequest,
    _username: str | None = Depends(require_demo_auth),
    geo: GeoService = Depends(provide_geo_service),
) -> ResolvedLocation:
    try:
        return ResolvedLocation(**await geo.resolve(request.placeId, request.sessionToken))
    except (RuntimeError, ValueError, httpx.HTTPError) as exc:
        raise HTTPException(status_code=503, detail="Location resolution is unavailable.") from exc
