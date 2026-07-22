"""Integration tests for learning service."""

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from src.collectors.base.models import MacroIndicatorRecord, NavRecord, NewsRecord
from src.config.settings import Settings
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.enums import AssetType, FeedbackAction, LearningOutcome
from src.engines.learning.engine import LearningEngine
from src.engines.market_intelligence.sentiment_analyzer import (
    analyze_sentiment,
    classify_news,
)
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.learning_record_repository import (
    SqlAlchemyLearningRecordRepository,
)
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.repositories.sqlalchemy.news_repository import SqlAlchemyNewsRepository
from src.repositories.sqlalchemy.portfolio_repository import (
    SqlAlchemyPortfolioRepository,
)
from src.repositories.sqlalchemy.recommendation_repository import (
    SqlAlchemyRecommendationRepository,
)
from src.services.learning_service import LearningService
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.mutual_fund_service import MutualFundService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService
from src.services.stock_service import StockService


def _build_recommendation_service(
    db_session: Session,
    test_settings: Settings,
) -> RecommendationService:
    portfolio_service = PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(db_session),
        asset_repository=SqlAlchemyAssetRepository(db_session),
        settings=test_settings,
    )
    learning_repository = SqlAlchemyLearningRecordRepository(db_session)
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    learning_service = LearningService(
        learning_repository=learning_repository,
        recommendation_repository=SqlAlchemyRecommendationRepository(db_session),
        portfolio_service=portfolio_service,
        engine=LearningEngine(learning_repository, market_repo),
    )
    return RecommendationService(
        recommendation_repository=SqlAlchemyRecommendationRepository(db_session),
        portfolio_service=portfolio_service,
        mutual_fund_service=MutualFundService(
            asset_repository=SqlAlchemyAssetRepository(db_session),
            market_data_repository=market_repo,
        ),
        stock_service=StockService(
            asset_repository=SqlAlchemyAssetRepository(db_session),
            market_data_repository=market_repo,
        ),
        market_intelligence_service=MarketIntelligenceService(
            market_data_repository=market_repo,
            news_repository=SqlAlchemyNewsRepository(db_session),
        ),
        settings=test_settings,
        learning_service=learning_service,
    )


def _seed_market_data(db_session: Session) -> None:
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
    saved_fund = asset_repo.save_mutual_fund(fund)
    market_repo.save_nav(
        NavRecord(
            symbol="MIF",
            nav_date=date(2025, 1, 1),
            nav=Decimal("100"),
            source="test",
        ),
        saved_fund.asset_id,
    )
    market_repo.save_nav(
        NavRecord(
            symbol="MIF",
            nav_date=date(2026, 1, 1),
            nav=Decimal("118"),
            source="test",
        ),
        saved_fund.asset_id,
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


def test_learning_records_created_on_recommendation_run(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Running recommendations should create learning records."""
    _seed_market_data(db_session)
    service = _build_recommendation_service(db_session, test_settings)
    recommendations = service.run_recommendation_cycle()
    assert recommendations

    learning_repo = SqlAlchemyLearningRecordRepository(db_session)
    for recommendation in recommendations:
        record = learning_repo.get_by_recommendation_id(recommendation.id)
        assert record is not None
        assert record.portfolio_snapshot_id is not None
        assert record.outcome == LearningOutcome.PENDING


def test_learning_feedback_and_evaluation(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Feedback sync and evaluation should update learning records."""
    _seed_market_data(db_session)
    service = _build_recommendation_service(db_session, test_settings)
    recommendations = service.run_recommendation_cycle()
    recommendation_id = recommendations[0].id

    service.record_feedback(recommendation_id, FeedbackAction.ACCEPTED)

    learning_service = service._learning_service
    assert learning_service is not None
    evaluated = learning_service.evaluate_pending()
    assert evaluated

    learning_repo = SqlAlchemyLearningRecordRepository(db_session)
    record = learning_repo.get_by_recommendation_id(recommendation_id)
    assert record is not None
    assert record.feedback == FeedbackAction.ACCEPTED
    assert record.outcome != LearningOutcome.PENDING

    report = learning_service.get_self_evaluation()
    assert report.total_records >= 1
