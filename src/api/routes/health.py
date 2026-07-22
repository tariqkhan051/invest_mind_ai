"""System health, readiness, and version endpoints.

See docs/18_API.md §14.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_app_settings
from src.api.schemas import ApiResponse, HealthData, ReadinessData, VersionData
from src.config.settings import Settings
from src.core.constants import API_VERSION
from src.core.exceptions import DatabaseError
from src.core.logging import get_logger
from src.database.session import check_database_connection

logger = get_logger("api.health")
router = APIRouter(tags=["System"])


@router.get("/health", response_model=ApiResponse[HealthData])
def health_check(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ApiResponse[HealthData]:
    """Return application liveness status."""
    return ApiResponse(
        message="Application is healthy",
        data=HealthData(
            status="healthy",
            environment=settings.environment,
            app_name=settings.app_name,
        ),
    )


@router.get("/ready", response_model=ApiResponse[ReadinessData])
def readiness_check(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ApiResponse[ReadinessData]:
    """Return application readiness including database connectivity."""
    database_status = "ready"
    try:
        check_database_connection(settings)
    except DatabaseError as exc:
        logger.error("readiness_check_failed reason={}", exc.message)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ApiResponse(
                success=False,
                message="Application is not ready",
                data=ReadinessData(
                    status="not_ready",
                    database="unavailable",
                    scheduler="unknown",
                ),
            ).model_dump(),
        ) from exc

    scheduler_status = "enabled" if settings.scheduler_enabled else "disabled"
    return ApiResponse(
        message="Application is ready",
        data=ReadinessData(
            status="ready",
            database=database_status,
            scheduler=scheduler_status,
        ),
    )


@router.get("/version", response_model=ApiResponse[VersionData])
def version_info(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ApiResponse[VersionData]:
    """Return application version metadata."""
    return ApiResponse(
        message="Version information",
        data=VersionData(
            name=settings.app_name,
            version=settings.app_version,
            api_version=API_VERSION,
            environment=settings.environment,
        ),
    )
