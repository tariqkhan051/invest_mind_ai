"""Recommendation repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.recommendation import Recommendation


class RecommendationRepository(ABC):
    """Persistence contract for AI recommendations."""

    @abstractmethod
    def save(self, recommendation: Recommendation) -> Recommendation:
        """Create or update a recommendation."""

    @abstractmethod
    def get_by_id(self, recommendation_id: UUID) -> Recommendation | None:
        """Load a recommendation by identifier."""

    @abstractmethod
    def list_by_portfolio(
        self,
        portfolio_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Recommendation]:
        """List recommendations for a portfolio ordered by newest first."""

    @abstractmethod
    def get_latest_batch(self, portfolio_id: UUID) -> list[Recommendation]:
        """Return recommendations from the most recent generation run."""

    @abstractmethod
    def count_by_portfolio(self, portfolio_id: UUID) -> int:
        """Count recommendations for a portfolio."""
