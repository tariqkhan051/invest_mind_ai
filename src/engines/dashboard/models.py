"""Dashboard aggregation models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.domain.entities.recommendation import Recommendation
from src.engines.market_intelligence.models import MarketSummary
from src.services.portfolio_service import PortfolioSummary


@dataclass
class ChartPoint:
    """Single point for dashboard charts."""

    label: str
    value: Decimal


@dataclass
class DashboardCharts:
    """Chart-ready dashboard datasets."""

    allocation: list[ChartPoint] = field(default_factory=list)
    portfolio_growth: list[ChartPoint] = field(default_factory=list)


@dataclass
class ActivityItem:
    """Recent dashboard activity entry."""

    activity_type: str
    title: str
    description: str
    occurred_at: datetime


@dataclass
class DashboardData:
    """Aggregated dashboard payload."""

    portfolio_summary: PortfolioSummary
    market_summary: MarketSummary
    latest_recommendations: list[Recommendation]
    charts: DashboardCharts
    recent_activity: list[ActivityItem]
