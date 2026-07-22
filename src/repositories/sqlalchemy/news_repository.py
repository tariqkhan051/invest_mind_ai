"""SQLAlchemy news repository."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.collectors.base.models import NewsRecord
from src.database.models.market_data import MarketNewsModel
from src.domain.enums import NewsCategory, SentimentLabel
from src.domain.read_models.news_article import NewsArticle
from src.repositories.interfaces.news_repository import NewsRepository


class SqlAlchemyNewsRepository(NewsRepository):
    """Persist and query market news articles."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save_news(
        self,
        record: NewsRecord,
        category: NewsCategory,
        sentiment: SentimentLabel,
        sentiment_score: Decimal,
    ) -> bool:
        if self.news_exists(record.url):
            return False
        model = MarketNewsModel(
            headline=record.headline,
            summary=record.summary,
            publisher=record.publisher,
            publication_time=record.publication_time,
            url=record.url,
            language=record.language,
            country=record.country,
            category=category.value,
            sentiment=sentiment.value,
            sentiment_score=sentiment_score,
            source=record.source,
            status="active",
            created_at=datetime.now(UTC),
        )
        self._session.add(model)
        self._session.flush()
        return True

    def news_exists(self, url: str) -> bool:
        stmt = select(MarketNewsModel.id).where(MarketNewsModel.url == url)
        return self._session.scalar(stmt) is not None

    def list_news(
        self,
        limit: int = 50,
        category: NewsCategory | None = None,
        country: str = "PK",
    ) -> list[NewsArticle]:
        stmt = (
            select(MarketNewsModel)
            .where(
                MarketNewsModel.country == country,
                MarketNewsModel.status == "active",
            )
            .order_by(MarketNewsModel.publication_time.desc())
            .limit(limit)
        )
        if category is not None:
            stmt = stmt.where(MarketNewsModel.category == category.value)
        return [self._to_entity(row) for row in self._session.scalars(stmt)]

    def get_by_id(self, article_id: UUID) -> NewsArticle | None:
        model = self._session.get(MarketNewsModel, article_id)
        if model is None or model.status != "active":
            return None
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: MarketNewsModel) -> NewsArticle:
        return NewsArticle(
            id=model.id,
            headline=model.headline,
            summary=model.summary,
            publisher=model.publisher,
            publication_time=model.publication_time,
            url=model.url,
            country=model.country,
            category=NewsCategory(model.category),
            sentiment=SentimentLabel(model.sentiment),
            sentiment_score=model.sentiment_score,
            source=model.source,
        )
