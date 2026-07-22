"""Asset registration application service."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.core.exceptions import FundNotFoundError, PortfolioValidationError
from src.core.logging import get_logger
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType
from src.repositories.interfaces.asset_repository import (
    MUTUAL_FUND_TYPES,
    AssetRepository,
)

logger = get_logger("services.asset")


@dataclass
class CreateMutualFundCommand:
    """Command to register a mutual fund asset."""

    symbol: str
    display_name: str
    asset_type: AssetType = AssetType.MUTUAL_FUND
    is_shariah: bool = True
    management_company: str | None = None
    expense_ratio: Decimal | None = None
    aum: Decimal | None = None
    provider: str | None = "manual"


@dataclass
class CreateStockCommand:
    """Command to register a PSX stock asset."""

    symbol: str
    display_name: str
    company_name: str | None = None
    industry: str | None = None
    is_shariah: bool = True
    market_cap: Decimal | None = None
    pe: Decimal | None = None
    provider: str | None = "manual"


class AssetService:
    """Register and look up investable assets."""

    def __init__(self, asset_repository: AssetRepository) -> None:
        self._asset_repository = asset_repository

    def list_assets(self, asset_type: AssetType | None = None) -> list[Asset]:
        """List active assets, optionally filtered by type."""
        if asset_type is not None:
            return self._asset_repository.find_by_type(asset_type)
        assets: list[Asset] = []
        for fund_type in sorted(MUTUAL_FUND_TYPES, key=lambda item: item.value):
            assets.extend(self._asset_repository.find_by_type(fund_type))
        assets.extend(self._asset_repository.find_by_type(AssetType.STOCK))
        return assets

    def get_by_symbol(self, symbol: str) -> Asset | None:
        """Return an asset by symbol if it exists."""
        return self._asset_repository.get_by_symbol(symbol.strip().upper())

    def get_asset(self, asset_id: UUID) -> Asset:
        """Return an asset by id or raise."""
        asset = self._asset_repository.get_by_id(asset_id)
        if asset is None:
            raise FundNotFoundError(f"Asset {asset_id} not found.")
        return asset

    def create_mutual_fund(self, command: CreateMutualFundCommand) -> MutualFund:
        """Create a mutual fund asset if the symbol is unused."""
        symbol = command.symbol.strip().upper()
        existing = self._asset_repository.get_by_symbol(symbol)
        if existing is not None:
            raise PortfolioValidationError(f"Asset symbol already exists: {symbol}")

        asset = Asset(
            symbol=symbol,
            display_name=command.display_name.strip(),
            asset_type=command.asset_type,
            is_shariah=command.is_shariah,
            provider=command.provider,
        )
        mutual_fund = MutualFund(
            asset_id=asset.id,
            asset=asset,
            management_company=command.management_company,
            expense_ratio=command.expense_ratio,
            aum=command.aum,
        )
        mutual_fund.validate()
        saved = self._asset_repository.save_mutual_fund(mutual_fund)
        logger.info("mutual_fund_created symbol={}", saved.asset.symbol)
        return saved

    def create_stock(self, command: CreateStockCommand) -> Stock:
        """Create a PSX stock asset if the symbol is unused."""
        symbol = command.symbol.strip().upper()
        existing = self._asset_repository.get_by_symbol(symbol)
        if existing is not None:
            raise PortfolioValidationError(f"Asset symbol already exists: {symbol}")

        asset = Asset(
            symbol=symbol,
            display_name=command.display_name.strip(),
            asset_type=AssetType.STOCK,
            exchange="PSX",
            is_shariah=command.is_shariah,
            provider=command.provider,
        )
        stock = Stock(
            asset_id=asset.id,
            asset=asset,
            company_name=command.company_name or command.display_name.strip(),
            industry=command.industry,
            market_cap=command.market_cap,
            pe=command.pe,
        )
        stock.validate()
        saved = self._asset_repository.save_stock(stock)
        logger.info("stock_created symbol={}", saved.asset.symbol)
        return saved
