from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from src.api.deps import provide_analysis_service, require_demo_auth
from src.models.schemas.intake import SpaceIntakeRequest
from src.services.analysis import AnalysisService

router = APIRouter(tags=["analysis"])

SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


@router.post("/analyze-space")
async def analyze_space(
    photo: UploadFile = File(...),
    business_type: str = Form(..., min_length=1, max_length=100),
    expected_rent: float = Form(..., gt=0),
    square_meters: float = Form(..., gt=0),
    location_mode: Literal["current", "address"] = Form(...),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    site_label: str | None = Form(None),
    _username: str | None = Depends(require_demo_auth),
    analysis_service: AnalysisService = Depends(provide_analysis_service),
):
    """Analyze a commercial space. Returns SSE stream with agent logs and final report."""
    if photo.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only PNG, JPEG, and WebP space images are supported.",
        )

    photo_bytes = await photo.read()
    if not photo_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(photo_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="The uploaded image exceeds 10 MB.")

    try:
        intake = SpaceIntakeRequest(
            photo_bytes=photo_bytes,
            photo_filename=photo.filename,
            photo_content_type=photo.content_type,
            business_type=business_type,
            expected_rent=expected_rent,
            square_meters=square_meters,
            location_mode=location_mode,
            latitude=latitude,
            longitude=longitude,
            site_label=site_label,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_input=False, include_context=False),
        ) from exc

    async def event_generator():
        async for sse_line in analysis_service.analyze(intake):
            yield sse_line

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
