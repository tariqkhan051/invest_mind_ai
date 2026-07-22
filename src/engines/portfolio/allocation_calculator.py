"""Portfolio allocation calculations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.domain.entities.holding import Holding
from src.domain.enums import HoldingStatus


@dataclass
class AllocationBreakdown:
    """Allocation percentages grouped by category."""

    by_asset_type: dict[str, Decimal]
    by_holding: dict[str, Decimal]
    cash_percentage: Decimal


def calculate_allocation(
    holdings: list[Holding],
    cash_balance: Decimal,
) -> AllocationBreakdown:
    """Calculate portfolio allocation by asset type and holding."""
    active_holdings = [
        holding
        for holding in holdings
        if holding.status == HoldingStatus.ACTIVE and holding.quantity > Decimal("0")
    ]
    investments_value = sum(
        (holding.current_value for holding in active_holdings), Decimal("0")
    )
    total_value = investments_value + cash_balance

    if total_value <= Decimal("0"):
        return AllocationBreakdown(
            by_asset_type={},
            by_holding={},
            cash_percentage=Decimal("0"),
        )

    by_asset_type: dict[str, Decimal] = {}
    for holding in active_holdings:
        key = holding.asset_type.value
        current = by_asset_type.get(key, Decimal("0"))
        by_asset_type[key] = current + (holding.current_value / total_value) * Decimal(
            "100"
        )

    by_holding = {
        str(holding.asset_id): (holding.current_value / total_value) * Decimal("100")
        for holding in active_holdings
    }

    cash_percentage = (cash_balance / total_value) * Decimal("100")
    if cash_balance > Decimal("0"):
        by_asset_type["cash"] = cash_percentage

    return AllocationBreakdown(
        by_asset_type=by_asset_type,
        by_holding=by_holding,
        cash_percentage=cash_percentage,
    )
