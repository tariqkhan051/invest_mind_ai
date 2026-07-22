"""Stock analysis data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class StockPerformanceMetrics:
    """Computed performance metrics for a stock."""

    daily_return: Decimal | None = None
    weekly_return: Decimal | None = None
    monthly_return: Decimal | None = None
    quarterly_return: Decimal | None = None
    yearly_return: Decimal | None = None
    cagr_3y: Decimal | None = None
    volatility: Decimal | None = None
    max_drawdown: Decimal | None = None


@dataclass
class TechnicalIndicators:
    """Technical indicator snapshot."""

    sma_20: Decimal | None = None
    sma_50: Decimal | None = None
    ema_12: Decimal | None = None
    rsi_14: Decimal | None = None
    momentum: Decimal | None = None
    volume_trend: Decimal | None = None


@dataclass
class FundamentalMetrics:
    """Fundamental ratio snapshot."""

    eps: Decimal | None = None
    pe: Decimal | None = None
    pbv: Decimal | None = None
    roe: Decimal | None = None
    roa: Decimal | None = None
    debt_ratio: Decimal | None = None
    dividend_yield: Decimal | None = None
    market_cap: Decimal | None = None


@dataclass
class StockAnalysis:
    """Complete analysis output for one stock."""

    asset_id: UUID
    symbol: str
    display_name: str
    company_name: str | None
    sector: str | None
    industry: str | None
    is_shariah: bool
    latest_price: Decimal | None
    latest_price_date: date | None
    performance: StockPerformanceMetrics = field(
        default_factory=StockPerformanceMetrics
    )
    technicals: TechnicalIndicators = field(default_factory=TechnicalIndicators)
    fundamentals: FundamentalMetrics = field(default_factory=FundamentalMetrics)
    ai_score: Decimal | None = None


@dataclass
class StockRanking:
    """Ranked stock entry."""

    rank: int
    asset_id: UUID
    symbol: str
    display_name: str
    ai_score: Decimal | None
    yearly_return: Decimal | None
    rsi_14: Decimal | None


@dataclass
class StockComparison:
    """Side-by-side stock comparison."""

    stocks: list[StockAnalysis]


@dataclass
class BuyOpportunity:
    """Detected stock buy opportunity."""

    asset_id: UUID
    symbol: str
    opportunity_type: str
    reason: str
    confidence: Decimal
    expected_return_pct: Decimal | None = None
    risk_level: str = "moderate"
