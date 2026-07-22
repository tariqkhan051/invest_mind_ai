"""Reward and penalty calculation for learning records."""

from __future__ import annotations

from decimal import Decimal

from src.domain.enums import FeedbackAction, LearningOutcome

BASE_REWARD = Decimal("1.0")
BASE_PENALTY = Decimal("1.0")
FEEDBACK_BONUS = Decimal("0.5")
FEEDBACK_PENALTY = Decimal("0.5")


def calculate_reward_penalty(
    outcome: LearningOutcome,
    feedback: FeedbackAction | None,
    prediction_error: Decimal | None,
) -> tuple[Decimal, Decimal, Decimal]:
    """Return learning score, reward, and penalty."""
    reward = Decimal("0")
    penalty = Decimal("0")

    if outcome == LearningOutcome.ACCURATE:
        reward = BASE_REWARD
    elif outcome == LearningOutcome.PARTIALLY_ACCURATE:
        reward = BASE_REWARD / Decimal("2")
    elif outcome == LearningOutcome.INACCURATE:
        penalty = BASE_PENALTY
    elif outcome == LearningOutcome.NO_OUTCOME:
        reward = Decimal("0.25")

    if feedback == FeedbackAction.ACCEPTED:
        reward += FEEDBACK_BONUS
    elif feedback == FeedbackAction.REJECTED:
        penalty += FEEDBACK_PENALTY

    learning_score = reward - penalty
    if prediction_error is not None:
        error_penalty = min(prediction_error / Decimal("10"), Decimal("1"))
        learning_score -= error_penalty
        penalty += error_penalty

    return learning_score, reward, penalty


def calculate_confidence_adjustment(
    outcome: LearningOutcome,
    current_weight: Decimal,
) -> Decimal:
    """Compute weight multiplier adjustment for a strategy."""
    step = Decimal("0.05")
    if outcome == LearningOutcome.ACCURATE:
        return min(current_weight + step, Decimal("2.0"))
    if outcome == LearningOutcome.INACCURATE:
        return max(current_weight - step, Decimal("0.5"))
    if outcome == LearningOutcome.PARTIALLY_ACCURATE:
        return current_weight
    return current_weight
