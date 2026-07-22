"""Investment goal entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import PortfolioValidationError
from src.domain.enums import GoalStatus, RiskProfile


@dataclass
class InvestmentGoal:
    """Financial goal linked to a portfolio."""

    id: UUID = field(default_factory=uuid4)
    portfolio_id: UUID = field(default_factory=uuid4)
    name: str = ""
    target_amount: Decimal = Decimal("0")
    current_amount: Decimal = Decimal("0")
    target_date: date | None = None
    monthly_contribution: Decimal = Decimal("0")
    priority: int = 1
    risk_preference: RiskProfile = RiskProfile.MODERATE
    status: GoalStatus = GoalStatus.ACTIVE
    notes: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> None:
        """Validate goal invariants."""
        if not self.name.strip():
            raise PortfolioValidationError("Goal name cannot be empty.")
        if self.target_amount <= Decimal("0"):
            raise PortfolioValidationError("Target amount must be positive.")
        if self.current_amount < Decimal("0"):
            raise PortfolioValidationError("Current amount cannot be negative.")
