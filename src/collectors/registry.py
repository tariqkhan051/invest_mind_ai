"""Collector registry and factory."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.mufap.collector import MufapCollector
from src.collectors.news.collector import NewsCollector
from src.collectors.psx.collector import PsxCollector
from src.collectors.sbp.collector import SbpCollector
from src.config.settings import Settings
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.repositories.sqlalchemy.news_repository import SqlAlchemyNewsRepository


def build_collectors(
    settings: Settings,
    session: Session,
    http_client: CollectorHttpClient | None = None,
) -> dict[str, BaseCollector]:
    """Create configured collector instances for the current session."""
    asset_repository = SqlAlchemyAssetRepository(session)
    market_data_repository = SqlAlchemyMarketDataRepository(session)
    news_repository = SqlAlchemyNewsRepository(session)
    return {
        "mufap": MufapCollector(
            settings,
            asset_repository,
            market_data_repository,
            http_client=http_client,
        ),
        "psx": PsxCollector(
            settings,
            asset_repository,
            market_data_repository,
            http_client=http_client,
        ),
        "sbp": SbpCollector(
            settings,
            market_data_repository,
            http_client=http_client,
        ),
        "news": NewsCollector(
            settings,
            news_repository,
            http_client=http_client,
        ),
    }
