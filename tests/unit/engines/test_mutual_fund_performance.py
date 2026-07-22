"""Unit tests for mutual fund performance calculations."""

from datetime import date, timedelta
from decimal import Decimal

from src.domain.read_models.nav_history import NavHistoryPoint
from src.engines.mutual_fund.performance_calculator import calculate_performance


def _build_history(
    days: int,
    start_nav: Decimal = Decimal("100"),
) -> list[NavHistoryPoint]:
    history: list[NavHistoryPoint] = []
    nav = start_nav
    start_date = date(2025, 1, 1)
    for offset in range(days):
        history.append(
            NavHistoryPoint(
                nav_date=start_date + timedelta(days=offset),
                nav=nav,
            )
        )
        nav *= Decimal("1.001")
    return history


def test_calculate_performance_returns_metrics() -> None:
    """Performance calculator should return period returns for sufficient history."""
    history = _build_history(400)
    metrics = calculate_performance(history)

    assert metrics.daily_return is not None
    assert metrics.monthly_return is not None
    assert metrics.yearly_return is not None
    assert metrics.since_inception_return is not None


def test_calculate_performance_handles_short_history() -> None:
    """Short history should return empty metrics."""
    metrics = calculate_performance(
        [
            NavHistoryPoint(nav_date=date(2026, 1, 1), nav=Decimal("100")),
        ]
    )
    assert metrics.yearly_return is None
