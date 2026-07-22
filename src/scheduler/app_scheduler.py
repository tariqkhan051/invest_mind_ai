"""Application scheduler using APScheduler."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config.settings import Settings
from src.core.logging import get_logger
from src.scheduler.executor import execute_job
from src.scheduler.registry import JOB_DEFINITIONS, get_result_mapper

logger = get_logger("scheduler.app")

_scheduler_instance: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler | None:
    """Return the active scheduler instance if running."""
    return _scheduler_instance


def _scheduled_wrapper(job_id: str, settings: Settings) -> None:
    """Wrapper invoked by APScheduler to run and record a job."""
    from src.database.session import get_session_factory
    from src.repositories.sqlalchemy.scheduler_job_run_repository import (
        SqlAlchemySchedulerJobRunRepository,
    )
    from src.services.scheduler_service import SchedulerService

    definition = JOB_DEFINITIONS[job_id]
    result = execute_job(
        job_id,
        definition.handler,
        settings,
        trigger="scheduled",
        result_mapper=get_result_mapper(job_id),
    )
    session_factory = get_session_factory(settings)
    session = session_factory()
    try:
        service = SchedulerService(
            job_run_repository=SqlAlchemySchedulerJobRunRepository(session),
            settings=settings,
            scheduler=get_scheduler(),
        )
        service.record_execution(definition, result)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_scheduler(settings: Settings) -> BackgroundScheduler:
    """Create and configure the background scheduler."""
    scheduler = BackgroundScheduler(timezone="Asia/Karachi")
    schedules = settings.providers_config.get("schedules", {})

    for job_id, definition in JOB_DEFINITIONS.items():
        cron = str(schedules.get(definition.schedule_key, definition.default_cron))
        scheduler.add_job(
            _scheduled_wrapper,
            trigger=CronTrigger.from_crontab(cron),
            args=[job_id, settings],
            id=job_id,
            replace_existing=True,
        )
    return scheduler


def start_scheduler(settings: Settings) -> BackgroundScheduler | None:
    """Start the scheduler when enabled."""
    global _scheduler_instance
    if not settings.scheduler_enabled or settings.is_testing:
        logger.info("scheduler_disabled environment={}", settings.environment)
        return None

    scheduler = create_scheduler(settings)
    scheduler.start()
    _scheduler_instance = scheduler
    logger.info("scheduler_started jobs={}", [job.id for job in scheduler.get_jobs()])
    return scheduler


def stop_scheduler(scheduler: BackgroundScheduler | None) -> None:
    """Shutdown the scheduler gracefully."""
    global _scheduler_instance
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        _scheduler_instance = None
        logger.info("scheduler_stopped")
