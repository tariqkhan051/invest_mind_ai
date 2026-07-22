"""Unit tests for domain value objects."""

from datetime import date
from decimal import Decimal

import pytest

from src.core.exceptions import PortfolioValidationError
from src.domain.value_objects.money import Money
from src.domain.value_objects.nav import NAV
from src.domain.value_objects.percentage import Percentage
from src.domain.value_objects.price import Price


def test_money_add_same_currency() -> None:
    """Money addition should work for matching currencies."""
    total = Money(Decimal("1000"), "PKR").add(Money(Decimal("500"), "PKR"))
    assert total.amount == Decimal("1500")


def test_money_rejects_currency_mismatch() -> None:
    """Money operations should reject different currencies."""
    with pytest.raises(PortfolioValidationError):
        Money(Decimal("100"), "PKR").add(Money(Decimal("50"), "USD"))


def test_percentage_valid_range() -> None:
    """Valid percentages should be accepted."""
    assert Percentage(Decimal("75.5")).value == Decimal("75.5")


def test_percentage_rejects_out_of_range() -> None:
    """Percentages outside 0-100 should be rejected."""
    with pytest.raises(PortfolioValidationError):
        Percentage(Decimal("101"))


def test_nav_must_be_positive() -> None:
    """NAV must be greater than zero."""
    with pytest.raises(PortfolioValidationError):
        NAV(Decimal("0"), date.today())


def test_price_must_be_positive() -> None:
    """Price must be greater than zero."""
    with pytest.raises(PortfolioValidationError):
        Price(Decimal("-1"), date.today())
