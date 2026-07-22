"""API route modules."""

from src.api.routes.assets import router as assets_router
from src.api.routes.collectors import router as collectors_router
from src.api.routes.dashboard import router as dashboard_router
from src.api.routes.health import router as health_router
from src.api.routes.learning import router as learning_router
from src.api.routes.market_intelligence import router as market_intelligence_router
from src.api.routes.mutual_fund import router as mutual_fund_router
from src.api.routes.notification import router as notification_router
from src.api.routes.portfolio import router as portfolio_router
from src.api.routes.recommendation import router as recommendation_router
from src.api.routes.report import router as report_router
from src.api.routes.scheduler import router as scheduler_router
from src.api.routes.stock import router as stock_router

__all__ = [
    "assets_router",
    "collectors_router",
    "dashboard_router",
    "health_router",
    "market_intelligence_router",
    "learning_router",
    "notification_router",
    "report_router",
    "mutual_fund_router",
    "portfolio_router",
    "recommendation_router",
    "scheduler_router",
    "stock_router",
]
