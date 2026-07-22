"""Recalculate holdings from confirmed transactions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.core.exceptions import PortfolioValidationError
from src.domain.entities.holding import Holding
from src.domain.entities.transaction import Transaction
from src.domain.enums import (
    AssetType,
    HoldingStatus,
    TransactionStatus,
    TransactionType,
)


@dataclass
class HoldingCalculationResult:
    """Result of rebuilding a holding from transactions."""

    holding: Holding


BUY_TYPES = {
    TransactionType.BUY,
    TransactionType.MANUAL_INVESTMENT,
    TransactionType.AUTOMATIC_SIP,
    TransactionType.SWITCH_IN,
    TransactionType.BONUS,
}

SELL_TYPES = {
    TransactionType.SELL,
    TransactionType.REDEMPTION,
    TransactionType.SWITCH_OUT,
}


def calculate_holding_from_transactions(
    portfolio_id: UUID,
    asset_id: UUID,
    asset_type: AssetType,
    transactions: list[Transaction],
    current_price: Decimal,
    portfolio_value: Decimal,
    currency: str = "PKR",
    existing_holding: Holding | None = None,
) -> HoldingCalculationResult:
    """Rebuild a holding state from confirmed transactions.

    Holdings are derived from transactions and must not be edited directly.
    See docs/12_PORTFOLIO_ENGINE.md §6–7.
    """
    confirmed = sorted(
        [
            transaction
            for transaction in transactions
            if transaction.status == TransactionStatus.CONFIRMED
            and transaction.asset_id == asset_id
        ],
        key=lambda item: (item.transaction_date, item.created_at),
    )

    holding = existing_holding or Holding(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        asset_type=asset_type,
        currency=currency,
    )

    quantity = Decimal("0")
    cost_basis = Decimal("0")
    realized_gain = Decimal("0")
    average_cost = Decimal("0")

    for transaction in confirmed:
        if transaction.transaction_type in BUY_TYPES:
            buy_units = transaction.units
            if buy_units <= Decimal("0"):
                continue
            buy_cost = transaction.net_amount or transaction.calculate_net_amount()
            new_quantity = quantity + buy_units
            if new_quantity > Decimal("0"):
                cost_basis += buy_cost
                average_cost = cost_basis / new_quantity
            quantity = new_quantity

        elif transaction.transaction_type in SELL_TYPES:
            sell_units = transaction.units
            if sell_units <= Decimal("0"):
                continue
            if sell_units > quantity:
                raise PortfolioValidationError(
                    "Cannot sell more units than currently held."
                )
            sell_proceeds = transaction.net_amount or transaction.calculate_net_amount()
            cost_of_sold = average_cost * sell_units
            realized_gain += sell_proceeds - cost_of_sold
            quantity -= sell_units
            cost_basis -= cost_of_sold
            if quantity > Decimal("0"):
                average_cost = cost_basis / quantity
            else:
                average_cost = Decimal("0")
                cost_basis = Decimal("0")

        elif transaction.transaction_type == TransactionType.DIVIDEND:
            realized_gain += (
                transaction.net_amount or transaction.calculate_net_amount()
            )

    holding.quantity = quantity
    holding.average_cost = average_cost
    holding.cost_basis = cost_basis
    holding.realized_gain = realized_gain
    holding.current_price = current_price
    holding.current_value = quantity * current_price
    holding.unrealized_gain = holding.current_value - cost_basis
    holding.status = (
        HoldingStatus.ACTIVE if quantity > Decimal("0") else HoldingStatus.CLOSED
    )

    if portfolio_value > Decimal("0") and holding.status == HoldingStatus.ACTIVE:
        holding.allocation_percentage = (
            holding.current_value / portfolio_value
        ) * Decimal("100")
    else:
        holding.allocation_percentage = Decimal("0")

    holding.validate()
    return HoldingCalculationResult(holding=holding)
