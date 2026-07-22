"""Integration tests for stock service."""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from src.collectors.base.models import PriceRecord
from src.domain.entities.asset import Asset
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.services.stock_service import StockService


def _seed_stock(
    db_session: Session,
    symbol: str,
    end_price: Decimal = Decimal("115"),
    pe: Decimal | None = Decimal("9"),
) -> Stock:
    asset_repo = SqlAlchemyAssetRepository(db_session)
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    asset = Asset(
        symbol=symbol,
        display_name=f"{symbol} Limited",
        asset_type=AssetType.STOCK,
        exchange="PSX",
    )
    stock = Stock(
        asset_id=asset.id,
        asset=asset,
        company_name=f"{symbol} Limited",
        industry="Banking",
        pe=pe,
        roe=Decimal("18"),
    )
    saved = asset_repo.save_stock(stock)
    market_repo.save_price(
        PriceRecord(
            symbol=symbol,
            price_date=date(2025, 1, 1),
            close_price=Decimal("100"),
            source="test",
        ),
        saved.asset_id,
    )
    market_repo.save_price(
        PriceRecord(
            symbol=symbol,
            price_date=date(2026, 1, 1),
            close_price=end_price,
            source="test",
        ),
        saved.asset_id,
    )
    return saved


def test_list_stocks_returns_analyses(db_session: Session) -> None:
    """Service should list and analyze persisted stocks."""
    _seed_stock(db_session, "HBL")
    _seed_stock(db_session, "UBL")
    service = StockService(
        asset_repository=SqlAlchemyAssetRepository(db_session),
        market_data_repository=SqlAlchemyMarketDataRepository(db_session),
    )

    stocks = service.list_stocks()
    assert len(stocks) == 2
    assert all(stock.ai_score is not None for stock in stocks)


def test_get_price_history_returns_ordered_points(db_session: Session) -> None:
    """Market data repository should return ascending price history."""
    saved = _seed_stock(db_session, "MCB")
    market_repo = SqlAlchemyMarketDataRepository(db_session)

    history = market_repo.get_price_history(saved.asset_id)
    assert len(history) == 2
    assert history[0].price_date < history[1].price_date


def test_compare_and_rank_stocks(db_session: Session) -> None:
    """Service should rank and compare stocks."""
    _seed_stock(db_session, "TOP", end_price=Decimal("130"))
    _seed_stock(db_session, "BOTTOM", end_price=Decimal("105"))
    service = StockService(
        asset_repository=SqlAlchemyAssetRepository(db_session),
        market_data_repository=SqlAlchemyMarketDataRepository(db_session),
    )

    rankings = service.get_rankings()
    assert rankings[0].symbol == "TOP"

    comparison = service.compare_stocks(["TOP", "BOTTOM"])
    assert len(comparison.stocks) == 2
