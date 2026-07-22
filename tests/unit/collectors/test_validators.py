"""Unit tests for collector validators."""

from datetime import date, timedelta
from decimal import Decimal

from src.collectors.base.models import MacroIndicatorRecord, NavRecord, PriceRecord
from src.collectors.base.validator import (
    validate_macro_record,
    validate_nav_record,
    validate_price_record,
)


def test_validate_nav_record_rejects_future_date() -> None:
    """Future NAV dates should fail validation."""
    future = date.today() + timedelta(days=1)
    errors = validate_nav_record(
        NavRecord(symbol="MIF", nav_date=future, nav=Decimal("50"), source="test")
    )
    assert errors


def test_validate_price_record_requires_positive_close() -> None:
    """Close price must be positive."""
    errors = validate_price_record(
        PriceRecord(
            symbol="MARI",
            price_date=date.today(),
            close_price=Decimal("0"),
            source="test",
        )
    )
    assert errors


def test_validate_macro_record_requires_name() -> None:
    """Macro indicator name is required."""
    errors = validate_macro_record(
        MacroIndicatorRecord(
            indicator_name="",
            release_date=date.today(),
            actual_value=Decimal("22.5"),
            source="sbp",
        )
    )
    assert errors
