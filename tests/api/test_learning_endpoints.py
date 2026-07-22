"""API tests for learning endpoints."""

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


def test_learning_records_and_evaluation_api(
    client: TestClient,
    db_session: Session,
) -> None:
    """Learning endpoints should return records and evaluation report."""
    _seed_data(db_session)
    db_session.commit()

    run = client.post("/api/v1/recommendations/run")
    assert run.status_code == 200
    recommendation_id = run.json()["data"][0]["id"]

    feedback = client.post(
        f"/api/v1/recommendations/{recommendation_id}/feedback",
        json={"action": FeedbackAction.ACCEPTED.value},
    )
    assert feedback.status_code == 200

    records = client.get("/api/v1/learning/records")
    assert records.status_code == 200
    body = records.json()
    assert body["success"] is True
    assert body["data"]["meta"]["total_items"] >= 1

    record_id = body["data"]["items"][0]["id"]
    detail = client.get(f"/api/v1/learning/records/{record_id}")
    assert detail.status_code == 200

    evaluate = client.post("/api/v1/learning/evaluate")
    assert evaluate.status_code == 200
    assert len(evaluate.json()["data"]) >= 1

    report = client.get("/api/v1/learning/evaluation")
    assert report.status_code == 200
    assert report.json()["data"]["total_records"] >= 1
