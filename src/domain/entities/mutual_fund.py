"""Mutual fund entity extending the asset concept."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.core.exceptions import PortfolioValidationError
from src.domain.entities.asset import Asset


@dataclass
class MutualFund:
    """Mutual fund-specific attributes linked to an asset."""

    asset_id: UUID
    asset: Asset
    management_company: str | None = None
    fund_category_id: UUID | None = None
    benchmark_id: UUID | None = None
    expense_ratio: Decimal | None = None
    front_load: Decimal | None = None
    back_load: Decimal | None = None
    management_fee: Decimal | None = None
    minimum_investment: Decimal | None = None
    minimum_sip: Decimal | None = None
    aum: Decimal | None = None
    cash_percentage: Decimal | None = None
    equity_percentage: Decimal | None = None
    debt_percentage: Decimal | None = None
    dividend_policy: str | None = None
    dividend_frequency: str | None = None
    website: str | None = None
    factsheet_url: str | None = None
    prospectus_url: str | None = None
    last_nav_update: datetime | None = None

    def validate(self) -> None:
        """Validate mutual fund invariants."""
        self.asset.validate()
        if self.expense_ratio is not None and self.expense_ratio < Decimal("0"):
            raise PortfolioValidationError("Expense ratio cannot be negative.")
        if self.aum is not None and self.aum < Decimal("0"):
            raise PortfolioValidationError("AUM cannot be negative.")
