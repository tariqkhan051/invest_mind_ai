"""Recommendation explanation builder."""

from __future__ import annotations

from src.engines.decision.models import DecisionContext, OpportunityCandidate


def build_explanation(
    candidate: OpportunityCandidate,
    context: DecisionContext,
) -> str:
    """Build a human-readable explanation for a recommendation."""
    lines = [
        candidate.reason,
        "",
        "Why now?",
        f"- Market regime: {context.market.regime.regime.value}",
        f"- Market score: {context.market.score.overall_score:.1f}/100",
        f"- Portfolio value: {context.portfolio.valuation.total_value} PKR",
    ]

    if context.market.sentiment.dominant_sentiment:
        lines.append(
            f"- News sentiment: {context.market.sentiment.dominant_sentiment.value}"
        )

    if candidate.symbol:
        lines.append(f"- Target: {candidate.symbol}")
    if candidate.from_symbol and candidate.to_symbol:
        lines.append(f"- Switch: {candidate.from_symbol} -> {candidate.to_symbol}")

    if candidate.recommended_amount is not None:
        lines.append(f"- Suggested amount: {candidate.recommended_amount} PKR")

    lines.extend(["", "Supporting factors:"])
    for key, value in candidate.evidence.items():
        lines.append(f"- {key.replace('_', ' ').title()}: {value}")

    return "\n".join(lines)
