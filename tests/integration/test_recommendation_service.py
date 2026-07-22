"""Integration tests for recommendation service."""

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from src.collectors.base.models import (
    MacroIndicatorRecord,
    NavRecord,
    NewsRecord,
    PriceRecord,
)
from src.config.settings import Settings
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.stock import Stock
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
from src.repositories.sqlalchemy.portfolio_repository import (
    SqlAlchemyPortfolioRepository,
)
from src.repositories.sqlalchemy.recommendation_repository import (
    SqlAlchemyRecommendationRepository,
)
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.mutual_fund_service import MutualFundService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService
from src.services.stock_service import StockService


def _build_service(
    db_session: Session,
    test_settings: Settings,
) -> RecommendationService:
    portfolio_service = PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(db_session),
        asset_repository=SqlAlchemyAssetRepository(db_session),
        settings=test_settings,
    )
    return RecommendationService(
        recommendation_repository=SqlAlchemyRecommendationRepository(db_session),
        portfolio_service=portfolio_service,
        mutual_fund_service=MutualFundService(
            asset_repository=SqlAlchemyAssetRepository(db_session),
            market_data_repository=SqlAlchemyMarketDataRepository(db_session),
        ),
        stock_service=StockService(
            asset_repository=SqlAlchemyAssetRepository(db_session),
            market_data_repository=SqlAlchemyMarketDataRepository(db_session),
        ),
        market_intelligence_service=MarketIntelligenceService(
            market_data_repository=SqlAlchemyMarketDataRepository(db_session),
            news_repository=SqlAlchemyNewsRepository(db_session),
        ),
        settings=test_settings,
    )


def _seed_market_data(db_session: Session) -> None:
    asset_repo = SqlAlchemyAssetRepository(db_session)
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    news_repo = SqlAlchemyNewsRepository(db_session)

    fund_asset = Asset(
        symbol="MIF",
        display_name="Meezan Islamic Fund",
        asset_type=AssetType.MUTUAL_FUND,
    )
    fund = MutualFund(
        asset_id=fund_asset.id,
        asset=fund_asset,
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

    stock_asset = Asset(
        symbol="HBL",
        display_name="Habib Bank Limited",
        asset_type=AssetType.STOCK,
        exchange="PSX",
    )
    stock = Stock(
        asset_id=stock_asset.id,
        asset=stock_asset,
        company_name="Habib Bank Limited",
        industry="Banking",
        pe=Decimal("8"),
        roe=Decimal("20"),
    )
    saved_stock = asset_repo.save_stock(stock)
    market_repo.save_price(
        PriceRecord(
            symbol="HBL",
            price_date=date(2025, 1, 1),
            close_price=Decimal("100"),
            source="test",
        ),
        saved_stock.asset_id,
    )
    market_repo.save_price(
        PriceRecord(
            symbol="HBL",
            price_date=date(2026, 1, 1),
            close_price=Decimal("120"),
            source="test",
        ),
        saved_stock.asset_id,
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


def test_run_recommendation_cycle_persists_results(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Recommendation service should generate and persist recommendations."""
    _seed_market_data(db_session)
    service = _build_service(db_session, test_settings)

    recommendations = service.run_recommendation_cycle()
    assert len(recommendations) >= 1
    assert all(item.explanation for item in recommendations)

    latest = service.get_latest()
    assert len(latest) == len(recommendations)


def test_record_feedback_updates_status(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Feedback should update recommendation status."""
    _seed_market_data(db_session)
    service = _build_service(db_session, test_settings)
    recommendation = service.run_recommendation_cycle()[0]

    updated = service.record_feedback(
        recommendation.id,
        FeedbackAction.ACCEPTED,
        notes="Looks good.",
    )
    assert updated.status.value == "accepted"
    assert updated.feedback_action == FeedbackAction.ACCEPTED
