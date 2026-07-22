"""Scheduler API routes — docs/18_API.md §13."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_scheduler_service
from src.api.schemas import ApiResponse
from src.api.schemas.scheduler import (
    SchedulerHistoryMeta,
    SchedulerHistoryResponse,
    SchedulerJobResponse,
    SchedulerJobRunResponse,
)
from src.core.constants import DEFAULT_PAGE_SIZE
from src.domain.entities.scheduler_job_run import SchedulerJobRun
from src.services.scheduler_service import SchedulerJobInfo, SchedulerService

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

SchedulerServiceDep = Annotated[SchedulerService, Depends(get_scheduler_service)]


def _map_job(job: SchedulerJobInfo) -> SchedulerJobResponse:
    return SchedulerJobResponse(
        job_id=job.job_id,
        name=job.name,
        category=job.category,
        description=job.description,
        schedule=job.schedule,
        next_run_at=job.next_run_at,
        enabled=job.enabled,
    )


def _map_run(job_run: SchedulerJobRun) -> SchedulerJobRunResponse:
    return SchedulerJobRunResponse(
        id=job_run.id,
        job_id=job_run.job_id,
        job_name=job_run.job_name,
        category=job_run.category,
        status=job_run.status.value,
        trigger=job_run.trigger.value,
        message=job_run.message,
        duration_ms=job_run.duration_ms,
        details=job_run.details,
        error_message=job_run.error_message,
        started_at=job_run.started_at,
        finished_at=job_run.finished_at,
    )


@router.get("/jobs", response_model=ApiResponse[list[SchedulerJobResponse]])
def list_scheduler_jobs(
    service: SchedulerServiceDep,
) -> ApiResponse[list[SchedulerJobResponse]]:
    """Return configured scheduler jobs."""
    jobs = service.list_jobs()
    return ApiResponse(
        message="Scheduler jobs retrieved",
        data=[_map_job(job) for job in jobs],
    )


@router.post("/jobs/run/{job_id}", response_model=ApiResponse[SchedulerJobRunResponse])
def run_scheduler_job(
    job_id: str,
    service: SchedulerServiceDep,
) -> ApiResponse[SchedulerJobRunResponse]:
    """Manually trigger a scheduler job."""
    job_run = service.run_job(job_id)
    return ApiResponse(
        message="Scheduler job executed",
        data=_map_run(job_run),
    )


@router.get("/history", response_model=ApiResponse[SchedulerHistoryResponse])
def get_scheduler_history(
    service: SchedulerServiceDep,
    job_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
) -> ApiResponse[SchedulerHistoryResponse]:
    """Return paginated scheduler execution history."""
    history = service.get_history(page=page, page_size=page_size, job_id=job_id)
    return ApiResponse(
        message="Scheduler history retrieved",
        data=SchedulerHistoryResponse(
            items=[_map_run(item) for item in history.items],
            meta=SchedulerHistoryMeta(
                page=history.page,
                page_size=history.page_size,
                total_items=history.total_items,
                total_pages=history.total_pages,
            ),
        ),
    )
