"""Mutual fund performance calculations."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from src.domain.read_models.nav_history import NavHistoryPoint
from src.engines.mutual_fund.models import FundPerformanceMetrics

TRADING_DAYS_PER_YEAR = Decimal("252")


def calculate_performance(
    history: list[NavHistoryPoint],
    as_of: date | None = None,
) -> FundPerformanceMetrics:
    """Calculate fund performance metrics from NAV history."""
    if not history:
        return FundPerformanceMetrics()

    sorted_history = sorted(history, key=lambda point: point.nav_date)
    as_of = as_of or sorted_history[-1].nav_date
    latest = sorted_history[-1]
    latest_nav = latest.nav

    if len(sorted_history) < 2:
        return FundPerformanceMetrics(
            monthly_return=latest.mtd_return,
            yearly_return=latest.fytd_return,
        )

    yearly = _period_return(sorted_history, as_of, days=365)
    monthly = _period_return(sorted_history, as_of, days=30)
    return FundPerformanceMetrics(
        daily_return=_period_return(sorted_history, as_of, days=1),
        weekly_return=_period_return(sorted_history, as_of, days=7),
        monthly_return=monthly if monthly is not None else latest.mtd_return,
        quarterly_return=_period_return(sorted_history, as_of, days=90),
        yearly_return=yearly if yearly is not None else latest.fytd_return,
        cagr_3y=_cagr(sorted_history, as_of, years=3),
        cagr_5y=_cagr(sorted_history, as_of, years=5),
        since_inception_return=_total_return(sorted_history[0].nav, latest_nav),
    )


def _period_return(
    history: list[NavHistoryPoint],
    as_of: date,
    days: int,
) -> Decimal | None:
    start_date = as_of - timedelta(days=days)
    start_point = _find_on_or_before(history, start_date)
    end_point = _find_on_or_before(history, as_of)
    if start_point is None or end_point is None:
        return None
    return _total_return(start_point.nav, end_point.nav)


def _cagr(
    history: list[NavHistoryPoint],
    as_of: date,
    years: int,
) -> Decimal | None:
    start_date = as_of - timedelta(days=years * 365)
    start_point = _find_on_or_before(history, start_date)
    end_point = _find_on_or_before(history, as_of)
    if start_point is None or end_point is None:
        return None
    if start_point.nav <= Decimal("0"):
        return None
    days = (end_point.nav_date - start_point.nav_date).days
    if days <= 0:
        return None
    growth = end_point.nav / start_point.nav
    exponent = Decimal("365") / Decimal(days)
    cagr = growth**exponent - Decimal("1")
    return cagr * Decimal("100")


def _total_return(start_nav: Decimal, end_nav: Decimal) -> Decimal | None:
    if start_nav <= Decimal("0"):
        return None
    return ((end_nav / start_nav) - Decimal("1")) * Decimal("100")


def _find_on_or_before(
    history: list[NavHistoryPoint],
    target_date: date,
) -> NavHistoryPoint | None:
    candidates = [point for point in history if point.nav_date <= target_date]
    if not candidates:
        return None
    return max(candidates, key=lambda point: point.nav_date)


def compute_daily_returns(history: list[NavHistoryPoint]) -> list[Decimal]:
    """Compute daily return series from NAV history."""
    sorted_history = sorted(history, key=lambda point: point.nav_date)
    returns: list[Decimal] = []
    for index in range(1, len(sorted_history)):
        previous = sorted_history[index - 1].nav
        current = sorted_history[index].nav
        if previous > Decimal("0"):
            returns.append((current / previous) - Decimal("1"))
    return returns
