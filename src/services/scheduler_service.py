"""Scheduler application service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import ceil

from apscheduler.schedulers.background import BackgroundScheduler

from src.config.settings import Settings
from src.core.exceptions import InvestMindError
from src.core.logging import get_logger
from src.domain.entities.scheduler_job_run import SchedulerJobRun
from src.domain.enums import SchedulerJobStatus, SchedulerJobTrigger
from src.repositories.interfaces.scheduler_job_run_repository import (
    SchedulerJobRunRepository,
)
from src.scheduler.executor import execute_job
from src.scheduler.models import JobDefinition, JobExecutionResult
from src.scheduler.registry import (
    JOB_DEFINITIONS,
    get_job_definition,
    get_result_mapper,
)

logger = get_logger("services.scheduler")


class SchedulerJobNotFoundError(InvestMindError):
    """Raised when a requested scheduler job does not exist."""


@dataclass
class SchedulerJobInfo:
    """Scheduler job metadata exposed via API."""

    job_id: str
    name: str
    category: str
    description: str
    schedule: str
    next_run_at: datetime | None
    enabled: bool


@dataclass
class PaginatedJobHistory:
    """Paginated scheduler execution history."""

    items: list[SchedulerJobRun]
    page: int
    page_size: int
    total_items: int
    total_pages: int


class SchedulerService:
    """Manage scheduler jobs, manual execution, and history."""

    def __init__(
        self,
        job_run_repository: SchedulerJobRunRepository,
        settings: Settings,
        scheduler: BackgroundScheduler | None = None,
    ) -> None:
        self._job_run_repository = job_run_repository
        self._settings = settings
        self._scheduler = scheduler

    def list_jobs(self) -> list[SchedulerJobInfo]:
        """Return configured scheduler jobs and next run times."""
        schedules = self._settings.providers_config.get("schedules", {})
        jobs: list[SchedulerJobInfo] = []
        scheduled_jobs = (
            {job.id: job for job in self._scheduler.get_jobs()}
            if self._scheduler is not None
            else {}
        )
        for definition in JOB_DEFINITIONS.values():
            scheduled = scheduled_jobs.get(definition.job_id)
            jobs.append(
                SchedulerJobInfo(
                    job_id=definition.job_id,
                    name=definition.name,
                    category=definition.category,
                    description=definition.description,
                    schedule=str(
                        schedules.get(definition.schedule_key, definition.default_cron)
                    ),
                    next_run_at=scheduled.next_run_time if scheduled else None,
                    enabled=self._settings.scheduler_enabled,
                )
            )
        return jobs

    def run_job(self, job_id: str) -> SchedulerJobRun:
        """Manually trigger a scheduler job."""
        definition = get_job_definition(job_id)
        if definition is None:
            raise SchedulerJobNotFoundError(f"Scheduler job {job_id} not found.")

        result = execute_job(
            job_id,
            definition.handler,
            self._settings,
            trigger=SchedulerJobTrigger.MANUAL.value,
            result_mapper=get_result_mapper(job_id),
        )
        saved = self.record_execution(definition, result)
        logger.info("job_triggered_manually job_id={} status={}", job_id, result.status)
        return saved

    def record_execution(
        self,
        definition: JobDefinition,
        result: JobExecutionResult,
    ) -> SchedulerJobRun:
        """Persist a job execution result."""
        job_run = SchedulerJobRun(
            job_id=definition.job_id,
            job_name=definition.name,
            category=definition.category,
            status=SchedulerJobStatus(result.status),
            trigger=SchedulerJobTrigger(result.trigger),
            message=result.message,
            duration_ms=result.duration_ms,
            details=result.details or None,
            error_message=result.error_message,
            started_at=result.started_at,
            finished_at=result.finished_at,
        )
        return self._job_run_repository.save(job_run)

    def get_history(
        self,
        page: int = 1,
        page_size: int = 25,
        job_id: str | None = None,
    ) -> PaginatedJobHistory:
        """Return paginated job execution history."""
        total_items = self._job_run_repository.count(job_id=job_id)
        offset = (page - 1) * page_size
        items = self._job_run_repository.list_recent(
            limit=page_size,
            offset=offset,
            job_id=job_id,
        )
        total_pages = ceil(total_items / page_size) if page_size else 0
        return PaginatedJobHistory(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )
