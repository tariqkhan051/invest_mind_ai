"""API tests for recommendation endpoints."""

from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.collectors.base.models import MacroIndicatorRecord, NavRecord, NewsRecord
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.enums import AssetType, FeedbackAction
from src.engines.market_intelligence.sentiment_analyzer import (
    analyze_sentiment,
    classify_news,
)
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.repositories.sqlalchemy.news_repository import SqlAlchemyNewsRepository


def _seed_data(db_session: Session) -> None:
    asset_repo = SqlAlchemyAssetRepository(db_session)
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    news_repo = SqlAlchemyNewsRepository(db_session)

    asset = Asset(
        symbol="MIF",
        display_name="Meezan Islamic Fund",
        asset_type=AssetType.MUTUAL_FUND,
    )
    fund = MutualFund(
        asset_id=asset.id,
        asset=asset,
        management_company="Meezan",
        expense_ratio=Decimal("1.5"),
        aum=Decimal("10000000000"),
    )
    saved = asset_repo.save_mutual_fund(fund)
    market_repo.save_nav(
        NavRecord(
            symbol="MIF",
            nav_date=date(2025, 1, 1),
            nav=Decimal("100"),
            source="test",
        ),
        saved.asset_id,
    )
    market_repo.save_nav(
        NavRecord(
            symbol="MIF",
            nav_date=date(2026, 1, 1),
            nav=Decimal("118"),
            source="test",
        ),
        saved.asset_id,
    )
    market_repo.save_macro(
        MacroIndicatorRecord(
            indicator_name="Inflation",
            release_date=date(2026, 1, 1),
            actual_value=Decimal("10"),
            source="test",
            trend="falling",
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


def test_run_and_get_latest_recommendations(
    client: TestClient,
    db_session: Session,
) -> None:
    """POST /recommendations/run and GET /latest should work."""
    _seed_data(db_session)
    db_session.commit()

    run = client.post("/api/v1/recommendations/run")
    assert run.status_code == 200
    body = run.json()
    assert body["success"] is True
    assert len(body["data"]) >= 1

    latest = client.get("/api/v1/recommendations/latest")
    assert latest.status_code == 200
    assert len(latest.json()["data"]) >= 1


def test_recommendation_history_and_feedback(
    client: TestClient,
    db_session: Session,
) -> None:
    """History and feedback endpoints should work."""
    _seed_data(db_session)
    db_session.commit()

    run = client.post("/api/v1/recommendations/run")
    recommendation_id = run.json()["data"][0]["id"]

    history = client.get("/api/v1/recommendations")
    assert history.status_code == 200
    assert history.json()["data"]["meta"]["total_items"] >= 1

    detail = client.get(f"/api/v1/recommendations/{recommendation_id}")
    assert detail.status_code == 200

    explanation = client.get(f"/api/v1/recommendations/explanation/{recommendation_id}")
    assert explanation.status_code == 200
    assert explanation.json()["data"]["summary"]

    feedback = client.post(
        f"/api/v1/recommendations/{recommendation_id}/feedback",
        json={"action": FeedbackAction.ACCEPTED.value},
    )
    assert feedback.status_code == 200
    assert feedback.json()["data"]["status"] == "accepted"
