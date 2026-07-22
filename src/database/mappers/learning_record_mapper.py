"""Learning record entity ↔ ORM mapper."""

from __future__ import annotations

from src.database.models.learning_record import LearningRecordModel
from src.domain.entities.learning_record import LearningRecord
from src.domain.enums import FeedbackAction, LearningOutcome


class LearningRecordMapper:
    """Map between LearningRecord entity and ORM model."""

    @staticmethod
    def to_entity(model: LearningRecordModel) -> LearningRecord:
        return LearningRecord(
            id=model.id,
            recommendation_id=model.recommendation_id,
            portfolio_snapshot_id=model.portfolio_snapshot_id,
            strategy_id=model.strategy_id,
            outcome=LearningOutcome(model.outcome),
            expected_return=model.expected_return,
            actual_return=model.actual_return,
            prediction_error=model.prediction_error,
            learning_score=model.learning_score,
            confidence_adjustment=model.confidence_adjustment,
            reward=model.reward,
            penalty=model.penalty,
            feedback=(
                FeedbackAction(model.feedback) if model.feedback else None
            ),
            evaluated_at=model.evaluated_at,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: LearningRecord) -> LearningRecordModel:
        return LearningRecordModel(
            id=entity.id,
            recommendation_id=entity.recommendation_id,
            portfolio_snapshot_id=entity.portfolio_snapshot_id,
            strategy_id=entity.strategy_id,
            outcome=entity.outcome.value,
            expected_return=entity.expected_return,
            actual_return=entity.actual_return,
            prediction_error=entity.prediction_error,
            learning_score=entity.learning_score,
            confidence_adjustment=entity.confidence_adjustment,
            reward=entity.reward,
            penalty=entity.penalty,
            feedback=entity.feedback.value if entity.feedback else None,
            evaluated_at=entity.evaluated_at,
            created_at=entity.created_at,
        )

    @staticmethod
    def update_model(model: LearningRecordModel, entity: LearningRecord) -> None:
        updated = LearningRecordMapper.to_model(entity)
        for column in LearningRecordModel.__table__.columns:
            if column.name == "id":
                continue
            setattr(model, column.name, getattr(updated, column.name))
