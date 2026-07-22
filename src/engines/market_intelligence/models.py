"""Market intelligence analysis data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from src.domain.enums import (
    AlertSeverity,
    InvestmentSignalType,
    MarketRegime,
    NewsCategory,
    SentimentLabel,
)
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.domain.read_models.news_article import NewsArticle


@dataclass
class SentimentSummary:
    """Aggregated news sentiment."""

    average_score: Decimal
    positive_count: int
    neutral_count: int
    negative_count: int
    dominant_sentiment: SentimentLabel


@dataclass
class RegimeAssessment:
    """Detected market regime with explanation."""

    regime: MarketRegime
    confidence: Decimal
    explanation: str


@dataclass
class MarketScore:
    """Overall market intelligence score."""

    overall_score: Decimal
    macro_score: Decimal
    sentiment_score: Decimal
    regime_score: Decimal
    calculation_date: date


@dataclass
class InvestmentSignal:
    """Advisory investment signal."""

    signal_type: InvestmentSignalType
    message: str
    confidence: Decimal


@dataclass
class MarketAlert:
    """Market alert for significant events."""

    alert_type: str
    severity: AlertSeverity
    message: str
    detected_at: datetime


@dataclass
class EconomySnapshot:
    """Latest macroeconomic indicator snapshot."""

    indicators: list[MacroIndicatorPoint] = field(default_factory=list)


@dataclass
class MarketSummary:
    """Complete market intelligence overview."""

    score: MarketScore
    regime: RegimeAssessment
    sentiment: SentimentSummary
    signals: list[InvestmentSignal]
    alerts: list[MarketAlert]
    latest_news: list[NewsArticle]
    economy: EconomySnapshot
    news_by_category: dict[NewsCategory, int] = field(default_factory=dict)
