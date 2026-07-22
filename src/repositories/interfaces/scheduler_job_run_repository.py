"""Scheduler job run repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.scheduler_job_run import SchedulerJobRun


class SchedulerJobRunRepository(ABC):
    """Persistence contract for scheduler execution history."""

    @abstractmethod
    def save(self, job_run: SchedulerJobRun) -> SchedulerJobRun:
        """Persist a job run record."""

    @abstractmethod
    def get_by_id(self, run_id: UUID) -> SchedulerJobRun | None:
        """Load a job run by id."""

    @abstractmethod
    def list_recent(
        self,
        limit: int = 50,
        offset: int = 0,
        job_id: str | None = None,
    ) -> list[SchedulerJobRun]:
        """Return recent job runs, optionally filtered by job id."""

    @abstractmethod
    def count(self, job_id: str | None = None) -> int:
        """Return total job run count."""
