"""AI recommendation application service."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import ceil
from uuid import UUID

from src.config.settings import Settings
from src.core.exceptions import RecommendationNotFoundError
from src.core.logging import get_logger
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.recommendation import Recommendation
from src.domain.enums import FeedbackAction
from src.engines.decision.engine import DecisionEngine
from src.engines.decision.models import DecisionContext
from src.repositories.interfaces.recommendation_repository import (
    RecommendationRepository,
)
from src.services.learning_service import LearningService
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.mutual_fund_service import MutualFundService
from src.services.portfolio_service import PortfolioService
from src.services.stock_service import StockService

logger = get_logger("services.recommendation")


@dataclass
class PaginatedRecommendations:
    """Paginated recommendation history."""

    items: list[Recommendation]
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass
class RecommendationExplanation:
    """Structured explanation for a recommendation."""

    recommendation_id: UUID
    summary: str
    detailed_explanation: str
    supporting_evidence: dict[str, str]


class RecommendationService:
    """Recommendation use cases coordinating engines and persistence."""

    def __init__(
        self,
        recommendation_repository: RecommendationRepository,
        portfolio_service: PortfolioService,
        mutual_fund_service: MutualFundService,
        stock_service: StockService,
        market_intelligence_service: MarketIntelligenceService,
        settings: Settings,
        engine: DecisionEngine | None = None,
        learning_service: LearningService | None = None,
    ) -> None:
        self._recommendation_repository = recommendation_repository
        self._portfolio_service = portfolio_service
        self._mutual_fund_service = mutual_fund_service
        self._stock_service = stock_service
        self._market_intelligence_service = market_intelligence_service
        self._settings = settings
        self._engine = engine or DecisionEngine()
        self._learning_service = learning_service

    def run_recommendation_cycle(
        self,
        portfolio_id: UUID | None = None,
    ) -> list[Recommendation]:
        """Generate and persist a new batch of recommendations."""
        portfolio_summary = self._portfolio_service.get_summary(portfolio_id)
        shariah_only = self._settings.shariah_mode
        context = DecisionContext(
            portfolio=portfolio_summary,
            market=self._market_intelligence_service.get_summary(),
            funds=self._mutual_fund_service.list_funds(shariah_only=shariah_only),
            stocks=self._stock_service.list_stocks(shariah_only=shariah_only),
            switch_opportunities=self._mutual_fund_service.get_switch_opportunities(
                shariah_only=shariah_only
            ),
            buy_opportunities=self._stock_service.get_buy_opportunities(
                shariah_only=shariah_only
            ),
            monthly_investment=Decimal(self._settings.default_monthly_investment),
            shariah_only=shariah_only,
        )
        recommendations = self._engine.generate(
            context,
            portfolio_summary.portfolio.id,
            min_confidence=self._min_confidence(),
            max_recommendations=self._max_recommendations(),
        )
        saved = [self._recommendation_repository.save(item) for item in recommendations]
        if self._learning_service is not None:
            self._learning_service.record_recommendations(saved)
        logger.info(
            "recommendations_generated portfolio_id={} count={}",
            portfolio_summary.portfolio.id,
            len(saved),
        )
        return saved

    def get_latest(self, portfolio_id: UUID | None = None) -> list[Recommendation]:
        """Return the latest recommendation batch."""
        portfolio = self._resolve_portfolio(portfolio_id)
        return self._recommendation_repository.get_latest_batch(portfolio.id)

    def get_history(
        self,
        portfolio_id: UUID | None = None,
        page: int = 1,
        page_size: int = 25,
    ) -> PaginatedRecommendations:
        """Return paginated recommendation history."""
        portfolio = self._resolve_portfolio(portfolio_id)
        total_items = self._recommendation_repository.count_by_portfolio(portfolio.id)
        offset = (page - 1) * page_size
        items = self._recommendation_repository.list_by_portfolio(
            portfolio.id,
            limit=page_size,
            offset=offset,
        )
        total_pages = ceil(total_items / page_size) if page_size else 0
        return PaginatedRecommendations(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )

    def get_recommendation(self, recommendation_id: UUID) -> Recommendation:
        """Return one recommendation by id."""
        recommendation = self._recommendation_repository.get_by_id(recommendation_id)
        if recommendation is None:
            raise RecommendationNotFoundError(
                f"Recommendation {recommendation_id} not found."
            )
        return recommendation

    def get_explanation(self, recommendation_id: UUID) -> RecommendationExplanation:
        """Return the explanation for a recommendation."""
        recommendation = self.get_recommendation(recommendation_id)
        return RecommendationExplanation(
            recommendation_id=recommendation.id,
            summary=recommendation.reason,
            detailed_explanation=recommendation.explanation,
            supporting_evidence=recommendation.supporting_evidence,
        )

    def record_feedback(
        self,
        recommendation_id: UUID,
        action: FeedbackAction,
        notes: str | None = None,
    ) -> Recommendation:
        """Record user feedback for a recommendation."""
        recommendation = self.get_recommendation(recommendation_id)
        recommendation.record_feedback(action, notes=notes)
        saved = self._recommendation_repository.save(recommendation)
        if self._learning_service is not None:
            self._learning_service.sync_feedback(saved)
        return saved

    def _resolve_portfolio(self, portfolio_id: UUID | None) -> Portfolio:
        if portfolio_id is not None:
            return self._portfolio_service.get_portfolio(portfolio_id)
        return self._portfolio_service.get_or_create_default_portfolio()

    def _min_confidence(self) -> Decimal:
        threshold = self._settings.features_config.get("ai", {}).get(
            "confidence_threshold",
            0.6,
        )
        return Decimal(str(threshold)) * Decimal("100")

    def _max_recommendations(self) -> int:
        return int(
            self._settings.features_config.get("ai", {}).get(
                "max_recommendations_per_day",
                3,
            )
        )
