"""Mutual fund risk calculations."""

from __future__ import annotations

import math
from decimal import Decimal

from src.domain.read_models.nav_history import NavHistoryPoint
from src.engines.mutual_fund.models import FundRiskMetrics
from src.engines.mutual_fund.performance_calculator import (
    TRADING_DAYS_PER_YEAR,
    compute_daily_returns,
)


def calculate_risk(history: list[NavHistoryPoint]) -> FundRiskMetrics:
    """Calculate risk metrics from NAV history."""
    if len(history) < 2:
        return FundRiskMetrics()

    daily_returns = compute_daily_returns(history)
    if not daily_returns:
        return FundRiskMetrics()

    std_dev = _standard_deviation(daily_returns)
    annualized_vol = std_dev * (TRADING_DAYS_PER_YEAR ** Decimal("0.5"))
    downside = _downside_deviation(daily_returns)

    return FundRiskMetrics(
        volatility=annualized_vol * Decimal("100"),
        standard_deviation=std_dev * Decimal("100"),
        max_drawdown=_max_drawdown(history),
        downside_risk=downside * Decimal("100"),
    )


def _standard_deviation(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0")
    mean = sum(values, Decimal("0")) / Decimal(len(values))
    variance = sum((value - mean) ** 2 for value in values) / Decimal(len(values))
    return Decimal(str(math.sqrt(float(variance))))


def _downside_deviation(values: list[Decimal]) -> Decimal:
    negative = [value for value in values if value < Decimal("0")]
    if not negative:
        return Decimal("0")
    return _standard_deviation(negative)


def _max_drawdown(history: list[NavHistoryPoint]) -> Decimal | None:
    sorted_history = sorted(history, key=lambda point: point.nav_date)
    peak = sorted_history[0].nav
    max_drawdown = Decimal("0")
    for point in sorted_history:
        if point.nav > peak:
            peak = point.nav
        if peak > Decimal("0"):
            drawdown = (peak - point.nav) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
    return max_drawdown * Decimal("100")
