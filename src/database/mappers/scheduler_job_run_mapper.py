"""Scheduler job run entity ↔ ORM mapper."""

from __future__ import annotations

from src.database.models.scheduler_job_run import SchedulerJobRunModel
from src.domain.entities.scheduler_job_run import SchedulerJobRun
from src.domain.enums import SchedulerJobStatus, SchedulerJobTrigger


class SchedulerJobRunMapper:
    """Map between SchedulerJobRun entity and ORM model."""

    @staticmethod
    def to_entity(model: SchedulerJobRunModel) -> SchedulerJobRun:
        return SchedulerJobRun(
            id=model.id,
            job_id=model.job_id,
            job_name=model.job_name,
            category=model.category,
            status=SchedulerJobStatus(model.status),
            trigger=SchedulerJobTrigger(model.trigger),
            message=model.message,
            duration_ms=float(model.duration_ms),
            details=model.details,
            error_message=model.error_message,
            started_at=model.started_at,
            finished_at=model.finished_at,
        )

    @staticmethod
    def to_model(entity: SchedulerJobRun) -> SchedulerJobRunModel:
        return SchedulerJobRunModel(
            id=entity.id,
            job_id=entity.job_id,
            job_name=entity.job_name,
            category=entity.category,
            status=entity.status.value,
            trigger=entity.trigger.value,
            message=entity.message,
            duration_ms=entity.duration_ms,
            details=entity.details,
            error_message=entity.error_message,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
        )
