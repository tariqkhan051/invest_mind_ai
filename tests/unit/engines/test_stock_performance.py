"""Unit tests for stock performance calculations."""

from datetime import date, timedelta
from decimal import Decimal

from src.domain.read_models.price_history import PriceHistoryPoint
from src.engines.stock.performance_calculator import calculate_performance


def _build_history(
    days: int,
    start_price: Decimal = Decimal("100"),
) -> list[PriceHistoryPoint]:
    history: list[PriceHistoryPoint] = []
    price = start_price
    start_date = date(2025, 1, 1)
    for offset in range(days):
        history.append(
            PriceHistoryPoint(
                price_date=start_date + timedelta(days=offset),
                close_price=price,
            )
        )
        price *= Decimal("1.001")
    return history


def test_calculate_performance_returns_metrics() -> None:
    """Performance calculator should return period returns for sufficient history."""
    history = _build_history(400)
    metrics = calculate_performance(history)

    assert metrics.daily_return is not None
    assert metrics.monthly_return is not None
    assert metrics.yearly_return is not None
    assert metrics.volatility is not None


def test_calculate_performance_handles_short_history() -> None:
    """Short history should return empty metrics."""
    metrics = calculate_performance(
        [
            PriceHistoryPoint(
                price_date=date(2026, 1, 1),
                close_price=Decimal("100"),
            )
        ]
    )
    assert metrics.yearly_return is None
