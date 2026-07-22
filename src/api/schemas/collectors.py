"""Collector API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.collectors.base.models import CollectorStatus


class CollectorRunResponse(BaseModel):
    """Collector execution result."""

    provider: str
    status: CollectorStatus
    rows_collected: int
    rows_saved: int
    rows_rejected: int
    rows_duplicates: int
    duration_ms: float
    errors: list[str] = Field(default_factory=list)
    started_at: datetime
    finished_at: datetime | None = None


class CollectorStatusResponse(BaseModel):
    """Collector status snapshot."""

    provider: str
    last_status: CollectorStatus
    last_run_at: datetime | None
    rows_saved: int
    rows_rejected: int
    duration_ms: float
    errors: list[str] = Field(default_factory=list)
    healthy: bool | None = None
