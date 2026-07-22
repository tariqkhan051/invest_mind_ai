"""Dashboard API schemas — docs/18_API.md §11."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.api.schemas.market_intelligence import MarketSummaryResponse
from src.api.schemas.portfolio import PortfolioSummaryResponse
from src.api.schemas.recommendation import RecommendationResponse


class ChartPointResponse(BaseModel):
    """Chart data point."""

    label: str
    value: Decimal


class DashboardChartsResponse(BaseModel):
    """Dashboard chart datasets."""

    allocation: list[ChartPointResponse]
    portfolio_growth: list[ChartPointResponse]


class ActivityItemResponse(BaseModel):
    """Recent dashboard activity item."""

    activity_type: str
    title: str
    description: str
    occurred_at: datetime


class DashboardResponse(BaseModel):
    """Unified dashboard payload."""

    portfolio_summary: PortfolioSummaryResponse
    market_summary: MarketSummaryResponse
    latest_recommendations: list[RecommendationResponse]
    charts: DashboardChartsResponse
    recent_activity: list[ActivityItemResponse] = Field(default_factory=list)
