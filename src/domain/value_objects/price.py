"""Price value object for market instruments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.core.exceptions import PortfolioValidationError


@dataclass(frozen=True, slots=True)
class Price:
    """Immutable market price for an asset on a given date."""

    value: Decimal
    price_date: date
    currency: str = "PKR"

    def __post_init__(self) -> None:
        decimal_value = Decimal(self.value)
        if decimal_value <= Decimal("0"):
            raise PortfolioValidationError("Price must be greater than zero.")
        object.__setattr__(self, "value", decimal_value)
