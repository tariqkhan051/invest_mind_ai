"""Integration tests for dashboard service."""

from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
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
from src.services.dashboard_service import DashboardService
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.mutual_fund_service import MutualFundService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService
from src.services.stock_service import StockService


def test_dashboard_service_returns_aggregated_data(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Dashboard service should aggregate portfolio and market data."""
    portfolio_service = PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(db_session),
        asset_repository=SqlAlchemyAssetRepository(db_session),
        settings=test_settings,
    )
    market_data_repository = SqlAlchemyMarketDataRepository(db_session)
    asset_repository = SqlAlchemyAssetRepository(db_session)
    service = DashboardService(
        portfolio_service=portfolio_service,
        market_intelligence_service=MarketIntelligenceService(
            market_data_repository=market_data_repository,
            news_repository=SqlAlchemyNewsRepository(db_session),
        ),
        recommendation_service=RecommendationService(
            recommendation_repository=SqlAlchemyRecommendationRepository(db_session),
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
                news_repository=SqlAlchemyNewsRepository(db_session),
            ),
            settings=test_settings,
        ),
        notification_repository=SqlAlchemyNotificationRepository(db_session),
        scheduler_job_run_repository=SqlAlchemySchedulerJobRunRepository(db_session),
    )

    dashboard = service.get_dashboard()
    assert dashboard.portfolio_summary.portfolio.name
    assert dashboard.market_summary.score.overall_score is not None
    assert isinstance(dashboard.charts.allocation, list)
