"""Integration tests for market intelligence service."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from src.collectors.base.models import MacroIndicatorRecord, NewsRecord
from src.domain.enums import SentimentLabel
from src.engines.market_intelligence.sentiment_analyzer import (
    analyze_sentiment,
    classify_news,
)
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.repositories.sqlalchemy.news_repository import SqlAlchemyNewsRepository
from src.services.market_intelligence_service import MarketIntelligenceService


def _seed_macro(db_session: Session) -> None:
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    market_repo.save_macro(
        MacroIndicatorRecord(
            indicator_name="Inflation",
            release_date=datetime(2026, 1, 1).date(),
            actual_value=Decimal("18"),
            source="test",
            trend="rising",
            forecast_value=Decimal("16"),
        )
    )
    market_repo.save_macro(
        MacroIndicatorRecord(
            indicator_name="Policy Rate",
            release_date=datetime(2026, 1, 1).date(),
            actual_value=Decimal("14"),
            source="test",
            previous_value=Decimal("13"),
        )
    )


def _seed_news(db_session: Session) -> None:
    news_repo = SqlAlchemyNewsRepository(db_session)
    record = NewsRecord(
        headline="Pakistan economy shows growth rally",
        url="https://example.com/news/growth",
        publication_time=datetime(2026, 1, 2, tzinfo=UTC),
        source="test",
        summary="Strong growth in banking sector.",
    )
    category = classify_news(record)
    sentiment, score = analyze_sentiment(record)
    news_repo.save_news(record, category, sentiment, score)


def test_market_intelligence_summary(db_session: Session) -> None:
    """Service should build a market summary from seeded data."""
    _seed_macro(db_session)
    _seed_news(db_session)
    service = MarketIntelligenceService(
        market_data_repository=SqlAlchemyMarketDataRepository(db_session),
        news_repository=SqlAlchemyNewsRepository(db_session),
    )

    summary = service.get_summary()
    assert summary.score.overall_score is not None
    assert summary.regime.regime is not None
    assert len(summary.latest_news) == 1


def test_market_intelligence_news_and_economy(db_session: Session) -> None:
    """Service should return news and economy snapshots."""
    _seed_macro(db_session)
    _seed_news(db_session)
    service = MarketIntelligenceService(
        market_data_repository=SqlAlchemyMarketDataRepository(db_session),
        news_repository=SqlAlchemyNewsRepository(db_session),
    )

    news = service.get_news()
    assert len(news) == 1
    assert news[0].sentiment == SentimentLabel.POSITIVE

    economy = service.get_economy()
    assert len(economy.indicators) == 2

    alerts = service.get_alerts()
    assert isinstance(alerts, list)
