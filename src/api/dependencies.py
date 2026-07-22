"""FastAPI dependency providers."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.settings import Settings, get_settings
from src.core.container import Container, get_container
from src.database.session import get_db_session
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
from src.repositories.sqlalchemy.scheduler_job_run_repository import (
    SqlAlchemySchedulerJobRunRepository,
)
from src.scheduler import get_scheduler
from src.scheduler.job_context import (
    build_notification_service,
    build_report_service,
)
from src.services.asset_service import AssetService
from src.services.collector_service import CollectorService
from src.services.dashboard_service import DashboardService
from src.services.learning_service import LearningService
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.mutual_fund_service import MutualFundService
from src.services.notification_service import NotificationService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService
from src.services.report_service import ReportService
from src.services.scheduler_service import SchedulerService
from src.services.stock_service import StockService


def get_app_settings() -> Settings:
    """Provide application settings."""
    return get_settings()


def get_app_container(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> Container:
    """Provide the application DI container."""
    container = get_container()
    container.settings = settings
    return container


def get_db(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> Generator[Session]:
    """Provide a database session per request."""
    yield from get_db_session(settings)


def get_asset_service(
    session: Annotated[Session, Depends(get_db)],
) -> AssetService:
    """Provide the asset registration service."""
    return AssetService(asset_repository=SqlAlchemyAssetRepository(session))


def get_portfolio_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> PortfolioService:
    """Provide the portfolio application service."""
    return PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(session),
        asset_repository=SqlAlchemyAssetRepository(session),
        settings=settings,
    )


def get_collector_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> CollectorService:
    """Provide the data collector service."""
    return CollectorService(settings=settings, session=session)


def get_mutual_fund_service(
    session: Annotated[Session, Depends(get_db)],
) -> MutualFundService:
    """Provide the mutual fund application service."""
    return MutualFundService(
        asset_repository=SqlAlchemyAssetRepository(session),
        market_data_repository=SqlAlchemyMarketDataRepository(session),
    )


def get_stock_service(
    session: Annotated[Session, Depends(get_db)],
) -> StockService:
    """Provide the stock application service."""
    return StockService(
        asset_repository=SqlAlchemyAssetRepository(session),
        market_data_repository=SqlAlchemyMarketDataRepository(session),
    )


def get_market_intelligence_service(
    session: Annotated[Session, Depends(get_db)],
) -> MarketIntelligenceService:
    """Provide the market intelligence application service."""
    return MarketIntelligenceService(
        market_data_repository=SqlAlchemyMarketDataRepository(session),
        news_repository=SqlAlchemyNewsRepository(session),
    )


def _build_portfolio_service(
    settings: Settings,
    session: Session,
) -> PortfolioService:
    return PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(session),
        asset_repository=SqlAlchemyAssetRepository(session),
        settings=settings,
    )


def get_learning_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> LearningService:
    """Provide the learning application service."""
    learning_repository = SqlAlchemyLearningRecordRepository(session)
    market_data_repository = SqlAlchemyMarketDataRepository(session)
    return LearningService(
        learning_repository=learning_repository,
        recommendation_repository=SqlAlchemyRecommendationRepository(session),
        portfolio_service=_build_portfolio_service(settings, session),
        engine=LearningEngine(learning_repository, market_data_repository),
    )


def get_recommendation_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> RecommendationService:
    """Provide the AI recommendation application service."""
    portfolio_service = _build_portfolio_service(settings, session)
    learning_service = None
    if settings.features_config.get("features", {}).get("learning_engine", False):
        learning_repository = SqlAlchemyLearningRecordRepository(session)
        learning_service = LearningService(
            learning_repository=learning_repository,
            recommendation_repository=SqlAlchemyRecommendationRepository(session),
            portfolio_service=portfolio_service,
            engine=LearningEngine(
                learning_repository,
                SqlAlchemyMarketDataRepository(session),
            ),
        )
    return RecommendationService(
        recommendation_repository=SqlAlchemyRecommendationRepository(session),
        portfolio_service=portfolio_service,
        mutual_fund_service=MutualFundService(
            asset_repository=SqlAlchemyAssetRepository(session),
            market_data_repository=SqlAlchemyMarketDataRepository(session),
        ),
        stock_service=StockService(
            asset_repository=SqlAlchemyAssetRepository(session),
            market_data_repository=SqlAlchemyMarketDataRepository(session),
        ),
        market_intelligence_service=MarketIntelligenceService(
            market_data_repository=SqlAlchemyMarketDataRepository(session),
            news_repository=SqlAlchemyNewsRepository(session),
        ),
        settings=settings,
        learning_service=learning_service,
    )


def get_notification_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> NotificationService:
    """Provide the notification application service."""
    return build_notification_service(settings, session)


def get_report_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> ReportService:
    """Provide the report application service."""
    return build_report_service(settings, session)


def get_dashboard_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> DashboardService:
    """Provide the dashboard aggregation service."""
    portfolio_service = PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(session),
        asset_repository=SqlAlchemyAssetRepository(session),
        settings=settings,
    )
    return DashboardService(
        portfolio_service=portfolio_service,
        market_intelligence_service=MarketIntelligenceService(
            market_data_repository=SqlAlchemyMarketDataRepository(session),
            news_repository=SqlAlchemyNewsRepository(session),
        ),
        recommendation_service=RecommendationService(
            recommendation_repository=SqlAlchemyRecommendationRepository(session),
            portfolio_service=portfolio_service,
            mutual_fund_service=MutualFundService(
                asset_repository=SqlAlchemyAssetRepository(session),
                market_data_repository=SqlAlchemyMarketDataRepository(session),
            ),
            stock_service=StockService(
                asset_repository=SqlAlchemyAssetRepository(session),
                market_data_repository=SqlAlchemyMarketDataRepository(session),
            ),
            market_intelligence_service=MarketIntelligenceService(
                market_data_repository=SqlAlchemyMarketDataRepository(session),
                news_repository=SqlAlchemyNewsRepository(session),
            ),
            settings=settings,
            learning_service=(
                LearningService(
                    learning_repository=SqlAlchemyLearningRecordRepository(session),
                    recommendation_repository=SqlAlchemyRecommendationRepository(
                        session
                    ),
                    portfolio_service=portfolio_service,
                    engine=LearningEngine(
                        SqlAlchemyLearningRecordRepository(session),
                        SqlAlchemyMarketDataRepository(session),
                    ),
                )
                if settings.features_config.get("features", {}).get(
                    "learning_engine", False
                )
                else None
            ),
        ),
        notification_repository=SqlAlchemyNotificationRepository(session),
        scheduler_job_run_repository=SqlAlchemySchedulerJobRunRepository(session),
    )


def get_scheduler_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> SchedulerService:
    """Provide the scheduler application service."""
    return SchedulerService(
        job_run_repository=SqlAlchemySchedulerJobRunRepository(session),
        settings=settings,
        scheduler=get_scheduler(),
    )
