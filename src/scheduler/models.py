"""Scheduler job execution result models."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.config.settings import Settings


@dataclass(frozen=True, slots=True)
class JobDefinition:
    """Metadata for a schedulable background job."""

    job_id: str
    name: str
    category: str
    description: str
    schedule_key: str
    default_cron: str
    handler: Callable[[Settings], Any]


@dataclass
class JobExecutionResult:
    """Outcome of a single job execution."""

    job_id: str
    status: str
    trigger: str
    message: str
    duration_ms: float
    started_at: datetime
    finished_at: datetime
    details: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
