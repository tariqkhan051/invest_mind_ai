"""Scheduler API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SchedulerJobResponse(BaseModel):
    """Scheduler job metadata."""

    job_id: str
    name: str
    category: str
    description: str
    schedule: str
    next_run_at: datetime | None
    enabled: bool


class SchedulerJobRunResponse(BaseModel):
    """Scheduler job execution record."""

    id: UUID
    job_id: str
    job_name: str
    category: str
    status: str
    trigger: str
    message: str
    duration_ms: float
    details: dict[str, object] | None = None
    error_message: str | None = None
    started_at: datetime
    finished_at: datetime


class SchedulerHistoryMeta(BaseModel):
    """Pagination metadata for scheduler history."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class SchedulerHistoryResponse(BaseModel):
    """Paginated scheduler execution history."""

    items: list[SchedulerJobRunResponse]
    meta: SchedulerHistoryMeta
