"""Asset registration API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_asset_service
from src.api.schemas import ApiResponse
from src.api.schemas.assets import (
    AssetResponse,
    CreateMutualFundRequest,
    CreateStockRequest,
    MutualFundCreatedResponse,
    StockCreatedResponse,
)
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType
from src.services.asset_service import (
    AssetService,
    CreateMutualFundCommand,
    CreateStockCommand,
)

router = APIRouter(prefix="/assets", tags=["Assets"])


def _map_asset(asset: Asset) -> AssetResponse:
    return AssetResponse(
        id=asset.id,
        symbol=asset.symbol,
        display_name=asset.display_name,
        asset_type=asset.asset_type.value,
        is_shariah=asset.is_shariah,
        exchange=asset.exchange,
        provider=asset.provider,
        status=asset.status.value,
    )


def _map_fund(fund: MutualFund) -> MutualFundCreatedResponse:
    return MutualFundCreatedResponse(
        asset_id=fund.asset_id,
        symbol=fund.asset.symbol,
        display_name=fund.asset.display_name,
        asset_type=fund.asset.asset_type.value,
        management_company=fund.management_company,
    )


def _map_stock(stock: Stock) -> StockCreatedResponse:
    return StockCreatedResponse(
        asset_id=stock.asset_id,
        symbol=stock.asset.symbol,
        display_name=stock.asset.display_name,
        company_name=stock.company_name,
        exchange=stock.asset.exchange,
    )


@router.get("", response_model=ApiResponse[list[AssetResponse]])
def list_assets(
    service: Annotated[AssetService, Depends(get_asset_service)],
    asset_type: AssetType | None = Query(default=None),
) -> ApiResponse[list[AssetResponse]]:
    """List registered assets."""
    assets = service.list_assets(asset_type)
    return ApiResponse(
        message="Assets retrieved",
        data=[_map_asset(asset) for asset in assets],
    )


@router.get("/{asset_id}", response_model=ApiResponse[AssetResponse])
def get_asset(
    asset_id: UUID,
    service: Annotated[AssetService, Depends(get_asset_service)],
) -> ApiResponse[AssetResponse]:
    """Get a single asset by id."""
    asset = service.get_asset(asset_id)
    return ApiResponse(message="Asset retrieved", data=_map_asset(asset))


@router.post("/funds", response_model=ApiResponse[MutualFundCreatedResponse])
def create_mutual_fund(
    body: CreateMutualFundRequest,
    service: Annotated[AssetService, Depends(get_asset_service)],
) -> ApiResponse[MutualFundCreatedResponse]:
    """Register a mutual fund so collectors and portfolio can use it."""
    created = service.create_mutual_fund(
        CreateMutualFundCommand(
            symbol=body.symbol,
            display_name=body.display_name,
            asset_type=body.asset_type,
            is_shariah=body.is_shariah,
            management_company=body.management_company,
            expense_ratio=body.expense_ratio,
            aum=body.aum,
        )
    )
    return ApiResponse(message="Mutual fund created", data=_map_fund(created))


@router.post("/stocks", response_model=ApiResponse[StockCreatedResponse])
def create_stock(
    body: CreateStockRequest,
    service: Annotated[AssetService, Depends(get_asset_service)],
) -> ApiResponse[StockCreatedResponse]:
    """Register a PSX stock so collectors and portfolio can use it."""
    created = service.create_stock(
        CreateStockCommand(
            symbol=body.symbol,
            display_name=body.display_name,
            company_name=body.company_name,
            industry=body.industry,
            is_shariah=body.is_shariah,
            market_cap=body.market_cap,
            pe=body.pe,
        )
    )
    return ApiResponse(message="Stock created", data=_map_stock(created))
