"""Create missing assets discovered by live collectors."""

from __future__ import annotations

from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType
from src.repositories.interfaces.asset_repository import AssetRepository


def ensure_mutual_fund(
    repository: AssetRepository,
    *,
    symbol: str,
    display_name: str,
    asset_type: AssetType = AssetType.MUTUAL_FUND,
    is_shariah: bool = True,
    management_company: str | None = None,
    provider: str = "mufap",
) -> Asset:
    """Return an existing fund asset or create one."""
    existing = repository.get_by_symbol(symbol)
    if existing is not None:
        return existing
    asset = Asset(
        symbol=symbol,
        display_name=display_name,
        asset_type=asset_type,
        is_shariah=is_shariah,
        provider=provider,
    )
    fund = MutualFund(
        asset_id=asset.id,
        asset=asset,
        management_company=management_company,
    )
    return repository.save_mutual_fund(fund).asset


def ensure_stock(
    repository: AssetRepository,
    *,
    symbol: str,
    display_name: str | None = None,
    is_shariah: bool = True,
    provider: str = "psx",
) -> Asset:
    """Return an existing stock asset or create one."""
    existing = repository.get_by_symbol(symbol)
    if existing is not None:
        return existing
    name = display_name or symbol
    asset = Asset(
        symbol=symbol,
        display_name=name,
        asset_type=AssetType.STOCK,
        exchange="PSX",
        is_shariah=is_shariah,
        provider=provider,
    )
    stock = Stock(asset_id=asset.id, asset=asset, company_name=name)
    return repository.save_stock(stock).asset
