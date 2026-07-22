"""Scheduler job execution helpers."""

from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from time import perf_counter
from typing import TypeVar

from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.core.logging import get_logger
from src.database.session import get_session_factory
from src.scheduler.models import JobExecutionResult

logger = get_logger("scheduler.executor")

T = TypeVar("T")


@contextmanager
def job_session(settings: Settings) -> Generator[Session]:
    """Provide a database session for scheduler jobs."""
    session_factory = get_session_factory(settings)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def execute_job[T](
    job_id: str,
    handler: Callable[[Settings], T],
    settings: Settings,
    *,
    trigger: str = "scheduled",
    result_mapper: Callable[[T], tuple[str, dict[str, object]]] | None = None,
) -> JobExecutionResult:
    """Execute a job handler and capture timing and outcome."""
    started_at = datetime.now(UTC)
    start = perf_counter()
    try:
        outcome = handler(settings)
        duration_ms = (perf_counter() - start) * 1000
        message = f"Job {job_id} completed"
        details: dict[str, object] = {}
        if result_mapper is not None:
            message, details = result_mapper(outcome)
        logger.info(
            "job_completed job_id={} trigger={} duration_ms={:.2f}",
            job_id,
            trigger,
            duration_ms,
        )
        return JobExecutionResult(
            job_id=job_id,
            status="success",
            trigger=trigger,
            message=message,
            duration_ms=duration_ms,
            started_at=started_at,
            finished_at=datetime.now(UTC),
            details=details,
        )
    except Exception as exc:
        duration_ms = (perf_counter() - start) * 1000
        logger.exception("job_failed job_id={} trigger={}", job_id, trigger)
        return JobExecutionResult(
            job_id=job_id,
            status="failed",
            trigger=trigger,
            message=f"Job {job_id} failed",
            duration_ms=duration_ms,
            started_at=started_at,
            finished_at=datetime.now(UTC),
            error_message=str(exc),
        )
