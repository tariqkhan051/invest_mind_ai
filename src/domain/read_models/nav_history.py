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
