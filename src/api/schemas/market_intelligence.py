"""Market intelligence API schemas — docs/18_API.md §8."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class MacroIndicatorResponse(BaseModel):
    """Macroeconomic indicator observation."""

    indicator_name: str
    release_date: date
    actual_value: Decimal
    country: str
    forecast_value: Decimal | None = None
    previous_value: Decimal | None = None
    unit: str | None = None
    trend: str | None = None
    source: str | None = None


class NewsArticleResponse(BaseModel):
    """Financial news article."""

    id: UUID
    headline: str
    summary: str | None = None
    publisher: str | None = None
    publication_time: datetime
    url: str
    country: str
    category: str
    sentiment: str
    sentiment_score: Decimal
    source: str | None = None


class SentimentSummaryResponse(BaseModel):
    """Aggregated news sentiment."""

    average_score: Decimal
    positive_count: int
    neutral_count: int
    negative_count: int
    dominant_sentiment: str


class RegimeResponse(BaseModel):
    """Detected market regime."""

    regime: str
    confidence: Decimal
    explanation: str


class MarketScoreResponse(BaseModel):
    """Market intelligence score."""

    overall_score: Decimal
    macro_score: Decimal
    sentiment_score: Decimal
    regime_score: Decimal
    calculation_date: date


class InvestmentSignalResponse(BaseModel):
    """Investment signal."""

    signal_type: str
    message: str
    confidence: Decimal


class MarketAlertResponse(BaseModel):
    """Market alert."""

    alert_type: str
    severity: str
    message: str
    detected_at: datetime


class EconomyResponse(BaseModel):
    """Macroeconomic snapshot."""

    indicators: list[MacroIndicatorResponse]


class MarketSummaryResponse(BaseModel):
    """Complete market intelligence summary."""

    score: MarketScoreResponse
    regime: RegimeResponse
    sentiment: SentimentSummaryResponse
    signals: list[InvestmentSignalResponse]
    alerts: list[MarketAlertResponse]
    latest_news: list[NewsArticleResponse]
    economy: EconomyResponse
    news_by_category: dict[str, int] = Field(default_factory=dict)
