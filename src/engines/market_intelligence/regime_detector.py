"""Market regime detection."""

from __future__ import annotations

from decimal import Decimal

from src.domain.enums import MarketRegime, SentimentLabel
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.engines.market_intelligence.models import RegimeAssessment, SentimentSummary

HIGH_INFLATION_THRESHOLD = Decimal("15")
HIGH_RATE_THRESHOLD = Decimal("15")
STRONG_SENTIMENT_THRESHOLD = Decimal("25")


def detect_regime(
    indicators: list[MacroIndicatorPoint],
    sentiment: SentimentSummary,
) -> RegimeAssessment:
    """Detect the current market regime from macro data and sentiment."""
    inflation = _find_indicator(indicators, ("inflation", "cpi"))
    policy_rate = _find_indicator(indicators, ("policy rate", "interest rate"))
    exchange_rate = _find_indicator(indicators, ("usd/pkr", "exchange rate"))

    if inflation is not None and inflation.actual_value >= HIGH_INFLATION_THRESHOLD:
        return RegimeAssessment(
            regime=MarketRegime.HIGH_INFLATION,
            confidence=Decimal("0.85"),
            explanation=(
                f"Inflation at {inflation.actual_value}% exceeds the "
                f"{HIGH_INFLATION_THRESHOLD}% threshold."
            ),
        )

    if policy_rate is not None and policy_rate.actual_value >= HIGH_RATE_THRESHOLD:
        return RegimeAssessment(
            regime=MarketRegime.HIGH_INTEREST_RATE,
            confidence=Decimal("0.8"),
            explanation=(
                f"Policy rate at {policy_rate.actual_value}% indicates a "
                "tight monetary environment."
            ),
        )

    if sentiment.average_score >= STRONG_SENTIMENT_THRESHOLD:
        return RegimeAssessment(
            regime=MarketRegime.STRONG_BULL,
            confidence=Decimal("0.75"),
            explanation="News sentiment is strongly positive.",
        )

    if sentiment.average_score <= -STRONG_SENTIMENT_THRESHOLD:
        return RegimeAssessment(
            regime=MarketRegime.STRONG_BEAR,
            confidence=Decimal("0.75"),
            explanation="News sentiment is strongly negative.",
        )

    if sentiment.dominant_sentiment == SentimentLabel.POSITIVE:
        return RegimeAssessment(
            regime=MarketRegime.BULL,
            confidence=Decimal("0.65"),
            explanation="Positive news sentiment supports a bullish environment.",
        )

    if sentiment.dominant_sentiment == SentimentLabel.NEGATIVE:
        return RegimeAssessment(
            regime=MarketRegime.BEAR,
            confidence=Decimal("0.65"),
            explanation="Negative news sentiment suggests cautious positioning.",
        )

    if exchange_rate is not None and exchange_rate.trend == "volatile":
        return RegimeAssessment(
            regime=MarketRegime.VOLATILE,
            confidence=Decimal("0.6"),
            explanation="Currency volatility is elevated.",
        )

    if inflation is not None and inflation.trend == "falling":
        return RegimeAssessment(
            regime=MarketRegime.RECOVERY,
            confidence=Decimal("0.55"),
            explanation="Falling inflation supports a recovery phase.",
        )

    return RegimeAssessment(
        regime=MarketRegime.NEUTRAL,
        confidence=Decimal("0.5"),
        explanation="No dominant macro or sentiment signal detected.",
    )


def _find_indicator(
    indicators: list[MacroIndicatorPoint],
    names: tuple[str, ...],
) -> MacroIndicatorPoint | None:
    for indicator in indicators:
        lowered = indicator.indicator_name.lower()
        if any(name in lowered for name in names):
            return indicator
    return None
