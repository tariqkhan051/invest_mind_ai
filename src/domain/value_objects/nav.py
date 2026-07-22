"""NAV value object for mutual funds."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.core.exceptions import PortfolioValidationError


@dataclass(frozen=True, slots=True)
class NAV:
    """Immutable net asset value for a fund on a given date."""

    value: Decimal
    nav_date: date
    currency: str = "PKR"

    def __post_init__(self) -> None:
        decimal_value = Decimal(self.value)
        if decimal_value <= Decimal("0"):
            raise PortfolioValidationError("NAV must be greater than zero.")
        object.__setattr__(self, "value", decimal_value)
