"""SQLAlchemy scheduler job run repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.mappers.scheduler_job_run_mapper import SchedulerJobRunMapper
from src.database.models.scheduler_job_run import SchedulerJobRunModel
from src.domain.entities.scheduler_job_run import SchedulerJobRun
from src.repositories.interfaces.scheduler_job_run_repository import (
    SchedulerJobRunRepository,
)


class SqlAlchemySchedulerJobRunRepository(SchedulerJobRunRepository):
    """Persist and query scheduler job execution history."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, job_run: SchedulerJobRun) -> SchedulerJobRun:
        model = SchedulerJobRunMapper.to_model(job_run)
        self._session.add(model)
        self._session.flush()
        return SchedulerJobRunMapper.to_entity(model)

    def get_by_id(self, run_id: UUID) -> SchedulerJobRun | None:
        model = self._session.get(SchedulerJobRunModel, run_id)
        return SchedulerJobRunMapper.to_entity(model) if model else None

    def list_recent(
        self,
        limit: int = 50,
        offset: int = 0,
        job_id: str | None = None,
    ) -> list[SchedulerJobRun]:
        stmt = select(SchedulerJobRunModel).order_by(
            SchedulerJobRunModel.started_at.desc()
        )
        if job_id is not None:
            stmt = stmt.where(SchedulerJobRunModel.job_id == job_id)
        stmt = stmt.offset(offset).limit(limit)
        return [
            SchedulerJobRunMapper.to_entity(row) for row in self._session.scalars(stmt)
        ]

    def count(self, job_id: str | None = None) -> int:
        stmt = select(func.count()).select_from(SchedulerJobRunModel)
        if job_id is not None:
            stmt = stmt.where(SchedulerJobRunModel.job_id == job_id)
        return int(self._session.scalar(stmt) or 0)
