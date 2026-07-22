"""Stock performance calculations from price history."""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal

from src.domain.read_models.price_history import PriceHistoryPoint
from src.engines.stock.models import StockPerformanceMetrics

TRADING_DAYS_PER_YEAR = Decimal("252")


def calculate_performance(
    history: list[PriceHistoryPoint],
    as_of: date | None = None,
) -> StockPerformanceMetrics:
    """Calculate stock performance metrics from price history."""
    if len(history) < 2:
        return StockPerformanceMetrics()

    sorted_history = sorted(history, key=lambda point: point.price_date)
    as_of = as_of or sorted_history[-1].price_date

    return StockPerformanceMetrics(
        daily_return=_period_return(sorted_history, as_of, days=1),
        weekly_return=_period_return(sorted_history, as_of, days=7),
        monthly_return=_period_return(sorted_history, as_of, days=30),
        quarterly_return=_period_return(sorted_history, as_of, days=90),
        yearly_return=_period_return(sorted_history, as_of, days=365),
        cagr_3y=_cagr(sorted_history, as_of, years=3),
        volatility=_annualized_volatility(sorted_history),
        max_drawdown=_max_drawdown(sorted_history),
    )


def _period_return(
    history: list[PriceHistoryPoint],
    as_of: date,
    days: int,
) -> Decimal | None:
    start_date = as_of - timedelta(days=days)
    start_point = _find_on_or_before(history, start_date)
    end_point = _find_on_or_before(history, as_of)
    if start_point is None or end_point is None:
        return None
    return _total_return(start_point.close_price, end_point.close_price)


def _cagr(
    history: list[PriceHistoryPoint],
    as_of: date,
    years: int,
) -> Decimal | None:
    start_date = as_of - timedelta(days=years * 365)
    start_point = _find_on_or_before(history, start_date)
    end_point = _find_on_or_before(history, as_of)
    if start_point is None or end_point is None:
        return None
    if start_point.close_price <= Decimal("0"):
        return None
    days = (end_point.price_date - start_point.price_date).days
    if days <= 0:
        return None
    growth = end_point.close_price / start_point.close_price
    exponent = Decimal("365") / Decimal(days)
    return (growth**exponent - Decimal("1")) * Decimal("100")


def _total_return(start_price: Decimal, end_price: Decimal) -> Decimal | None:
    if start_price <= Decimal("0"):
        return None
    return ((end_price / start_price) - Decimal("1")) * Decimal("100")


def _find_on_or_before(
    history: list[PriceHistoryPoint],
    target_date: date,
) -> PriceHistoryPoint | None:
    candidates = [point for point in history if point.price_date <= target_date]
    if not candidates:
        return None
    return max(candidates, key=lambda point: point.price_date)


def _daily_returns(history: list[PriceHistoryPoint]) -> list[Decimal]:
    sorted_history = sorted(history, key=lambda point: point.price_date)
    returns: list[Decimal] = []
    for index in range(1, len(sorted_history)):
        previous = sorted_history[index - 1].close_price
        current = sorted_history[index].close_price
        if previous > Decimal("0"):
            returns.append((current / previous) - Decimal("1"))
    return returns


def _annualized_volatility(history: list[PriceHistoryPoint]) -> Decimal | None:
    returns = _daily_returns(history)
    if len(returns) < 2:
        return None
    mean = sum(returns, Decimal("0")) / Decimal(len(returns))
    variance = sum((value - mean) ** 2 for value in returns) / Decimal(len(returns))
    std_dev = Decimal(str(math.sqrt(float(variance))))
    return std_dev * (TRADING_DAYS_PER_YEAR ** Decimal("0.5")) * Decimal("100")


def _max_drawdown(history: list[PriceHistoryPoint]) -> Decimal | None:
    sorted_history = sorted(history, key=lambda point: point.price_date)
    peak = sorted_history[0].close_price
    max_drawdown = Decimal("0")
    for point in sorted_history:
        if point.close_price > peak:
            peak = point.close_price
        if peak > Decimal("0"):
            drawdown = (peak - point.close_price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
    return max_drawdown * Decimal("100")
