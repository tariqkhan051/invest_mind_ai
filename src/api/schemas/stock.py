"""Stock API schemas — docs/18_API.md §7."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class StockPerformanceResponse(BaseModel):
    """Performance metrics for a stock."""

    daily_return: Decimal | None = None
    weekly_return: Decimal | None = None
    monthly_return: Decimal | None = None
    quarterly_return: Decimal | None = None
    yearly_return: Decimal | None = None
    cagr_3y: Decimal | None = None
    volatility: Decimal | None = None
    max_drawdown: Decimal | None = None


class TechnicalIndicatorsResponse(BaseModel):
    """Technical indicator snapshot."""

    sma_20: Decimal | None = None
    sma_50: Decimal | None = None
    ema_12: Decimal | None = None
    rsi_14: Decimal | None = None
    momentum: Decimal | None = None
    volume_trend: Decimal | None = None


class FundamentalMetricsResponse(BaseModel):
    """Fundamental ratio snapshot."""

    eps: Decimal | None = None
    pe: Decimal | None = None
    pbv: Decimal | None = None
    roe: Decimal | None = None
    roa: Decimal | None = None
    debt_ratio: Decimal | None = None
    dividend_yield: Decimal | None = None
    market_cap: Decimal | None = None


class StockAnalysisResponse(BaseModel):
    """Analyzed stock details."""

    asset_id: UUID
    symbol: str
    display_name: str
    company_name: str | None = None
    sector: str | None = None
    industry: str | None = None
    is_shariah: bool
    latest_price: Decimal | None = None
    latest_price_date: date | None = None
    performance: StockPerformanceResponse
    technicals: TechnicalIndicatorsResponse
    fundamentals: FundamentalMetricsResponse
    ai_score: Decimal | None = None


class PriceHistoryPointResponse(BaseModel):
    """Single price history point."""

    price_date: date
    close_price: Decimal
    open_price: Decimal | None = None
    high_price: Decimal | None = None
    low_price: Decimal | None = None
    adjusted_close: Decimal | None = None
    volume: Decimal | None = None


class StockRankingResponse(BaseModel):
    """Ranked stock entry."""

    rank: int
    asset_id: UUID
    symbol: str
    display_name: str
    ai_score: Decimal | None = None
    yearly_return: Decimal | None = None
    rsi_14: Decimal | None = None


class StockComparisonResponse(BaseModel):
    """Side-by-side stock comparison."""

    stocks: list[StockAnalysisResponse]


class CompareStocksRequest(BaseModel):
    """Request body for stock comparison."""

    symbols: list[str] = Field(min_length=1)


class BuyOpportunityResponse(BaseModel):
    """Detected stock buy opportunity."""

    asset_id: UUID
    symbol: str
    opportunity_type: str
    reason: str
    confidence: Decimal
    expected_return_pct: Decimal | None = None
    risk_level: str
