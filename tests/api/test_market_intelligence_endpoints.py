"""API tests for market intelligence endpoints."""

from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.collectors.base.models import MacroIndicatorRecord, NewsRecord
from src.engines.market_intelligence.sentiment_analyzer import (
    analyze_sentiment,
    classify_news,
)
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.repositories.sqlalchemy.news_repository import SqlAlchemyNewsRepository


def _seed_data(db_session: Session) -> None:
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    news_repo = SqlAlchemyNewsRepository(db_session)

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


def test_market_summary_endpoint(client: TestClient, db_session: Session) -> None:
    """GET /market/summary should return market intelligence."""
    _seed_data(db_session)
    db_session.commit()

    response = client.get("/api/v1/market/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["score"]["overall_score"] is not None


def test_market_news_and_regime_endpoints(
    client: TestClient,
    db_session: Session,
) -> None:
    """News and regime endpoints should return valid payloads."""
    _seed_data(db_session)
    db_session.commit()

    news = client.get("/api/v1/market/news")
    assert news.status_code == 200
    assert len(news.json()["data"]) == 1

    regime = client.get("/api/v1/market/regime")
    assert regime.status_code == 200
    assert regime.json()["data"]["regime"] is not None


def test_market_economy_signals_alerts_endpoints(
    client: TestClient,
    db_session: Session,
) -> None:
    """Economy, signals, alerts, and score endpoints should work."""
    _seed_data(db_session)
    db_session.commit()

    economy = client.get("/api/v1/market/economy")
    assert economy.status_code == 200
    assert len(economy.json()["data"]["indicators"]) >= 1

    signals = client.get("/api/v1/market/signals")
    assert signals.status_code == 200
    assert isinstance(signals.json()["data"], list)

    alerts = client.get("/api/v1/market/alerts")
    assert alerts.status_code == 200
    assert isinstance(alerts.json()["data"], list)

    score = client.get("/api/v1/market/score")
    assert score.status_code == 200
    assert score.json()["data"]["overall_score"] is not None
