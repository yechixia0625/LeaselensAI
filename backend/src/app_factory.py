from fastapi import FastAPI

from src.api.router import api_router
from src.api.v1 import analyze, auth, locations
from src.config.settings import get_settings
from src.middleware.cors import setup_cors
from src.middleware.error_handler import register_error_handlers


def create_app() -> FastAPI:
    """Application factory for creating the FastAPI app."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url=None,
    )

    setup_cors(app)
    register_error_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(auth.router, prefix="/api")
    app.include_router(analyze.router, prefix="/api")
    app.include_router(locations.router, prefix="/api")

    return app
