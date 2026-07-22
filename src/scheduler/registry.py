"""Scheduler job registry."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.domain.enums import SchedulerJobCategory
from src.scheduler.jobs import (
    collector_result_mapper,
    run_daily_report,
    run_learning_evaluation,
    run_macro_import,
    run_nav_import,
    run_news_import,
    run_portfolio_snapshot,
    run_recommendation_cycle,
    run_stock_import,
)
from src.scheduler.models import JobDefinition

JOB_DEFINITIONS: dict[str, JobDefinition] = {
    "nav_import": JobDefinition(
        job_id="nav_import",
        name="NAV Import",
        category=SchedulerJobCategory.MARKET.value,
        description="Import daily mutual fund NAV data from MUFAP.",
        schedule_key="nav_import",
        default_cron="0 18 * * *",
        handler=run_nav_import,
    ),
    "stock_import": JobDefinition(
        job_id="stock_import",
        name="Stock Import",
        category=SchedulerJobCategory.MARKET.value,
        description="Import PSX stock prices during market hours.",
        schedule_key="stock_import",
        default_cron="*/15 9-15 * * 1-5",
        handler=run_stock_import,
    ),
    "macro_import": JobDefinition(
        job_id="macro_import",
        name="Macro Import",
        category=SchedulerJobCategory.MARKET.value,
        description="Import SBP macroeconomic indicators.",
        schedule_key="macro_import",
        default_cron="0 8 * * *",
        handler=run_macro_import,
    ),
    "news_import": JobDefinition(
        job_id="news_import",
        name="News Import",
        category=SchedulerJobCategory.MARKET.value,
        description="Import and classify market news articles.",
        schedule_key="news_import",
        default_cron="*/10 * * * *",
        handler=run_news_import,
    ),
    "portfolio_snapshot": JobDefinition(
        job_id="portfolio_snapshot",
        name="Portfolio Snapshot",
        category=SchedulerJobCategory.SYSTEM.value,
        description="Capture daily portfolio valuation snapshot.",
        schedule_key="portfolio_snapshot",
        default_cron="0 19 * * *",
        handler=run_portfolio_snapshot,
    ),
    "recommendation_cycle": JobDefinition(
        job_id="recommendation_cycle",
        name="Recommendation Cycle",
        category=SchedulerJobCategory.AI.value,
        description="Generate daily AI investment recommendations.",
        schedule_key="recommendation_cycle",
        default_cron="0 20 * * *",
        handler=run_recommendation_cycle,
    ),
    "learning_evaluation": JobDefinition(
        job_id="learning_evaluation",
        name="Learning Evaluation",
        category=SchedulerJobCategory.LEARNING.value,
        description="Evaluate pending recommendation outcomes.",
        schedule_key="learning_evaluation",
        default_cron="0 21 * * *",
        handler=run_learning_evaluation,
    ),
    "daily_report": JobDefinition(
        job_id="daily_report",
        name="Daily Report",
        category=SchedulerJobCategory.SYSTEM.value,
        description="Generate the daily investment report.",
        schedule_key="daily_report",
        default_cron="0 22 * * *",
        handler=run_daily_report,
    ),
}

COLLECTOR_JOBS = {"nav_import", "stock_import", "macro_import", "news_import"}


def get_job_definition(job_id: str) -> JobDefinition | None:
    """Return job definition by id."""
    return JOB_DEFINITIONS.get(job_id)


def get_result_mapper(
    job_id: str,
) -> Callable[[Any], tuple[str, dict[str, object]]] | None:
    """Return optional result mapper for a job."""
    if job_id in COLLECTOR_JOBS:
        return collector_result_mapper
    if job_id == "portfolio_snapshot":

        def _map_portfolio(result: dict[str, object]) -> tuple[str, dict[str, object]]:
            return ("Portfolio snapshot generated", result)

        return _map_portfolio
    if job_id == "recommendation_cycle":

        def _map_recommendations(
            result: dict[str, object],
        ) -> tuple[str, dict[str, object]]:
            count = result.get("count", 0)
            return (f"Generated {count} recommendations", result)

        return _map_recommendations
    if job_id == "learning_evaluation":

        def _map_learning(result: dict[str, object]) -> tuple[str, dict[str, object]]:
            count = result.get("count", 0)
            return (f"Evaluated {count} learning records", result)

        return _map_learning
    if job_id == "daily_report":

        def _map_report(result: dict[str, object]) -> tuple[str, dict[str, object]]:
            return ("Daily report generated", result)

        return _map_report
    return None
