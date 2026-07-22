"""Portfolio engine — coordinates valuation and metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.entities.holding import Holding
from src.domain.entities.portfolio_snapshot import PortfolioSnapshot
from src.domain.entities.transaction import Transaction
from src.engines.portfolio.allocation_calculator import (
    AllocationBreakdown,
    calculate_allocation,
)
from src.engines.portfolio.performance_calculator import (
    build_xirr_cashflows,
    calculate_absolute_return,
    calculate_cagr,
    calculate_xirr,
)


@dataclass
class PortfolioValuation:
    """Current portfolio valuation summary."""

    investment_value: Decimal
    cash_balance: Decimal
    total_value: Decimal
    total_invested: Decimal
    unrealized_gain: Decimal
    realized_gain: Decimal


@dataclass
class PortfolioPerformance:
    """Portfolio performance metrics."""

    absolute_return: Decimal
    percentage_return: Decimal
    xirr: Decimal | None
    cagr: Decimal | None


class PortfolioEngine:
    """Pure calculation engine for portfolio analytics."""

    def calculate_valuation(
        self,
        holdings: list[Holding],
        cash_balance: Decimal,
    ) -> PortfolioValuation:
        """Calculate portfolio value from holdings and cash."""
        investment_value = sum(
            (holding.current_value for holding in holdings), Decimal("0")
        )
        total_invested = sum((holding.cost_basis for holding in holdings), Decimal("0"))
        unrealized_gain = sum(
            (holding.unrealized_gain for holding in holdings), Decimal("0")
        )
        realized_gain = sum(
            (holding.realized_gain for holding in holdings), Decimal("0")
        )
        total_value = investment_value + cash_balance
        return PortfolioValuation(
            investment_value=investment_value,
            cash_balance=cash_balance,
            total_value=total_value,
            total_invested=total_invested,
            unrealized_gain=unrealized_gain,
            realized_gain=realized_gain,
        )

    def calculate_cash_balance(self, transactions: list[Transaction]) -> Decimal:
        """Derive available cash from confirmed transaction flows."""
        from src.domain.enums import TransactionStatus, TransactionType

        outflow_types = {
            TransactionType.BUY,
            TransactionType.MANUAL_INVESTMENT,
            TransactionType.AUTOMATIC_SIP,
            TransactionType.SWITCH_IN,
            TransactionType.FEE,
        }
        inflow_types = {
            TransactionType.SELL,
            TransactionType.REDEMPTION,
            TransactionType.SWITCH_OUT,
            TransactionType.DIVIDEND,
            TransactionType.ADJUSTMENT,
        }

        balance = Decimal("0")
        for transaction in transactions:
            if transaction.status != TransactionStatus.CONFIRMED:
                continue
            amount = transaction.net_amount or transaction.calculate_net_amount()
            if transaction.transaction_type in outflow_types:
                balance -= amount
            elif transaction.transaction_type in inflow_types:
                balance += amount
        return balance

    def calculate_allocation(
        self,
        holdings: list[Holding],
        cash_balance: Decimal,
    ) -> AllocationBreakdown:
        """Calculate allocation breakdown."""
        return calculate_allocation(holdings, cash_balance)

    def calculate_performance(
        self,
        transactions: list[Transaction],
        valuation: PortfolioValuation,
        start_date: date | None,
        as_of: date | None = None,
    ) -> PortfolioPerformance:
        """Calculate return metrics including XIRR and CAGR."""
        as_of = as_of or date.today()
        absolute_return, percentage_return = calculate_absolute_return(
            valuation.total_invested,
            valuation.total_value,
        )
        cashflows = build_xirr_cashflows(
            transactions,
            valuation.total_value,
            as_of,
        )
        xirr = calculate_xirr(cashflows)

        cagr: Decimal | None = None
        if start_date is not None and valuation.total_invested > Decimal("0"):
            cagr = calculate_cagr(
                valuation.total_invested,
                valuation.total_value,
                start_date,
                as_of,
            )

        return PortfolioPerformance(
            absolute_return=absolute_return,
            percentage_return=percentage_return,
            xirr=xirr,
            cagr=cagr,
        )

    def build_snapshot(
        self,
        portfolio_id: UUID,
        valuation: PortfolioValuation,
        performance: PortfolioPerformance,
        allocation: AllocationBreakdown,
        snapshot_date: date | None = None,
    ) -> PortfolioSnapshot:
        """Build a portfolio snapshot from current metrics."""
        return PortfolioSnapshot(
            portfolio_id=portfolio_id,
            snapshot_date=snapshot_date or date.today(),
            total_value=valuation.total_value,
            investment_value=valuation.investment_value,
            cash_value=valuation.cash_balance,
            xirr=performance.xirr,
            cagr=performance.cagr,
            allocation_json=dict(allocation.by_asset_type),
        )
