"""AI decision engine orchestration."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.entities.recommendation import Recommendation
from src.engines.decision.generator import generate_recommendations
from src.engines.decision.models import DecisionContext


class DecisionEngine:
    """Transform portfolio and market intelligence into recommendations."""

    def generate(
        self,
        context: DecisionContext,
        portfolio_id: UUID,
        min_confidence: Decimal,
        max_recommendations: int,
        generated_at: datetime | None = None,
    ) -> list[Recommendation]:
        """Generate recommendations for a portfolio."""
        return generate_recommendations(
            context,
            portfolio_id,
            min_confidence=min_confidence,
            max_recommendations=max_recommendations,
            generated_at=generated_at,
        )
