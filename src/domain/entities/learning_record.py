"""Learning record entity for continuous AI improvement."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import PortfolioValidationError
from src.domain.enums import FeedbackAction, LearningOutcome


@dataclass
class LearningRecord:
    """Captures recommendation context, feedback, and evaluated outcome."""

    recommendation_id: UUID
    id: UUID = field(default_factory=uuid4)
    portfolio_snapshot_id: UUID | None = None
    strategy_id: str | None = None
    outcome: LearningOutcome = LearningOutcome.PENDING
    expected_return: Decimal | None = None
    actual_return: Decimal | None = None
    prediction_error: Decimal | None = None
    learning_score: Decimal | None = None
    confidence_adjustment: Decimal | None = None
    reward: Decimal | None = None
    penalty: Decimal | None = None
    feedback: FeedbackAction | None = None
    evaluated_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> None:
        """Validate learning record invariants."""
        if self.expected_return is not None and self.expected_return < Decimal("-100"):
            raise PortfolioValidationError("Expected return cannot be below -100%.")

    def apply_feedback(self, action: FeedbackAction) -> None:
        """Record user feedback on the linked recommendation."""
        self.feedback = action

    def apply_evaluation(
        self,
        *,
        outcome: LearningOutcome,
        actual_return: Decimal | None,
        prediction_error: Decimal | None,
        learning_score: Decimal,
        confidence_adjustment: Decimal,
        reward: Decimal,
        penalty: Decimal,
        evaluated_at: datetime,
    ) -> None:
        """Apply outcome evaluation results.

        Historical records are never overwritten.
        """
        if self.outcome != LearningOutcome.PENDING:
            return
        self.outcome = outcome
        self.actual_return = actual_return
        self.prediction_error = prediction_error
        self.learning_score = learning_score
        self.confidence_adjustment = confidence_adjustment
        self.reward = reward
        self.penalty = penalty
        self.evaluated_at = evaluated_at
