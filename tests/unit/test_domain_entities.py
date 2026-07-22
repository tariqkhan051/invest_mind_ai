"""Unit tests for domain entities."""

from decimal import Decimal

import pytest

from src.core.exceptions import PortfolioValidationError
from src.domain.entities.asset import Asset
from src.domain.entities.holding import Holding
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.transaction import Transaction
from src.domain.enums import TransactionType


def test_portfolio_validate_rejects_negative_sip() -> None:
    """Portfolio monthly SIP cannot be negative."""
    portfolio = Portfolio(monthly_sip=Decimal("-1"))
    with pytest.raises(PortfolioValidationError):
        portfolio.validate()


def test_holding_validate_rejects_negative_quantity() -> None:
    """Holding quantity cannot be negative."""
    holding = Holding(quantity=Decimal("-1"))
    with pytest.raises(PortfolioValidationError):
        holding.validate()


def test_transaction_confirm_sets_net_amount() -> None:
    """Confirming a transaction should compute net amount."""
    transaction = Transaction(
        gross_amount=Decimal("10000"),
        fees=Decimal("100"),
        taxes=Decimal("50"),
        transaction_type=TransactionType.BUY,
    )
    transaction.confirm()
    assert transaction.net_amount == Decimal("9850")


def test_asset_requires_symbol_and_name() -> None:
    """Asset validation should require symbol and display name."""
    with pytest.raises(PortfolioValidationError):
        Asset(symbol="", display_name="").validate()


def test_holding_update_market_value() -> None:
    """Holding market value and allocation should update from price."""
    holding = Holding(quantity=Decimal("100"), cost_basis=Decimal("8000"))
    holding.update_market_value(Decimal("100"), Decimal("10000"))
    assert holding.current_value == Decimal("10000")
    assert holding.allocation_percentage == Decimal("100")
    assert holding.unrealized_gain == Decimal("2000")
