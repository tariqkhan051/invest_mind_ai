"""Integration tests for scheduler service."""

from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.repositories.sqlalchemy.scheduler_job_run_repository import (
    SqlAlchemySchedulerJobRunRepository,
)
from src.services.scheduler_service import SchedulerService


def test_run_job_records_history(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Manual job execution should persist scheduler history."""
    service = SchedulerService(
        job_run_repository=SqlAlchemySchedulerJobRunRepository(db_session),
        settings=test_settings,
        scheduler=None,
    )
    job_run = service.run_job("portfolio_snapshot")
    assert job_run.job_id == "portfolio_snapshot"
    assert job_run.status.value == "success"

    history = service.get_history()
    assert history.total_items >= 1
    assert history.items[0].job_id == "portfolio_snapshot"
