"""Recommendation entity ↔ ORM mapper."""

from __future__ import annotations

from src.database.models.recommendation import RecommendationModel
from src.domain.entities.recommendation import Recommendation
from src.domain.enums import (
    FeedbackAction,
    RecommendationStatus,
    RecommendationType,
    RiskLevel,
)


class RecommendationMapper:
    """Map between Recommendation entity and ORM model."""

    @staticmethod
    def to_entity(model: RecommendationModel) -> Recommendation:
        return Recommendation(
            id=model.id,
            portfolio_id=model.portfolio_id,
            recommendation_type=RecommendationType(model.recommendation_type),
            priority=model.priority,
            asset_id=model.asset_id,
            from_asset_id=model.from_asset_id,
            to_asset_id=model.to_asset_id,
            symbol=model.symbol,
            from_symbol=model.from_symbol,
            to_symbol=model.to_symbol,
            recommended_amount=model.recommended_amount,
            expected_return=model.expected_return,
            expected_risk=RiskLevel(model.expected_risk),
            confidence=model.confidence,
            reason=model.reason,
            explanation=model.explanation,
            supporting_evidence=model.supporting_evidence or {},
            status=RecommendationStatus(model.status),
            feedback_action=(
                FeedbackAction(model.feedback_action) if model.feedback_action else None
            ),
            feedback_notes=model.feedback_notes,
            generated_at=model.generated_at,
            expires_at=model.expires_at,
        )

    @staticmethod
    def to_model(entity: Recommendation) -> RecommendationModel:
        return RecommendationModel(
            id=entity.id,
            portfolio_id=entity.portfolio_id,
            recommendation_type=entity.recommendation_type.value,
            priority=entity.priority,
            asset_id=entity.asset_id,
            from_asset_id=entity.from_asset_id,
            to_asset_id=entity.to_asset_id,
            symbol=entity.symbol,
            from_symbol=entity.from_symbol,
            to_symbol=entity.to_symbol,
            recommended_amount=entity.recommended_amount,
            expected_return=entity.expected_return,
            expected_risk=entity.expected_risk.value,
            confidence=entity.confidence,
            reason=entity.reason,
            explanation=entity.explanation,
            supporting_evidence=entity.supporting_evidence or None,
            status=entity.status.value,
            feedback_action=(
                entity.feedback_action.value if entity.feedback_action else None
            ),
            feedback_notes=entity.feedback_notes,
            generated_at=entity.generated_at,
            expires_at=entity.expires_at,
        )

    @staticmethod
    def update_model(model: RecommendationModel, entity: Recommendation) -> None:
        updated = RecommendationMapper.to_model(entity)
        for column in RecommendationModel.__table__.columns:
            if column.name == "id":
                continue
            setattr(model, column.name, getattr(updated, column.name))
