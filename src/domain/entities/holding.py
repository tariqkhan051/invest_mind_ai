"""Holding entity representing ownership of an asset."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import PortfolioValidationError
from src.domain.enums import AssetType, HoldingStatus


@dataclass
class Holding:
    """Current ownership of one asset within a portfolio."""

    id: UUID = field(default_factory=uuid4)
    portfolio_id: UUID = field(default_factory=uuid4)
    asset_id: UUID = field(default_factory=uuid4)
    asset_type: AssetType = AssetType.MUTUAL_FUND
    quantity: Decimal = Decimal("0")
    average_cost: Decimal = Decimal("0")
    current_price: Decimal = Decimal("0")
    current_value: Decimal = Decimal("0")
    cost_basis: Decimal = Decimal("0")
    unrealized_gain: Decimal = Decimal("0")
    realized_gain: Decimal = Decimal("0")
    allocation_percentage: Decimal = Decimal("0")
    currency: str = "PKR"
    status: HoldingStatus = HoldingStatus.ACTIVE
    last_price_update: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> None:
        """Validate holding invariants."""
        if self.quantity < Decimal("0"):
            raise PortfolioValidationError("Holding quantity cannot be negative.")
        if self.cost_basis < Decimal("0"):
            raise PortfolioValidationError("Cost basis cannot be negative.")
        if self.current_value < Decimal("0"):
            raise PortfolioValidationError("Current value cannot be negative.")
        if self.allocation_percentage < Decimal("0"):
            raise PortfolioValidationError("Allocation percentage cannot be negative.")

    def update_market_value(self, price: Decimal, portfolio_value: Decimal) -> None:
        """Recalculate market value and allocation weight."""
        self.current_price = price
        self.current_value = self.quantity * price
        self.unrealized_gain = self.current_value - self.cost_basis
        if portfolio_value > Decimal("0"):
            self.allocation_percentage = (
                self.current_value / portfolio_value
            ) * Decimal("100")
        else:
            self.allocation_percentage = Decimal("0")
        self.last_price_update = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def close_position(self) -> None:
        """Mark the holding as closed."""
        self.status = HoldingStatus.CLOSED
        self.updated_at = datetime.utcnow()
