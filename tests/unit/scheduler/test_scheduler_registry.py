"""Unit tests for scheduler registry and executor."""

from src.scheduler.registry import JOB_DEFINITIONS, get_job_definition


def test_job_registry_contains_core_jobs() -> None:
    """Registry should include market, AI, and learning jobs."""
    expected = {
        "nav_import",
        "stock_import",
        "macro_import",
        "news_import",
        "portfolio_snapshot",
        "recommendation_cycle",
        "learning_evaluation",
        "daily_report",
    }
    assert expected.issubset(set(JOB_DEFINITIONS.keys()))


def test_get_job_definition_returns_metadata() -> None:
    """Job definition lookup should return configured metadata."""
    definition = get_job_definition("portfolio_snapshot")
    assert definition is not None
    assert definition.name == "Portfolio Snapshot"
    assert definition.category == "system"
