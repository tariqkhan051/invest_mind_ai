"""Rule-based AI fund scoring (MVP)."""

from __future__ import annotations

from decimal import Decimal

from src.engines.mutual_fund.models import (
    FundAnalysis,
    FundPerformanceMetrics,
    FundRiskMetrics,
)

MAX_SCORE = Decimal("100")
MIN_SCORE = Decimal("0")


def calculate_ai_score(
    performance: FundPerformanceMetrics,
    risk: FundRiskMetrics,
    aum: Decimal | None,
    expense_ratio: Decimal | None,
) -> Decimal:
    """Compute a 0–100 fund score from performance, risk, and fund quality."""
    score = Decimal("50")

    if performance.yearly_return is not None:
        score += _clamp(
            performance.yearly_return / Decimal("2"),
            Decimal("-15"),
            Decimal("20"),
        )

    if performance.monthly_return is not None:
        score += _clamp(performance.monthly_return, Decimal("-5"), Decimal("10"))

    if risk.volatility is not None:
        score -= _clamp(risk.volatility / Decimal("4"), Decimal("0"), Decimal("15"))

    if risk.max_drawdown is not None:
        score -= _clamp(risk.max_drawdown / Decimal("3"), Decimal("0"), Decimal("15"))

    if aum is not None:
        if aum >= Decimal("10000000000"):
            score += Decimal("5")
        elif aum >= Decimal("1000000000"):
            score += Decimal("3")

    if expense_ratio is not None:
        if expense_ratio <= Decimal("1.5"):
            score += Decimal("5")
        elif expense_ratio >= Decimal("3"):
            score -= Decimal("5")

    return _clamp(score, MIN_SCORE, MAX_SCORE)


def rank_score(analysis: FundAnalysis) -> Decimal:
    """Return the primary ranking value for a fund."""
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
