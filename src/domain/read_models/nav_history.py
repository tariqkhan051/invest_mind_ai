"""NAV history read model for queries and analysis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class NavHistoryPoint:
    """Single NAV observation."""

    nav_date: date
    nav: Decimal
    daily_return: Decimal | None = None
    offer_price: Decimal | None = None
    repurchase_price: Decimal | None = None
    fytd_return: Decimal | None = None
    mtd_return: Decimal | None = None
    category: str | None = None
    source: str | None = None
