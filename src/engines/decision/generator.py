"""Recommendation generation logic."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from src.core.constants import MAX_RECOMMENDATIONS
from src.domain.entities.recommendation import Recommendation
from src.domain.enums import RecommendationStatus, RecommendationType
from src.engines.decision.explanation_builder import build_explanation
from src.engines.decision.models import DecisionContext, OpportunityCandidate
from src.engines.decision.opportunity_builder import build_candidates

DEFAULT_EXPIRY_DAYS = 7


def generate_recommendations(
    context: DecisionContext,
    portfolio_id: UUID,
    min_confidence: Decimal,
    max_recommendations: int = MAX_RECOMMENDATIONS,
    generated_at: datetime | None = None,
) -> list[Recommendation]:
    """Generate ranked recommendations from decision context."""
    generated_at = generated_at or datetime.now(UTC)
    expires_at = generated_at + timedelta(days=DEFAULT_EXPIRY_DAYS)
    candidates = build_candidates(context)
    selected = _select_candidates(candidates, min_confidence, max_recommendations)

    recommendations: list[Recommendation] = []
    for candidate in selected:
        recommendations.append(
            Recommendation(
                portfolio_id=portfolio_id,
                recommendation_type=candidate.recommendation_type,
                priority=candidate.priority,
                asset_id=candidate.asset_id,
                from_asset_id=candidate.from_asset_id,
                to_asset_id=candidate.to_asset_id,
                symbol=candidate.symbol,
                from_symbol=candidate.from_symbol,
                to_symbol=candidate.to_symbol,
                recommended_amount=candidate.recommended_amount,
                expected_return=candidate.expected_return,
                expected_risk=candidate.expected_risk,
                confidence=candidate.score,
                reason=candidate.reason,
                explanation=build_explanation(candidate, context),
                supporting_evidence=candidate.evidence,
                status=RecommendationStatus.ACTIVE,
                generated_at=generated_at,
                expires_at=expires_at,
            )
        )
    return recommendations


def _select_candidates(
    candidates: list[OpportunityCandidate],
    min_confidence: Decimal,
    max_recommendations: int,
) -> list[OpportunityCandidate]:
    actionable = [
        candidate
        for candidate in candidates
        if candidate.recommendation_type != RecommendationType.NO_ACTION
        and candidate.score >= min_confidence
    ]
    actionable.sort(key=lambda item: (item.priority, item.score), reverse=True)
    if actionable:
        return actionable[:max_recommendations]

    no_action = next(
        (
            candidate
            for candidate in candidates
            if candidate.recommendation_type == RecommendationType.NO_ACTION
        ),
        None,
    )
    if no_action is not None:
        return [no_action]
    return candidates[:1]
