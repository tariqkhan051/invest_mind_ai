"""Learning engine orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from src.domain.entities.learning_record import LearningRecord
from src.domain.entities.portfolio_snapshot import PortfolioSnapshot
from src.domain.entities.recommendation import Recommendation
from src.domain.enums import LearningOutcome
from src.engines.learning.models import OutcomeEvaluation, SelfEvaluationReport
from src.engines.learning.outcome_evaluator import (
    calculate_actual_return,
    calculate_prediction_error,
    classify_outcome,
)
from src.engines.learning.reward_calculator import (
    calculate_confidence_adjustment,
    calculate_reward_penalty,
)
from src.repositories.interfaces.learning_record_repository import (
    LearningRecordRepository,
)
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class LearningEngine:
    """Evaluate recommendations and update learning weights."""

    def __init__(
        self,
        learning_repository: LearningRecordRepository,
        market_data_repository: MarketDataRepository,
    ) -> None:
        self._learning_repository = learning_repository
        self._market_data_repository = market_data_repository

    def create_record(
        self,
        recommendation: Recommendation,
        snapshot: PortfolioSnapshot | None = None,
    ) -> LearningRecord:
        """Create a learning record when a recommendation is generated."""
        record = LearningRecord(
            recommendation_id=recommendation.id,
            portfolio_snapshot_id=snapshot.id if snapshot else None,
            strategy_id=recommendation.recommendation_type.value,
            expected_return=recommendation.expected_return,
            feedback=recommendation.feedback_action,
        )
        return self._learning_repository.save(record)

    def evaluate_record(
        self,
        record: LearningRecord,
        recommendation: Recommendation,
    ) -> LearningRecord:
        """Evaluate a pending learning record against market outcomes."""
        if record.outcome != LearningOutcome.PENDING:
            return record

        actual_return = calculate_actual_return(
            recommendation,
            self._market_data_repository,
        )
        outcome = classify_outcome(
            record.expected_return,
            actual_return,
            recommendation.recommendation_type,
        )
        prediction_error = calculate_prediction_error(
            record.expected_return,
            actual_return,
        )
        strategy_key = record.strategy_id or recommendation.recommendation_type.value
        current_weight = self._learning_repository.get_weight(strategy_key)
        confidence_adjustment = calculate_confidence_adjustment(outcome, current_weight)
        learning_score, reward, penalty = calculate_reward_penalty(
            outcome,
            record.feedback,
            prediction_error,
        )

        evaluation = OutcomeEvaluation(
            outcome=outcome,
            actual_return=actual_return,
            prediction_error=prediction_error,
            learning_score=learning_score,
            confidence_adjustment=confidence_adjustment,
            reward=reward,
            penalty=penalty,
        )
        record.apply_evaluation(
            outcome=evaluation.outcome,
            actual_return=evaluation.actual_return,
            prediction_error=evaluation.prediction_error,
            learning_score=evaluation.learning_score,
            confidence_adjustment=evaluation.confidence_adjustment,
            reward=evaluation.reward,
            penalty=evaluation.penalty,
            evaluated_at=datetime.now(UTC),
        )
        saved = self._learning_repository.save(record)
        if outcome in {
            LearningOutcome.ACCURATE,
            LearningOutcome.INACCURATE,
            LearningOutcome.PARTIALLY_ACCURATE,
        }:
            self._learning_repository.save_weight(strategy_key, confidence_adjustment)
        return saved

    def build_self_evaluation_report(self) -> SelfEvaluationReport:
        """Generate aggregate learning performance metrics."""
        total = self._learning_repository.count_all()
        accurate = self._learning_repository.count_by_outcome(LearningOutcome.ACCURATE)
        partial = self._learning_repository.count_by_outcome(
            LearningOutcome.PARTIALLY_ACCURATE
        )
        inaccurate = self._learning_repository.count_by_outcome(
            LearningOutcome.INACCURATE
        )
        pending = self._learning_repository.count_by_outcome(LearningOutcome.PENDING)
        evaluated = total - pending

        records = self._learning_repository.list_all(limit=1000)
        errors = [
            record.prediction_error
            for record in records
            if record.prediction_error is not None
        ]
        rewards = [record.reward for record in records if record.reward is not None]
        scores = [
            record.learning_score
            for record in records
            if record.learning_score is not None
        ]
        feedback_breakdown: dict[str, int] = {}
        strategy_weights: dict[str, Decimal] = {}
        for record in records:
            if record.feedback is not None:
                key = record.feedback.value
                feedback_breakdown[key] = feedback_breakdown.get(key, 0) + 1
            if record.strategy_id:
                strategy_weights[record.strategy_id] = (
                    self._learning_repository.get_weight(record.strategy_id)
                )

        accuracy_rate = Decimal("0")
        if evaluated > 0:
            accuracy_rate = (
                Decimal(accurate + partial) / Decimal(evaluated) * Decimal("100")
            )

        return SelfEvaluationReport(
            total_records=total,
            evaluated_records=evaluated,
            pending_records=pending,
            accurate_count=accurate,
            partially_accurate_count=partial,
            inaccurate_count=inaccurate,
            accuracy_rate=accuracy_rate.quantize(Decimal("0.01")),
            average_prediction_error=(
                sum(errors) / Decimal(len(errors)) if errors else None
            ),
            average_reward=(
                sum(rewards) / Decimal(len(rewards)) if rewards else None
            ),
            average_learning_score=(
                sum(scores) / Decimal(len(scores)) if scores else None
            ),
            feedback_breakdown=feedback_breakdown,
            strategy_weights=strategy_weights,
        )
