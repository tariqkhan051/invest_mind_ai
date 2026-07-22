"""Stock application service."""

from __future__ import annotations

from datetime import date

from src.core.exceptions import StockNotFoundError
from src.core.logging import get_logger
from src.domain.entities.stock import Stock
from src.domain.read_models.price_history import PriceHistoryPoint
from src.engines.stock.engine import StockEngine
from src.engines.stock.models import (
    BuyOpportunity,
    StockAnalysis,
    StockComparison,
    StockRanking,
)
from src.repositories.interfaces.asset_repository import AssetRepository
from src.repositories.interfaces.market_data_repository import MarketDataRepository

logger = get_logger("services.stock")


class StockService:
    """Stock use cases coordinating persistence and analysis."""

    def __init__(
        self,
        asset_repository: AssetRepository,
        market_data_repository: MarketDataRepository,
        engine: StockEngine | None = None,
    ) -> None:
        self._asset_repository = asset_repository
        self._market_data_repository = market_data_repository
        self._engine = engine or StockEngine()

    def list_stocks(
        self,
        shariah_only: bool = False,
        sector: str | None = None,
    ) -> list[StockAnalysis]:
        """List and analyze all stocks."""
        stocks = self._asset_repository.list_stocks(
            shariah_only=shariah_only,
            sector=sector,
        )
        return [self._analyze_stock(stock) for stock in stocks]

    def get_stock(self, symbol: str) -> StockAnalysis:
        """Get analyzed details for one stock by symbol."""
        stock = self._asset_repository.get_stock_by_symbol(symbol.upper())
        if stock is None:
            raise StockNotFoundError(f"Stock {symbol} not found.")
        return self._analyze_stock(stock)

    def get_price_history(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[PriceHistoryPoint]:
        """Return price history for a stock."""
        stock = self._asset_repository.get_stock_by_symbol(symbol.upper())
        if stock is None:
            raise StockNotFoundError(f"Stock {symbol} not found.")
        return self._market_data_repository.get_price_history(
            stock.asset_id,
            from_date=from_date,
            to_date=to_date,
        )

    def get_rankings(
        self,
        shariah_only: bool = False,
        sector: str | None = None,
        limit: int | None = None,
    ) -> list[StockRanking]:
        """Return ranked stocks."""
        analyses = self.list_stocks(shariah_only=shariah_only, sector=sector)
        return self._engine.rank_stocks(analyses, limit=limit)

    def compare_stocks(self, symbols: list[str]) -> StockComparison:
        """Compare multiple stocks side by side."""
        if not symbols:
            raise StockNotFoundError(
                "At least one stock symbol is required for comparison."
            )
        analyses = [self.get_stock(symbol.upper()) for symbol in symbols]
        return self._engine.compare_stocks(analyses)

    def get_buy_opportunities(
        self,
        shariah_only: bool = False,
        sector: str | None = None,
    ) -> list[BuyOpportunity]:
        """Detect potential buy opportunities."""
        analyses = self.list_stocks(shariah_only=shariah_only, sector=sector)
        return self._engine.find_buy_opportunities(analyses)

    def _analyze_stock(self, stock: Stock) -> StockAnalysis:
        history = self._market_data_repository.get_price_history(stock.asset_id)
        return self._engine.analyze_stock(stock, history)
