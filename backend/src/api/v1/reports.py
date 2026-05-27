from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import provide_db_session, require_demo_auth
from src.repositories.report import ReportRepository

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    _username: str | None = Depends(require_demo_auth),
    session: AsyncSession = Depends(provide_db_session),
):
    """Retrieve a saved report by ID."""
    repo = ReportRepository(session)
    report = await repo.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.report_json
