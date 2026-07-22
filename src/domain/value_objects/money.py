"""Money value object representing a currency amount."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.core.exceptions import PortfolioValidationError


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary amount with currency."""

    amount: Decimal
    currency: str = "PKR"

    def __post_init__(self) -> None:
        if self.currency.strip() == "":
            raise PortfolioValidationError("Currency cannot be empty.")
        object.__setattr__(self, "amount", Decimal(self.amount))

    def is_negative(self) -> bool:
        """Return True when the amount is below zero."""
        return self.amount < Decimal("0")

    def is_zero(self) -> bool:
        """Return True when the amount is zero."""
        return self.amount == Decimal("0")

    def add(self, other: Money) -> Money:
        """Add two money values in the same currency."""
        self._ensure_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: Money) -> Money:
        """Subtract two money values in the same currency."""
        self._ensure_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def multiply(self, factor: Decimal) -> Money:
        """Multiply the amount by a scalar factor."""
        return Money(self.amount * Decimal(factor), self.currency)

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise PortfolioValidationError(
                f"Currency mismatch: {self.currency} vs {other.currency}."
            )
