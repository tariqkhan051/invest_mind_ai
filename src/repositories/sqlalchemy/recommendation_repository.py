"""SQLAlchemy recommendation repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.mappers.recommendation_mapper import RecommendationMapper
from src.database.models.recommendation import RecommendationModel
from src.domain.entities.recommendation import Recommendation
from src.repositories.interfaces.recommendation_repository import (
    RecommendationRepository,
)


class SqlAlchemyRecommendationRepository(RecommendationRepository):
    """Persist and query AI recommendations."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, recommendation: Recommendation) -> Recommendation:
        recommendation.validate()
        model = self._session.get(RecommendationModel, recommendation.id)
        if model is None:
            model = RecommendationMapper.to_model(recommendation)
            self._session.add(model)
        else:
            RecommendationMapper.update_model(model, recommendation)
        self._session.flush()
        return RecommendationMapper.to_entity(model)

    def get_by_id(self, recommendation_id: UUID) -> Recommendation | None:
        model = self._session.get(RecommendationModel, recommendation_id)
        return RecommendationMapper.to_entity(model) if model else None

    def list_by_portfolio(
        self,
        portfolio_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Recommendation]:
        stmt = (
            select(RecommendationModel)
            .where(RecommendationModel.portfolio_id == portfolio_id)
            .order_by(RecommendationModel.generated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [
            RecommendationMapper.to_entity(row) for row in self._session.scalars(stmt)
        ]

    def get_latest_batch(self, portfolio_id: UUID) -> list[Recommendation]:
        latest_stmt = select(func.max(RecommendationModel.generated_at)).where(
            RecommendationModel.portfolio_id == portfolio_id
        )
        latest_generated_at = self._session.scalar(latest_stmt)
        if latest_generated_at is None:
            return []

        stmt = (
            select(RecommendationModel)
            .where(
                RecommendationModel.portfolio_id == portfolio_id,
                RecommendationModel.generated_at == latest_generated_at,
            )
            .order_by(RecommendationModel.priority.desc())
        )
        return [
            RecommendationMapper.to_entity(row) for row in self._session.scalars(stmt)
        ]

    def count_by_portfolio(self, portfolio_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(RecommendationModel)
            .where(RecommendationModel.portfolio_id == portfolio_id)
        )
        return int(self._session.scalar(stmt) or 0)
