"""Portfolio performance metrics — XIRR, CAGR, returns."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scipy.optimize import brentq

from src.domain.entities.transaction import Transaction
from src.domain.enums import TransactionStatus, TransactionType


def calculate_absolute_return(
    total_invested: Decimal, current_value: Decimal
) -> tuple[Decimal, Decimal]:
    """Return absolute and percentage return."""
    absolute = current_value - total_invested
    if total_invested == Decimal("0"):
        return absolute, Decimal("0")
    percentage = (absolute / total_invested) * Decimal("100")
    return absolute, percentage


def calculate_cagr(
    beginning_value: Decimal,
    ending_value: Decimal,
    start_date: date,
    end_date: date,
) -> Decimal | None:
    """Calculate compound annual growth rate as a percentage."""
    if beginning_value <= Decimal("0") or ending_value <= Decimal("0"):
        return None
    days = (end_date - start_date).days
    if days <= 0:
        return None
    years = Decimal(days) / Decimal("365.25")
    if years == Decimal("0"):
        return None
    ratio = ending_value / beginning_value
    cagr = (ratio ** (Decimal("1") / years)) - Decimal("1")
    return cagr * Decimal("100")


def calculate_xirr(
    cashflows: list[tuple[date, Decimal]],
) -> Decimal | None:
    """Calculate annualized XIRR as a percentage.

    Cashflows use negative amounts for investments and positive for withdrawals
    or terminal portfolio value.
    """
    if len(cashflows) < 2:
        return None

    start_date = min(flow_date for flow_date, _ in cashflows)
    flow_data = [
        (float(amount), (flow_date - start_date).days / 365.25)
        for flow_date, amount in cashflows
    ]

    def net_present_value(rate: float) -> float:
        return float(sum(amount / ((1 + rate) ** years) for amount, years in flow_data))

    try:
        rate = float(brentq(net_present_value, -0.9999, 10.0))
    except ValueError:
        return None
    return Decimal(str(rate * 100))


def build_xirr_cashflows(
    transactions: list[Transaction],
    terminal_value: Decimal,
    as_of: date,
) -> list[tuple[date, Decimal]]:
    """Build cashflow series from confirmed transactions and terminal value."""
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
    }

    cashflows: list[tuple[date, Decimal]] = []
    for transaction in transactions:
        if transaction.status != TransactionStatus.CONFIRMED:
            continue
        amount = transaction.net_amount or transaction.calculate_net_amount()
        if transaction.transaction_type in outflow_types:
            cashflows.append((transaction.transaction_date, -amount))
        elif transaction.transaction_type in inflow_types:
            cashflows.append((transaction.transaction_date, amount))

    if terminal_value > Decimal("0"):
        cashflows.append((as_of, terminal_value))
    return cashflows
