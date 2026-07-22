"""Portfolio aggregate root entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.core.exceptions import PortfolioValidationError
from src.domain.enums import (
    InvestmentHorizon,
    InvestmentObjective,
    InvestmentPreference,
    PortfolioStatus,
    RiskProfile,
)


@dataclass
class Portfolio:
    """Represents a user's investment portfolio."""

    id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)
    name: str = "Primary Portfolio"
    description: str | None = None
    base_currency: str = "PKR"
    risk_profile: RiskProfile = RiskProfile.AGGRESSIVE
    investment_preference: InvestmentPreference = InvestmentPreference.SHARIAH_COMPLIANT
    investment_objective: InvestmentObjective = InvestmentObjective.WEALTH_CREATION
    investment_horizon: InvestmentHorizon = InvestmentHorizon.LONG
    monthly_sip: Decimal = Decimal("50000")
    status: PortfolioStatus = PortfolioStatus.ACTIVE
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def validate(self) -> None:
        """Validate portfolio invariants."""
        if not self.name.strip():
            raise PortfolioValidationError("Portfolio name cannot be empty.")
        if self.monthly_sip < Decimal("0"):
            raise PortfolioValidationError("Monthly SIP cannot be negative.")
        if not self.base_currency.strip():
            raise PortfolioValidationError("Base currency is required.")

    def archive(self) -> None:
        """Archive the portfolio."""
        self.status = PortfolioStatus.ARCHIVED
        self.version += 1
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the portfolio."""
        self.status = PortfolioStatus.ACTIVE
        self.version += 1
        self.updated_at = datetime.utcnow()
