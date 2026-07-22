"""Percentage value object."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.core.exceptions import PortfolioValidationError


@dataclass(frozen=True, slots=True)
class Percentage:
    """Immutable percentage value between 0 and 100."""

    value: Decimal

    def __post_init__(self) -> None:
        decimal_value = Decimal(self.value)
        if decimal_value < Decimal("0") or decimal_value > Decimal("100"):
            raise PortfolioValidationError(
                "Percentage must be between 0 and 100 inclusive."
            )
        object.__setattr__(self, "value", decimal_value)

    def as_fraction(self) -> Decimal:
        """Return the percentage as a decimal fraction."""
        return self.value / Decimal("100")

    @classmethod
    def from_fraction(cls, fraction: Decimal) -> Percentage:
        """Create a percentage from a decimal fraction."""
        return cls(fraction * Decimal("100"))
