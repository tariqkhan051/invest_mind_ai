"""APScheduler background jobs."""

from __future__ import annotations

from src.collectors.base.models import CollectorRunResult
from src.config.settings import Settings
from src.domain.enums import ReportType
from src.scheduler.executor import job_session
from src.scheduler.job_context import (
    build_learning_service,
    build_portfolio_service,
    build_recommendation_service,
    build_report_service,
)
from src.services.collector_service import CollectorService


def run_nav_import(settings: Settings) -> CollectorRunResult:
    """Scheduled NAV import job."""
    with job_session(settings) as session:
        service = CollectorService(settings, session)
        return service.run_nav_import()


def run_stock_import(settings: Settings) -> CollectorRunResult:
    """Scheduled stock price import job."""
    with job_session(settings) as session:
        service = CollectorService(settings, session)
        return service.run_stock_import()


def run_macro_import(settings: Settings) -> CollectorRunResult:
    """Scheduled macro indicator import job."""
    with job_session(settings) as session:
        service = CollectorService(settings, session)
        return service.run_macro_import()


def run_news_import(settings: Settings) -> CollectorRunResult:
    """Scheduled news import job."""
    with job_session(settings) as session:
        service = CollectorService(settings, session)
        return service.run_news_import()


def run_portfolio_snapshot(settings: Settings) -> dict[str, object]:
    """Generate daily portfolio snapshot."""
    with job_session(settings) as session:
        service = build_portfolio_service(settings, session)
        snapshot = service.generate_snapshot()
        return {
            "portfolio_id": str(snapshot.portfolio_id),
            "snapshot_date": snapshot.snapshot_date.isoformat(),
            "total_value": str(snapshot.total_value),
        }


def run_recommendation_cycle(settings: Settings) -> dict[str, object]:
    """Generate daily AI recommendations."""
    with job_session(settings) as session:
        service = build_recommendation_service(settings, session)
        recommendations = service.run_recommendation_cycle()
        return {"count": len(recommendations)}


def run_learning_evaluation(settings: Settings) -> dict[str, object]:
    """Evaluate pending learning records."""
    with job_session(settings) as session:
        service = build_learning_service(settings, session)
        evaluated = service.evaluate_pending()
        return {"count": len(evaluated)}


def run_daily_report(settings: Settings) -> dict[str, object]:
    """Generate the daily investment report."""
    with job_session(settings) as session:
        service = build_report_service(settings, session)
        report = service.generate(ReportType.DAILY)
        return {"report_id": str(report.id), "report_type": report.report_type.value}


def collector_result_mapper(
    result: CollectorRunResult,
) -> tuple[str, dict[str, object]]:
    """Map collector run result to job message and details."""
    return (
        f"{result.provider} import {result.status.value}",
        {
            "provider": result.provider,
            "status": result.status.value,
            "rows_saved": result.rows_saved,
            "rows_rejected": result.rows_rejected,
            "rows_duplicates": result.rows_duplicates,
        },
    )
