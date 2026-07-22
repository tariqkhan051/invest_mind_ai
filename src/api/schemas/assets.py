"""Asset registration API schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.enums import AssetType


class AssetResponse(BaseModel):
    """Asset summary response."""

    id: UUID
    symbol: str
    display_name: str
    asset_type: str
    is_shariah: bool
    exchange: str | None = None
    provider: str | None = None
    status: str


class CreateMutualFundRequest(BaseModel):
    """Request body for registering a mutual fund."""

    symbol: str = Field(min_length=1, max_length=32)
    display_name: str = Field(min_length=1, max_length=200)
    asset_type: AssetType = AssetType.MUTUAL_FUND
    is_shariah: bool = True
    management_company: str | None = None
    expense_ratio: Decimal | None = Field(default=None, ge=0)
    aum: Decimal | None = Field(default=None, ge=0)


class CreateStockRequest(BaseModel):
    """Request body for registering a PSX stock."""

    symbol: str = Field(min_length=1, max_length=32)
    display_name: str = Field(min_length=1, max_length=200)
    company_name: str | None = None
    industry: str | None = None
    is_shariah: bool = True
    market_cap: Decimal | None = Field(default=None, ge=0)
    pe: Decimal | None = Field(default=None, ge=0)


class MutualFundCreatedResponse(BaseModel):
    """Created mutual fund response."""

    asset_id: UUID
    symbol: str
    display_name: str
    asset_type: str
    management_company: str | None = None


class StockCreatedResponse(BaseModel):
    """Created stock response."""

    asset_id: UUID
    symbol: str
    display_name: str
    company_name: str | None = None
    exchange: str | None = None
