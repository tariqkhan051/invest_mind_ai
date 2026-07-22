"""Stock entity extending the asset concept."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.core.exceptions import PortfolioValidationError
from src.domain.entities.asset import Asset


@dataclass
class Stock:
    """PSX stock-specific attributes linked to an asset."""

    asset_id: UUID
    asset: Asset
    isin: str | None = None
    company_name: str | None = None
    sector_id: UUID | None = None
    industry: str | None = None
    market_cap: Decimal | None = None
    free_float: Decimal | None = None
    shares_outstanding: Decimal | None = None
    eps: Decimal | None = None
    pe: Decimal | None = None
    pbv: Decimal | None = None
    roe: Decimal | None = None
    roa: Decimal | None = None
    debt_ratio: Decimal | None = None
    dividend_yield: Decimal | None = None
    last_financial_update: datetime | None = None

    def validate(self) -> None:
        """Validate stock invariants."""
        self.asset.validate()
        if self.market_cap is not None and self.market_cap < Decimal("0"):
            raise PortfolioValidationError("Market cap cannot be negative.")
