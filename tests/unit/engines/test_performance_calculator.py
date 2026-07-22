"""Unit tests for portfolio performance calculations."""

from datetime import date
from decimal import Decimal

from src.engines.portfolio.performance_calculator import (
    calculate_absolute_return,
    calculate_cagr,
    calculate_xirr,
)


def test_calculate_absolute_return() -> None:
    """Absolute and percentage return should be computed correctly."""
    absolute, percentage = calculate_absolute_return(
        Decimal("100000"),
        Decimal("120000"),
    )
    assert absolute == Decimal("20000")
    assert percentage == Decimal("20")


def test_calculate_cagr() -> None:
    """CAGR should annualize growth over the period."""
    result = calculate_cagr(
        Decimal("100000"),
        Decimal("121000"),
        date(2024, 1, 1),
        date(2025, 1, 1),
    )
    assert result is not None
    assert result > Decimal("20")
    assert result < Decimal("22")


def test_calculate_xirr_simple_investment() -> None:
    """XIRR should solve for a simple one-year investment."""
    cashflows = [
        (date(2024, 1, 1), Decimal("-100000")),
        (date(2025, 1, 1), Decimal("115000")),
    ]
    result = calculate_xirr(cashflows)
    assert result is not None
    assert result > Decimal("14")
    assert result < Decimal("16")
