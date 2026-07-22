"""SQLAlchemy ORM models."""

from src.database.models.asset import (
    AssetModel,
    BenchmarkModel,
    FundCategoryModel,
    MutualFundModel,
    SectorModel,
    StockModel,
)
from src.database.models.learning_record import (
    LearningRecordModel,
    LearningWeightModel,
)
from src.database.models.market_data import (
    MarketMacroIndicatorModel,
    MarketNewsModel,
    NavHistoryModel,
    PriceHistoryModel,
)
from src.database.models.notification import NotificationModel
from src.database.models.portfolio import (
    HoldingModel,
    InvestmentGoalModel,
    PortfolioModel,
    PortfolioSnapshotModel,
    TransactionModel,
)
from src.database.models.recommendation import RecommendationModel
from src.database.models.report import ReportModel
from src.database.models.scheduler_job_run import SchedulerJobRunModel

__all__ = [
    "AssetModel",
    "BenchmarkModel",
    "FundCategoryModel",
    "HoldingModel",
    "InvestmentGoalModel",
    "MutualFundModel",
    "NotificationModel",
    "LearningRecordModel",
    "LearningWeightModel",
    "MarketMacroIndicatorModel",
    "MarketNewsModel",
    "NavHistoryModel",
    "PortfolioModel",
    "PortfolioSnapshotModel",
    "RecommendationModel",
    "ReportModel",
    "SchedulerJobRunModel",
    "PriceHistoryModel",
    "SectorModel",
    "StockModel",
    "TransactionModel",
]
