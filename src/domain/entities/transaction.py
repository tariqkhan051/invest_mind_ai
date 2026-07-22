"""Transaction entity for immutable investment events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import PortfolioValidationError
from src.domain.enums import TransactionStatus, TransactionType


@dataclass
class Transaction:
    """Immutable investment transaction after confirmation."""

    id: UUID = field(default_factory=uuid4)
    portfolio_id: UUID = field(default_factory=uuid4)
    holding_id: UUID | None = None
    asset_id: UUID = field(default_factory=uuid4)
    transaction_type: TransactionType = TransactionType.BUY
    units: Decimal = Decimal("0")
    price: Decimal = Decimal("0")
    gross_amount: Decimal = Decimal("0")
    fees: Decimal = Decimal("0")
    taxes: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")
    reference_number: str | None = None
    transaction_date: date = field(default_factory=date.today)
    settlement_date: date | None = None
    notes: str | None = None
    source: str = "manual"
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> None:
        """Validate transaction invariants."""
        if self.units < Decimal("0"):
            raise PortfolioValidationError("Transaction units cannot be negative.")
        if self.price < Decimal("0"):
            raise PortfolioValidationError("Transaction price cannot be negative.")
        if self.gross_amount < Decimal("0") and self.transaction_type not in {
            TransactionType.SELL,
            TransactionType.REDEMPTION,
            TransactionType.SWITCH_OUT,
        }:
            raise PortfolioValidationError("Gross amount cannot be negative.")

    def calculate_net_amount(self) -> Decimal:
        """Calculate net amount from gross, fees, and taxes."""
        return self.gross_amount - self.fees - self.taxes

    def confirm(self) -> None:
        """Confirm the transaction and freeze it."""
        self.net_amount = self.calculate_net_amount()
        self.status = TransactionStatus.CONFIRMED
