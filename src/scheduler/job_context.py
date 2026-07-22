"""Service construction helpers for scheduler jobs."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.engines.learning.engine import LearningEngine
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.learning_record_repository import (
    SqlAlchemyLearningRecordRepository,
)
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.repositories.sqlalchemy.news_repository import SqlAlchemyNewsRepository
from src.repositories.sqlalchemy.notification_repository import (
    SqlAlchemyNotificationRepository,
)
from src.repositories.sqlalchemy.portfolio_repository import (
    SqlAlchemyPortfolioRepository,
)
from src.repositories.sqlalchemy.recommendation_repository import (
    SqlAlchemyRecommendationRepository,
)
from src.repositories.sqlalchemy.report_repository import SqlAlchemyReportRepository
from src.services.learning_service import LearningService
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.mutual_fund_service import MutualFundService
from src.services.notification_service import NotificationService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService
from src.services.report_service import ReportService
from src.services.stock_service import StockService


def build_portfolio_service(settings: Settings, session: Session) -> PortfolioService:
    """Construct portfolio service for scheduler jobs."""
    return PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(session),
        asset_repository=SqlAlchemyAssetRepository(session),
        settings=settings,
    )


def build_learning_service(settings: Settings, session: Session) -> LearningService:
    """Construct learning service for scheduler jobs."""
    learning_repository = SqlAlchemyLearningRecordRepository(session)
    market_data_repository = SqlAlchemyMarketDataRepository(session)
    return LearningService(
        learning_repository=learning_repository,
        recommendation_repository=SqlAlchemyRecommendationRepository(session),
        portfolio_service=build_portfolio_service(settings, session),
        engine=LearningEngine(learning_repository, market_data_repository),
    )


def build_recommendation_service(
    settings: Settings,
    session: Session,
) -> RecommendationService:
    """Construct recommendation service for scheduler jobs."""
    portfolio_service = build_portfolio_service(settings, session)
    learning_service = None
    if settings.features_config.get("features", {}).get("learning_engine", False):
        learning_service = build_learning_service(settings, session)
    market_data_repository = SqlAlchemyMarketDataRepository(session)
    asset_repository = SqlAlchemyAssetRepository(session)
    return RecommendationService(
        recommendation_repository=SqlAlchemyRecommendationRepository(session),
        portfolio_service=portfolio_service,
        mutual_fund_service=MutualFundService(
            asset_repository=asset_repository,
            market_data_repository=market_data_repository,
        ),
        stock_service=StockService(
            asset_repository=asset_repository,
            market_data_repository=market_data_repository,
        ),
        market_intelligence_service=MarketIntelligenceService(
            market_data_repository=market_data_repository,
            news_repository=SqlAlchemyNewsRepository(session),
        ),
        settings=settings,
        learning_service=learning_service,
    )


def build_notification_service(
    settings: Settings,
    session: Session,
) -> NotificationService:
    """Construct notification service for scheduler jobs."""
    return NotificationService(
        notification_repository=SqlAlchemyNotificationRepository(session),
        settings=settings,
    )


def build_report_service(settings: Settings, session: Session) -> ReportService:
    """Construct report service for scheduler jobs."""
    learning_service = None
    if settings.features_config.get("features", {}).get("learning_engine", False):
        learning_service = build_learning_service(settings, session)
    notification_service = None
    if settings.features_config.get("features", {}).get("notifications", False):
        notification_service = build_notification_service(settings, session)
    market_data_repository = SqlAlchemyMarketDataRepository(session)
    return ReportService(
        report_repository=SqlAlchemyReportRepository(session),
        portfolio_service=build_portfolio_service(settings, session),
        market_intelligence_service=MarketIntelligenceService(
            market_data_repository=market_data_repository,
            news_repository=SqlAlchemyNewsRepository(session),
        ),
        recommendation_service=build_recommendation_service(settings, session),
        settings=settings,
        learning_service=learning_service,
        notification_service=notification_service,
    )
