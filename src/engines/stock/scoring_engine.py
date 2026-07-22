"""Rule-based AI stock scoring (MVP)."""

from __future__ import annotations

from decimal import Decimal

from src.engines.stock.models import (
    FundamentalMetrics,
    StockAnalysis,
    StockPerformanceMetrics,
    TechnicalIndicators,
)

MAX_SCORE = Decimal("100")
MIN_SCORE = Decimal("0")


def calculate_ai_score(
    performance: StockPerformanceMetrics,
    technicals: TechnicalIndicators,
    fundamentals: FundamentalMetrics,
) -> Decimal:
    """Compute a 0–100 stock score from performance, technicals, and fundamentals."""
    score = Decimal("50")

    if performance.yearly_return is not None:
        score += _clamp(
            performance.yearly_return / Decimal("2"),
            Decimal("-15"),
            Decimal("20"),
        )

    if performance.monthly_return is not None:
        score += _clamp(performance.monthly_return, Decimal("-5"), Decimal("10"))

    if performance.volatility is not None:
        score -= _clamp(
            performance.volatility / Decimal("4"),
            Decimal("0"),
            Decimal("15"),
        )

    if technicals.rsi_14 is not None:
        if Decimal("40") <= technicals.rsi_14 <= Decimal("65"):
            score += Decimal("5")
        elif technicals.rsi_14 > Decimal("75"):
            score -= Decimal("5")

    if technicals.momentum is not None and technicals.momentum > Decimal("0"):
        score += _clamp(
            technicals.momentum / Decimal("4"),
            Decimal("0"),
            Decimal("10"),
        )

    if fundamentals.pe is not None:
        if fundamentals.pe < Decimal("12"):
            score += Decimal("5")
        elif fundamentals.pe > Decimal("25"):
            score -= Decimal("5")

    if fundamentals.roe is not None and fundamentals.roe > Decimal("15"):
        score += Decimal("5")

    if (
        fundamentals.dividend_yield is not None
        and fundamentals.dividend_yield > Decimal("4")
    ):
        score += Decimal("3")

    return _clamp(score, MIN_SCORE, MAX_SCORE)


def rank_score(analysis: StockAnalysis) -> Decimal:
    """Return the primary ranking value for a stock."""
    if analysis.ai_score is not None:
        return analysis.ai_score
    if analysis.performance.yearly_return is not None:
        return analysis.performance.yearly_return
    return Decimal("0")


def _clamp(value: Decimal, minimum: Decimal, maximum: Decimal) -> Decimal:
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value
