"""Market intelligence scoring."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.domain.enums import MarketRegime
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.engines.market_intelligence.models import (
    MarketScore,
    RegimeAssessment,
    SentimentSummary,
)

MAX_SCORE = Decimal("100")
MIN_SCORE = Decimal("0")

REGIME_SCORES: dict[MarketRegime, Decimal] = {
    MarketRegime.STRONG_BULL: Decimal("85"),
    MarketRegime.BULL: Decimal("70"),
    MarketRegime.RECOVERY: Decimal("65"),
    MarketRegime.NEUTRAL: Decimal("50"),
    MarketRegime.VOLATILE: Decimal("40"),
    MarketRegime.BEAR: Decimal("30"),
    MarketRegime.STRONG_BEAR: Decimal("20"),
    MarketRegime.HIGH_INFLATION: Decimal("35"),
    MarketRegime.HIGH_INTEREST_RATE: Decimal("38"),
}


def calculate_market_score(
    indicators: list[MacroIndicatorPoint],
    sentiment: SentimentSummary,
    regime: RegimeAssessment,
    as_of: date | None = None,
) -> MarketScore:
    """Compute the overall market intelligence score."""
    as_of = as_of or date.today()
    macro_score = _macro_score(indicators)
    sentiment_score = _sentiment_score(sentiment)
    regime_score = REGIME_SCORES.get(regime.regime, Decimal("50"))
    overall = _clamp(
        (macro_score + sentiment_score + regime_score) / Decimal("3"),
        MIN_SCORE,
        MAX_SCORE,
    )
    return MarketScore(
        overall_score=overall,
        macro_score=macro_score,
        sentiment_score=sentiment_score,
        regime_score=regime_score,
        calculation_date=as_of,
    )


def _macro_score(indicators: list[MacroIndicatorPoint]) -> Decimal:
    if not indicators:
        return Decimal("50")
    score = Decimal("50")
    for indicator in indicators:
        name = indicator.indicator_name.lower()
        if indicator.trend == "rising" and "inflation" in name:
            score -= Decimal("5")
        elif indicator.trend == "falling" and "inflation" in name:
            score += Decimal("5")
        elif indicator.trend == "stable":
            score += Decimal("2")
    return _clamp(score, MIN_SCORE, MAX_SCORE)


def _sentiment_score(sentiment: SentimentSummary) -> Decimal:
    normalized = Decimal("50") + (sentiment.average_score / Decimal("2"))
    return _clamp(normalized, MIN_SCORE, MAX_SCORE)


def _clamp(value: Decimal, minimum: Decimal, maximum: Decimal) -> Decimal:
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value
