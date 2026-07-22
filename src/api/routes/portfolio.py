"""Portfolio API routes — docs/18_API.md §5 and docs/12_PORTFOLIO_ENGINE.md §19."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_portfolio_service
from src.api.schemas import ApiResponse
from src.api.schemas.portfolio import (
    AllocationResponse,
    CreatePortfolioRequest,
    CreateTransactionRequest,
    HoldingResponse,
    PerformanceResponse,
    PortfolioResponse,
    PortfolioSummaryResponse,
    SnapshotResponse,
    TransactionListResponse,
    TransactionResponse,
)
from src.core.constants import DEFAULT_PAGE_SIZE
from src.domain.entities.holding import Holding
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.portfolio_snapshot import PortfolioSnapshot
from src.domain.entities.transaction import Transaction
from src.engines.portfolio.engine import PortfolioPerformance
from src.services.portfolio_service import (
    PaginatedTransactions,
    PortfolioService,
    PortfolioSummary,
    RecordTransactionCommand,
)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


def _map_portfolio(portfolio: Portfolio) -> PortfolioResponse:
    return PortfolioResponse(
        id=portfolio.id,
        name=portfolio.name,
        description=portfolio.description,
        base_currency=portfolio.base_currency,
        risk_profile=portfolio.risk_profile.value,
        investment_preference=portfolio.investment_preference.value,
        monthly_sip=portfolio.monthly_sip,
        status=portfolio.status.value,
    )


def _map_holding(holding: Holding) -> HoldingResponse:
    return HoldingResponse(
        id=holding.id,
        asset_id=holding.asset_id,
        asset_type=holding.asset_type.value,
        quantity=holding.quantity,
        average_cost=holding.average_cost,
        current_price=holding.current_price,
        current_value=holding.current_value,
        cost_basis=holding.cost_basis,
        unrealized_gain=holding.unrealized_gain,
        realized_gain=holding.realized_gain,
        allocation_percentage=holding.allocation_percentage,
        currency=holding.currency,
        status=holding.status.value,
    )


def _map_transaction(transaction: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        portfolio_id=transaction.portfolio_id,
        holding_id=transaction.holding_id,
        asset_id=transaction.asset_id,
        transaction_type=transaction.transaction_type.value,
        units=transaction.units,
        price=transaction.price,
        gross_amount=transaction.gross_amount,
        fees=transaction.fees,
        taxes=transaction.taxes,
        net_amount=transaction.net_amount,
        reference_number=transaction.reference_number,
        transaction_date=transaction.transaction_date,
        settlement_date=transaction.settlement_date,
        notes=transaction.notes,
        source=transaction.source,
        status=transaction.status.value,
        created_at=transaction.created_at,
    )


def _map_snapshot(snapshot: PortfolioSnapshot) -> SnapshotResponse:
    return SnapshotResponse(
        id=snapshot.id,
        portfolio_id=snapshot.portfolio_id,
        snapshot_date=snapshot.snapshot_date,
        total_value=snapshot.total_value,
        investment_value=snapshot.investment_value,
        cash_value=snapshot.cash_value,
        xirr=snapshot.xirr,
        cagr=snapshot.cagr,
        allocation=snapshot.allocation_json,
        created_at=snapshot.created_at,
    )


def _map_summary(summary: PortfolioSummary) -> PortfolioSummaryResponse:
    return PortfolioSummaryResponse(
        portfolio=_map_portfolio(summary.portfolio),
        portfolio_value=summary.valuation.total_value,
        cash=summary.valuation.cash_balance,
        investment_value=summary.valuation.investment_value,
        total_invested=summary.valuation.total_invested,
        total_return=summary.performance.absolute_return,
        total_return_percentage=summary.performance.percentage_return,
        unrealized_gain=summary.valuation.unrealized_gain,
        realized_gain=summary.valuation.realized_gain,
        xirr=summary.performance.xirr,
        cagr=summary.performance.cagr,
        allocation=AllocationResponse(
            by_asset_type=summary.allocation.by_asset_type,
            by_holding=summary.allocation.by_holding,
            cash_percentage=summary.allocation.cash_percentage,
        ),
    )


def _map_performance(performance: PortfolioPerformance) -> PerformanceResponse:
    return PerformanceResponse(
        absolute_return=performance.absolute_return,
        percentage_return=performance.percentage_return,
        xirr=performance.xirr,
        cagr=performance.cagr,
    )


def _map_transaction_page(page: PaginatedTransactions) -> TransactionListResponse:
    return TransactionListResponse(
        items=[_map_transaction(item) for item in page.items],
        page=page.page,
        page_size=page.page_size,
        total_items=page.total_items,
        total_pages=page.total_pages,
    )


@router.get("", response_model=ApiResponse[PortfolioSummaryResponse])
def get_portfolio_summary(
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[PortfolioSummaryResponse]:
    """Return portfolio summary with value, returns, and allocation."""
    summary = service.get_summary()
    return ApiResponse(
        message="Portfolio summary retrieved",
        data=_map_summary(summary),
    )


@router.get("/summary", response_model=ApiResponse[PortfolioSummaryResponse])
def get_portfolio_summary_alias(
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[PortfolioSummaryResponse]:
    """Return portfolio summary (alias endpoint)."""
    summary = service.get_summary()
    return ApiResponse(
        message="Portfolio summary retrieved",
        data=_map_summary(summary),
    )


@router.post("", response_model=ApiResponse[PortfolioResponse])
def create_portfolio(
    request: CreatePortfolioRequest,
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[PortfolioResponse]:
    """Create a new portfolio."""
    portfolio = service.create_portfolio(
        name=request.name,
        description=request.description,
    )
    return ApiResponse(
        message="Portfolio created",
        data=_map_portfolio(portfolio),
    )


@router.get("/holdings", response_model=ApiResponse[list[HoldingResponse]])
def get_holdings(
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[list[HoldingResponse]]:
    """Return current portfolio holdings."""
    holdings = service.get_holdings()
    return ApiResponse(
        message="Holdings retrieved",
        data=[_map_holding(holding) for holding in holdings],
    )


@router.get("/transactions", response_model=ApiResponse[TransactionListResponse])
def get_transactions(
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PAGE_SIZE,
) -> ApiResponse[TransactionListResponse]:
    """Return paginated portfolio transactions."""
    transactions = service.get_transactions(page=page, page_size=page_size)
    return ApiResponse(
        message="Transactions retrieved",
        data=_map_transaction_page(transactions),
    )


@router.post("/transactions", response_model=ApiResponse[TransactionResponse])
def create_transaction(
    request: CreateTransactionRequest,
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[TransactionResponse]:
    """Record a new portfolio transaction."""
    command = RecordTransactionCommand(
        asset_id=request.asset_id,
        transaction_type=request.transaction_type,
        units=request.units,
        price=request.price,
        gross_amount=request.gross_amount,
        fees=request.fees,
        taxes=request.taxes,
        transaction_date=request.transaction_date,
        reference_number=request.reference_number,
        notes=request.notes,
        source=request.source,
    )
    transaction = service.record_transaction(command)
    return ApiResponse(
        message="Transaction recorded",
        data=_map_transaction(transaction),
    )


@router.get("/snapshots", response_model=ApiResponse[list[SnapshotResponse]])
def get_snapshots(
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[list[SnapshotResponse]]:
    """Return portfolio snapshots."""
    snapshots = service.get_snapshots()
    return ApiResponse(
        message="Snapshots retrieved",
        data=[_map_snapshot(snapshot) for snapshot in snapshots],
    )


@router.post("/snapshots", response_model=ApiResponse[SnapshotResponse])
def create_snapshot(
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[SnapshotResponse]:
    """Generate and store a portfolio snapshot."""
    snapshot = service.generate_snapshot()
    return ApiResponse(
        message="Snapshot generated",
        data=_map_snapshot(snapshot),
    )


@router.get("/performance", response_model=ApiResponse[PerformanceResponse])
def get_performance(
    service: Annotated[PortfolioService, Depends(get_portfolio_service)],
) -> ApiResponse[PerformanceResponse]:
    """Return portfolio performance metrics."""
    performance = service.get_performance()
    return ApiResponse(
        message="Performance metrics retrieved",
        data=_map_performance(performance),
    )
