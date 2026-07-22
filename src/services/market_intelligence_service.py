"""Market intelligence application service."""

from __future__ import annotations

from uuid import UUID

from src.core.exceptions import NewsNotFoundError
from src.core.logging import get_logger
from src.domain.enums import NewsCategory
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.domain.read_models.news_article import NewsArticle
from src.engines.market_intelligence.engine import MarketIntelligenceEngine
from src.engines.market_intelligence.models import (
    EconomySnapshot,
    InvestmentSignal,
    MarketAlert,
    MarketScore,
    MarketSummary,
    RegimeAssessment,
    SentimentSummary,
)
from src.repositories.interfaces.market_data_repository import MarketDataRepository
from src.repositories.interfaces.news_repository import NewsRepository

logger = get_logger("services.market_intelligence")


class MarketIntelligenceService:
    """Market intelligence use cases coordinating persistence and analysis."""

    def __init__(
        self,
        market_data_repository: MarketDataRepository,
        news_repository: NewsRepository,
        engine: MarketIntelligenceEngine | None = None,
    ) -> None:
        self._market_data_repository = market_data_repository
        self._news_repository = news_repository
        self._engine = engine or MarketIntelligenceEngine()

    def get_summary(self, country: str = "PK") -> MarketSummary:
        """Build the complete market intelligence summary."""
        indicators = self._market_data_repository.get_macro_indicators(country=country)
        news = self._news_repository.list_news(country=country)
        return self._engine.build_summary(indicators, news)

    def get_news(
        self,
        limit: int = 50,
        category: NewsCategory | None = None,
        country: str = "PK",
    ) -> list[NewsArticle]:
        """Return latest news articles."""
        return self._news_repository.list_news(
            limit=limit,
            category=category,
            country=country,
        )

    def get_news_article(self, article_id: UUID) -> NewsArticle:
        """Return one news article by id."""
        article = self._news_repository.get_by_id(article_id)
        if article is None:
            raise NewsNotFoundError(f"News article {article_id} not found.")
        return article

    def get_economy(self, country: str = "PK") -> EconomySnapshot:
        """Return latest macroeconomic indicators."""
        indicators = self._market_data_repository.get_macro_indicators(country=country)
        latest = self._engine.latest_indicators(indicators)
        return EconomySnapshot(indicators=latest)

    def get_regime(self, country: str = "PK") -> RegimeAssessment:
        """Detect the current market regime."""
        indicators = self._market_data_repository.get_macro_indicators(country=country)
        news = self._news_repository.list_news(country=country)
        return self._engine.detect_regime(indicators, news)

    def get_score(self, country: str = "PK") -> MarketScore:
        """Calculate the market intelligence score."""
        indicators = self._market_data_repository.get_macro_indicators(country=country)
        news = self._news_repository.list_news(country=country)
        return self._engine.calculate_score(indicators, news)

    def get_signals(self, country: str = "PK") -> list[InvestmentSignal]:
        """Return investment signals for the current regime."""
        regime = self.get_regime(country=country)
        return self._engine.generate_signals(regime)

    def get_alerts(self, country: str = "PK") -> list[MarketAlert]:
        """Return market alerts from macro changes."""
        indicators = self._market_data_repository.get_macro_indicators(country=country)
        return self._engine.generate_alerts(indicators)

    def get_sentiment(self, country: str = "PK") -> SentimentSummary:
        """Return aggregated news sentiment."""
        from src.engines.market_intelligence.sentiment_analyzer import (
            summarize_sentiment,
        )

        news = self._news_repository.list_news(country=country)
        return summarize_sentiment(news)

    def list_macro_history(
        self,
        country: str = "PK",
        indicator_name: str | None = None,
    ) -> list[MacroIndicatorPoint]:
        """Return macro indicator history."""
        return self._market_data_repository.get_macro_indicators(
            country=country,
            indicator_name=indicator_name,
        )
