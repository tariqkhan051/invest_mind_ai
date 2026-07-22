"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.middleware import register_exception_handlers, register_middleware
from src.api.routes import (
    collectors_router,
    health_router,
    market_intelligence_router,
    mutual_fund_router,
    portfolio_router,
    recommendation_router,
    stock_router,
)
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.learning import router as learning_router
from src.api.routes.notification import router as notification_router
from src.api.routes.report import router as report_router
from src.api.routes.scheduler import router as scheduler_router
from src.config.settings import Settings, get_settings
from src.core.logging import get_logger, setup_logging
from src.database.session import init_database
from src.scheduler import start_scheduler, stop_scheduler

logger = get_logger("api.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    setup_logging(settings)
    logger.info(
        "application_starting name={} version={} environment={}",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )

    init_database(settings)
    logger.info("database_initialized url={}", settings.database_url.split("@")[-1])

    app.state.scheduler = start_scheduler(settings)

    yield

    stop_scheduler(getattr(app.state, "scheduler", None))
    logger.info("application_shutdown")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app_settings = settings or get_settings()

    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        description=(
            "AI-powered Shariah-compliant investment advisor for Pakistani investors."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    register_middleware(app, app_settings)
    register_exception_handlers(app)

    app.include_router(health_router, prefix=app_settings.api_prefix)
    app.include_router(portfolio_router, prefix=app_settings.api_prefix)
    app.include_router(mutual_fund_router, prefix=app_settings.api_prefix)
    app.include_router(stock_router, prefix=app_settings.api_prefix)
    app.include_router(market_intelligence_router, prefix=app_settings.api_prefix)
    app.include_router(recommendation_router, prefix=app_settings.api_prefix)
    app.include_router(learning_router, prefix=app_settings.api_prefix)
    app.include_router(scheduler_router, prefix=app_settings.api_prefix)
    app.include_router(report_router, prefix=app_settings.api_prefix)
    app.include_router(dashboard_router, prefix=app_settings.api_prefix)
    app.include_router(notification_router, prefix=app_settings.api_prefix)
    app.include_router(collectors_router, prefix=app_settings.api_prefix)

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        """Root redirect information."""
        return {
            "message": f"{app_settings.app_name} API",
            "docs": "/docs",
            "health": f"{app_settings.api_prefix}/health",
        }

    return app
