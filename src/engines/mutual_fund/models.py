"""Mutual fund analysis data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class FundPerformanceMetrics:
    """Computed performance metrics for a fund."""

    daily_return: Decimal | None = None
    weekly_return: Decimal | None = None
    monthly_return: Decimal | None = None
    quarterly_return: Decimal | None = None
    yearly_return: Decimal | None = None
    cagr_3y: Decimal | None = None
    cagr_5y: Decimal | None = None
    since_inception_return: Decimal | None = None


@dataclass
class FundRiskMetrics:
    """Computed risk metrics for a fund."""

    volatility: Decimal | None = None
    standard_deviation: Decimal | None = None
    max_drawdown: Decimal | None = None
    downside_risk: Decimal | None = None


@dataclass
class FundAnalysis:
    """Complete analysis output for one mutual fund."""

    asset_id: UUID
    symbol: str
    display_name: str
    asset_type: str
    is_shariah: bool
    management_company: str | None
    expense_ratio: Decimal | None
    aum: Decimal | None
    latest_nav: Decimal | None
    latest_nav_date: date | None
    performance: FundPerformanceMetrics = field(default_factory=FundPerformanceMetrics)
    risk: FundRiskMetrics = field(default_factory=FundRiskMetrics)
    ai_score: Decimal | None = None


@dataclass
class FundRanking:
    """Ranked fund entry."""

    rank: int
    asset_id: UUID
    symbol: str
    display_name: str
    ai_score: Decimal | None
    yearly_return: Decimal | None
    volatility: Decimal | None


@dataclass
class FundComparison:
    """Side-by-side fund comparison."""

    funds: list[FundAnalysis]


@dataclass
class SwitchOpportunity:
    """Potential fund switch recommendation."""

    from_asset_id: UUID
    from_symbol: str
    to_asset_id: UUID
    to_symbol: str
    expected_benefit_pct: Decimal
    reason: str
    confidence: Decimal
