"""Mutual fund API schemas — docs/18_API.md §6."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class FundPerformanceResponse(BaseModel):
    """Performance metrics for a fund."""

    daily_return: Decimal | None = None
    weekly_return: Decimal | None = None
    monthly_return: Decimal | None = None
    quarterly_return: Decimal | None = None
    yearly_return: Decimal | None = None
    cagr_3y: Decimal | None = None
    cagr_5y: Decimal | None = None
    since_inception_return: Decimal | None = None


class FundRiskResponse(BaseModel):
    """Risk metrics for a fund."""

    volatility: Decimal | None = None
    standard_deviation: Decimal | None = None
    max_drawdown: Decimal | None = None
    downside_risk: Decimal | None = None


class FundAnalysisResponse(BaseModel):
    """Analyzed mutual fund details."""

    asset_id: UUID
    symbol: str
    display_name: str
    asset_type: str
    is_shariah: bool
    management_company: str | None = None
    expense_ratio: Decimal | None = None
    aum: Decimal | None = None
    latest_nav: Decimal | None = None
    latest_nav_date: date | None = None
    performance: FundPerformanceResponse
    risk: FundRiskResponse
    ai_score: Decimal | None = None


class NavHistoryPointResponse(BaseModel):
    """Single NAV history point."""

    nav_date: date
    nav: Decimal
    daily_return: Decimal | None = None


class FundRankingResponse(BaseModel):
    """Ranked fund entry."""

    rank: int
    asset_id: UUID
    symbol: str
    display_name: str
    ai_score: Decimal | None = None
    yearly_return: Decimal | None = None
    volatility: Decimal | None = None


class FundComparisonResponse(BaseModel):
    """Side-by-side fund comparison."""

    funds: list[FundAnalysisResponse]


class CompareFundsRequest(BaseModel):
    """Request body for fund comparison."""

    fund_ids: list[UUID] = Field(min_length=1)


class SwitchOpportunityResponse(BaseModel):
    """Potential fund switch recommendation."""

    from_asset_id: UUID
    from_symbol: str
    to_asset_id: UUID
    to_symbol: str
    expected_benefit_pct: Decimal
    reason: str
    confidence: Decimal


class FundCategoryResponse(BaseModel):
    """Category-level fund summary."""

    category: str
    fund_count: int
    average_yearly_return: float | None = None
    average_volatility: float | None = None
    top_performer: str | None = None
