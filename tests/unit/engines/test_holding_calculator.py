"""Unit tests for holding calculator."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.transaction import Transaction
from src.domain.enums import AssetType, TransactionStatus, TransactionType
from src.engines.portfolio.holding_calculator import calculate_holding_from_transactions


def test_holding_calculated_from_buy_transactions() -> None:
    """Holdings should be derived from confirmed buy transactions."""
    portfolio_id = uuid4()
    asset_id = uuid4()
    transactions = [
        Transaction(
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            transaction_type=TransactionType.BUY,
            units=Decimal("100"),
            price=Decimal("50"),
            gross_amount=Decimal("5000"),
            status=TransactionStatus.CONFIRMED,
            net_amount=Decimal("5000"),
            transaction_date=date(2024, 1, 1),
        ),
        Transaction(
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            transaction_type=TransactionType.BUY,
            units=Decimal("50"),
            price=Decimal("60"),
            gross_amount=Decimal("3000"),
            status=TransactionStatus.CONFIRMED,
            net_amount=Decimal("3000"),
            transaction_date=date(2024, 6, 1),
        ),
    ]

    result = calculate_holding_from_transactions(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        asset_type=AssetType.MUTUAL_FUND,
        transactions=transactions,
        current_price=Decimal("65"),
        portfolio_value=Decimal("9750"),
    )

    assert result.holding.quantity == Decimal("150")
    assert result.holding.cost_basis == Decimal("8000")
    assert result.holding.current_value == Decimal("9750")
