"""Learning engine data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from src.domain.enums import LearningOutcome


@dataclass
class OutcomeEvaluation:
    """Result of comparing prediction to market reality."""

    outcome: LearningOutcome
    actual_return: Decimal | None
    prediction_error: Decimal | None
    learning_score: Decimal
    confidence_adjustment: Decimal
    reward: Decimal
    penalty: Decimal


@dataclass
class SelfEvaluationReport:
    """Aggregate learning performance summary."""

    total_records: int
    evaluated_records: int
    pending_records: int
    accurate_count: int
    partially_accurate_count: int
    inaccurate_count: int
    accuracy_rate: Decimal
    average_prediction_error: Decimal | None
    average_reward: Decimal | None
    average_learning_score: Decimal | None
    feedback_breakdown: dict[str, int] = field(default_factory=dict)
    strategy_weights: dict[str, Decimal] = field(default_factory=dict)
