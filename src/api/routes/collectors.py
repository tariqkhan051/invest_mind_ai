"""Data collection API routes — docs/18_API.md §12."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.dependencies import get_collector_service
from src.api.schemas import ApiResponse
from src.api.schemas.collectors import CollectorRunResponse, CollectorStatusResponse
from src.collectors.base.models import CollectorRunResult
from src.services.collector_service import CollectorService, CollectorStatusSnapshot

router = APIRouter(prefix="/collectors", tags=["Data Collection"])


def _map_run_result(result: CollectorRunResult) -> CollectorRunResponse:
    return CollectorRunResponse(
        provider=result.provider,
        status=result.status,
        rows_collected=result.rows_collected,
        rows_saved=result.rows_saved,
        rows_rejected=result.rows_rejected,
        rows_duplicates=result.rows_duplicates,
        duration_ms=result.duration_ms,
        errors=result.errors,
        started_at=result.started_at,
        finished_at=result.finished_at,
    )


def _map_status(snapshot: CollectorStatusSnapshot) -> CollectorStatusResponse:
    return CollectorStatusResponse(
        provider=snapshot.provider,
        last_status=snapshot.last_status,
        last_run_at=snapshot.last_run_at,
        rows_saved=snapshot.rows_saved,
        rows_rejected=snapshot.rows_rejected,
        duration_ms=snapshot.duration_ms,
        errors=snapshot.errors,
        healthy=snapshot.healthy,
    )


@router.post("/nav", response_model=ApiResponse[CollectorRunResponse])
def trigger_nav_import(
    service: Annotated[CollectorService, Depends(get_collector_service)],
) -> ApiResponse[CollectorRunResponse]:
    """Trigger the MUFAP NAV collector manually."""
    result = service.run_nav_import()
    return ApiResponse(
        message="NAV import completed",
        data=_map_run_result(result),
    )


@router.post("/stocks", response_model=ApiResponse[CollectorRunResponse])
def trigger_stock_import(
    service: Annotated[CollectorService, Depends(get_collector_service)],
) -> ApiResponse[CollectorRunResponse]:
    """Trigger the PSX stock price collector manually."""
    result = service.run_stock_import()
    return ApiResponse(
        message="Stock import completed",
        data=_map_run_result(result),
    )


@router.post("/macro", response_model=ApiResponse[CollectorRunResponse])
def trigger_macro_import(
    service: Annotated[CollectorService, Depends(get_collector_service)],
) -> ApiResponse[CollectorRunResponse]:
    """Trigger the SBP macro indicator collector manually."""
    result = service.run_macro_import()
    return ApiResponse(
        message="Macro import completed",
        data=_map_run_result(result),
    )


@router.post("/news", response_model=ApiResponse[CollectorRunResponse])
def trigger_news_import(
    service: Annotated[CollectorService, Depends(get_collector_service)],
) -> ApiResponse[CollectorRunResponse]:
    """Trigger the news collector manually."""
    result = service.run_news_import()
    return ApiResponse(
        message="News import completed",
        data=_map_run_result(result),
    )


@router.get("/status", response_model=ApiResponse[list[CollectorStatusResponse]])
def get_collector_status(
    service: Annotated[CollectorService, Depends(get_collector_service)],
) -> ApiResponse[list[CollectorStatusResponse]]:
    """Return status for all data collectors."""
    statuses = service.get_status()
    return ApiResponse(
        message="Collector status retrieved",
        data=[_map_status(snapshot) for snapshot in statuses],
    )
