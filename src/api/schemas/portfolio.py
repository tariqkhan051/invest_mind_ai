"""Portfolio API request and response schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.enums import TransactionType


class PortfolioResponse(BaseModel):
    """Portfolio metadata."""

    id: UUID
    name: str
    description: str | None
    base_currency: str
    risk_profile: str
    investment_preference: str
    monthly_sip: Decimal
    status: str


class AllocationResponse(BaseModel):
    """Allocation breakdown."""

    by_asset_type: dict[str, Decimal]
    by_holding: dict[str, Decimal]
    cash_percentage: Decimal


class PortfolioSummaryResponse(BaseModel):
    """Portfolio summary with valuation and performance."""

    portfolio: PortfolioResponse
    portfolio_value: Decimal
    cash: Decimal
    investment_value: Decimal
    total_invested: Decimal
    total_return: Decimal
    total_return_percentage: Decimal
    unrealized_gain: Decimal
    realized_gain: Decimal
    xirr: Decimal | None
    cagr: Decimal | None
    allocation: AllocationResponse


class HoldingResponse(BaseModel):
    """Portfolio holding details."""

    id: UUID
    asset_id: UUID
    asset_type: str
    quantity: Decimal
    average_cost: Decimal
    current_price: Decimal
    current_value: Decimal
    cost_basis: Decimal
    unrealized_gain: Decimal
    realized_gain: Decimal
    allocation_percentage: Decimal
    currency: str
    status: str


class TransactionResponse(BaseModel):
    """Portfolio transaction details."""

    id: UUID
    portfolio_id: UUID
    holding_id: UUID | None
    asset_id: UUID
    transaction_type: str
    units: Decimal
    price: Decimal
    gross_amount: Decimal
    fees: Decimal
    taxes: Decimal
    net_amount: Decimal
    reference_number: str | None
    transaction_date: date
    settlement_date: date | None
    notes: str | None
    source: str
    status: str
    created_at: datetime


class CreateTransactionRequest(BaseModel):
    """Request body for recording a transaction."""

    asset_id: UUID
    transaction_type: TransactionType
    units: Decimal = Field(ge=0)
    price: Decimal = Field(ge=0)
    gross_amount: Decimal | None = None
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    taxes: Decimal = Field(default=Decimal("0"), ge=0)
    transaction_date: date | None = None
    reference_number: str | None = None
    notes: str | None = None
    source: str = "manual"


class CreatePortfolioRequest(BaseModel):
    """Request body for creating a portfolio."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class SnapshotResponse(BaseModel):
    """Portfolio snapshot details."""

    id: UUID
    portfolio_id: UUID
    snapshot_date: date
    total_value: Decimal
    investment_value: Decimal
    cash_value: Decimal
    xirr: Decimal | None
    cagr: Decimal | None
    allocation: dict[str, Decimal] | None
    created_at: datetime


class PerformanceResponse(BaseModel):
    """Portfolio performance metrics."""

    absolute_return: Decimal
    percentage_return: Decimal
    xirr: Decimal | None
    cagr: Decimal | None


class TransactionListResponse(BaseModel):
    """Paginated transaction list."""

    items: list[TransactionResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int
