"""Investment recommendation entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import PortfolioValidationError
from src.domain.enums import (
    FeedbackAction,
    RecommendationStatus,
    RecommendationType,
    RiskLevel,
)


@dataclass
class Recommendation:
    """AI-generated investment recommendation."""

    portfolio_id: UUID
    recommendation_type: RecommendationType
    confidence: Decimal
    reason: str
    explanation: str
    id: UUID = field(default_factory=uuid4)
    priority: int = 50
    asset_id: UUID | None = None
    from_asset_id: UUID | None = None
    to_asset_id: UUID | None = None
    symbol: str | None = None
    from_symbol: str | None = None
    to_symbol: str | None = None
    recommended_amount: Decimal | None = None
    expected_return: Decimal | None = None
    expected_risk: RiskLevel = RiskLevel.MODERATE
    supporting_evidence: dict[str, str] = field(default_factory=dict)
    status: RecommendationStatus = RecommendationStatus.ACTIVE
    feedback_action: FeedbackAction | None = None
    feedback_notes: str | None = None
    generated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None

    def validate(self) -> None:
        """Validate recommendation invariants."""
        if not self.reason.strip():
            raise PortfolioValidationError("Recommendation reason is required.")
        if not self.explanation.strip():
            raise PortfolioValidationError("Recommendation explanation is required.")
        if self.confidence < Decimal("0") or self.confidence > Decimal("100"):
            raise PortfolioValidationError("Confidence must be between 0 and 100.")

    def record_feedback(self, action: FeedbackAction, notes: str | None = None) -> None:
        """Apply user feedback to the recommendation."""
        self.feedback_action = action
        self.feedback_notes = notes
        if action == FeedbackAction.ACCEPTED:
            self.status = RecommendationStatus.ACCEPTED
        elif action == FeedbackAction.REJECTED:
            self.status = RecommendationStatus.REJECTED
        elif action == FeedbackAction.IGNORED:
            self.status = RecommendationStatus.IGNORED
