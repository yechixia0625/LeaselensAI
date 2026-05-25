
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import Settings, get_settings
from src.pipeline.orchestrator import AnalysisOrchestrator
from src.repositories.analysis import AnalysisRepository
from src.repositories.report import ReportRepository
from src.services.analysis import AnalysisService
from src.services.demo_auth import DemoAuthService
from src.services.geo import GeoService
from src.services.llm import LLMService


async def provide_settings() -> Settings:
    return get_settings()


# Database engine and session factory (lazy init)
_engine = None
_session_factory: async_sessionmaker | None = None


async def provide_db_session(
    settings: Settings = Depends(provide_settings),
) -> AsyncSession:
    global _engine, _session_factory
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
        )
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    async with _session_factory() as session:
        yield session


async def provide_llm_service(
    settings: Settings = Depends(provide_settings),
) -> AsyncGenerator[LLMService, None]:
    llm = LLMService(settings)
    try:
        yield llm
    finally:
        await llm.close()


async def provide_geo_service(
    settings: Settings = Depends(provide_settings),
) -> AsyncGenerator[GeoService, None]:
    geo = GeoService(settings)
    try:
        yield geo
    finally:
        await geo.close()


async def provide_analysis_service(
    llm: LLMService = Depends(provide_llm_service),
    geo: GeoService = Depends(provide_geo_service),
    session: AsyncSession = Depends(provide_db_session),
) -> AnalysisService:
    orchestrator = AnalysisOrchestrator(llm, geo)
    report_repo = ReportRepository(session)
    analysis_repo = AnalysisRepository(session)
    return AnalysisService(orchestrator, report_repo, analysis_repo)


async def provide_demo_auth_service(
    settings: Settings = Depends(provide_settings),
) -> DemoAuthService:
    return DemoAuthService(
        username=settings.demo_auth_username or "",
        password=settings.demo_auth_password or "",
        secret=settings.demo_auth_secret or "",
        cookie_name=settings.demo_auth_cookie_name,
    )


async def require_demo_auth(
    request: Request,
    settings: Settings = Depends(provide_settings),
    auth: DemoAuthService = Depends(provide_demo_auth_service),
) -> str | None:
    if not settings.demo_auth_enabled:
        return None

    cookie_value = request.cookies.get(settings.demo_auth_cookie_name)
    username = auth.read_cookie_value(cookie_value)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return username
