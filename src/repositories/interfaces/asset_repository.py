"""Abstract asset repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType

MUTUAL_FUND_TYPES: frozenset[AssetType] = frozenset(
    {
        AssetType.MUTUAL_FUND,
        AssetType.MONEY_MARKET_FUND,
        AssetType.INCOME_FUND,
        AssetType.EQUITY_FUND,
        AssetType.BALANCED_FUND,
        AssetType.CASH_MANAGEMENT_FUND,
    }
)


class AssetRepository(ABC):
    """Persistence contract for investable assets."""

    @abstractmethod
    def get_by_id(self, asset_id: UUID) -> Asset | None:
        """Load an asset by identifier."""

    @abstractmethod
    def get_by_symbol(self, symbol: str) -> Asset | None:
        """Load an asset by symbol."""

    @abstractmethod
    def find_by_type(self, asset_type: AssetType) -> list[Asset]:
        """Find assets by type."""

    @abstractmethod
    def save(self, asset: Asset) -> Asset:
        """Create or update an asset."""

    @abstractmethod
    def get_mutual_fund(self, asset_id: UUID) -> MutualFund | None:
        """Load a mutual fund with its asset."""

    @abstractmethod
    def save_mutual_fund(self, mutual_fund: MutualFund) -> MutualFund:
        """Create or update a mutual fund."""

    @abstractmethod
    def get_stock(self, asset_id: UUID) -> Stock | None:
        """Load a stock with its asset."""

    @abstractmethod
    def save_stock(self, stock: Stock) -> Stock:
        """Create or update a stock."""

    @abstractmethod
    def list_mutual_funds(
        self,
        shariah_only: bool = False,
        asset_type: AssetType | None = None,
    ) -> list[MutualFund]:
        """List mutual funds with optional filters."""

    @abstractmethod
    def list_stocks(
        self,
        shariah_only: bool = False,
        sector: str | None = None,
    ) -> list[Stock]:
        """List stocks with optional filters."""

    @abstractmethod
    def get_stock_by_symbol(self, symbol: str) -> Stock | None:
        """Load a stock by its trading symbol."""
