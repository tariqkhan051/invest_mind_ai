"""Unit tests for learning engine components."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.learning_record import LearningRecord
from src.domain.enums import (
    FeedbackAction,
    LearningOutcome,
    RecommendationType,
)
from src.engines.learning.outcome_evaluator import (
    calculate_prediction_error,
    classify_outcome,
)
from src.engines.learning.reward_calculator import (
    calculate_confidence_adjustment,
    calculate_reward_penalty,
)


def test_classify_outcome_accurate_when_error_small() -> None:
    """Small prediction error should classify as accurate."""
    outcome = classify_outcome(
        Decimal("10"),
        Decimal("11"),
        RecommendationType.INVEST,
    )
    assert outcome == LearningOutcome.ACCURATE


def test_classify_outcome_no_action_for_hold_cash() -> None:
    """Hold cash recommendations should not be scored against returns."""
    outcome = classify_outcome(
        None,
        Decimal("5"),
        RecommendationType.HOLD_CASH,
    )
    assert outcome == LearningOutcome.NO_OUTCOME


def test_calculate_prediction_error() -> None:
    """Prediction error should be absolute difference."""
    error = calculate_prediction_error(Decimal("12"), Decimal("8"))
    assert error == Decimal("4")


def test_calculate_reward_penalty_with_accepted_feedback() -> None:
    """Accepted feedback should increase reward."""
    score, reward, penalty = calculate_reward_penalty(
        LearningOutcome.ACCURATE,
        FeedbackAction.ACCEPTED,
        Decimal("1"),
    )
    assert reward > Decimal("1")
    assert penalty >= Decimal("0")
    assert score > Decimal("0")


def test_confidence_adjustment_increases_on_accuracy() -> None:
    """Accurate outcomes should increase strategy weight."""
    adjusted = calculate_confidence_adjustment(
        LearningOutcome.ACCURATE,
        Decimal("1.0"),
    )
    assert adjusted > Decimal("1.0")


def test_evaluated_learning_record_is_immutable() -> None:
    """Evaluated records should not be overwritten."""
    record = LearningRecord(
        recommendation_id=uuid4(),
        outcome=LearningOutcome.ACCURATE,
        learning_score=Decimal("1"),
    )
    record.apply_evaluation(
        outcome=LearningOutcome.INACCURATE,
        actual_return=Decimal("-5"),
        prediction_error=Decimal("10"),
        learning_score=Decimal("-1"),
        confidence_adjustment=Decimal("0.5"),
        reward=Decimal("0"),
        penalty=Decimal("1"),
        evaluated_at=datetime.now(UTC),
    )
    assert record.outcome == LearningOutcome.ACCURATE
