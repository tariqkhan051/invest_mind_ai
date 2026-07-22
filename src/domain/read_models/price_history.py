"""Price history read model for queries and analysis."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PriceHistoryPoint:
    """Single price observation for a stock."""

    price_date: date
    close_price: Decimal
    open_price: Decimal | None = None
    high_price: Decimal | None = None
    low_price: Decimal | None = None
    adjusted_close: Decimal | None = None
    volume: Decimal | None = None
