"""News repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from src.collectors.base.models import NewsRecord
from src.domain.enums import NewsCategory, SentimentLabel
from src.domain.read_models.news_article import NewsArticle


class NewsRepository(ABC):
    """Persistence contract for market news."""

    @abstractmethod
    def save_news(
        self,
        record: NewsRecord,
        category: NewsCategory,
        sentiment: SentimentLabel,
        sentiment_score: Decimal,
    ) -> bool:
        """Save a news article. Returns False when duplicate exists."""

    @abstractmethod
    def news_exists(self, url: str) -> bool:
        """Return True when a news article with the URL already exists."""

    @abstractmethod
    def list_news(
        self,
        limit: int = 50,
        category: NewsCategory | None = None,
        country: str = "PK",
    ) -> list[NewsArticle]:
        """List news articles ordered by publication time descending."""

    @abstractmethod
    def get_by_id(self, article_id: UUID) -> NewsArticle | None:
        """Load a news article by identifier."""
