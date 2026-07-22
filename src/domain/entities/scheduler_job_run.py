"""Scheduler job execution history entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.enums import SchedulerJobStatus, SchedulerJobTrigger


@dataclass
class SchedulerJobRun:
    """Persisted record of a background job execution."""

    job_id: str
    job_name: str
    category: str
    status: SchedulerJobStatus
    trigger: SchedulerJobTrigger
    message: str
    id: UUID = field(default_factory=uuid4)
    duration_ms: float = 0.0
    details: dict[str, object] | None = None
    error_message: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime = field(default_factory=datetime.utcnow)
