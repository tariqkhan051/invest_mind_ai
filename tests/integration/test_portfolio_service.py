"""Integration tests for portfolio service."""

from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.core.exceptions import PortfolioValidationError
from src.domain.entities.asset import Asset
from src.domain.enums import AssetType, TransactionType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.portfolio_repository import (
    SqlAlchemyPortfolioRepository,
)
from src.services.portfolio_service import PortfolioService, RecordTransactionCommand


@pytest.fixture
def portfolio_service(db_session: Session, test_settings: Settings) -> PortfolioService:
    """Provide a portfolio service backed by the test database."""
    return PortfolioService(
        portfolio_repository=SqlAlchemyPortfolioRepository(db_session),
        asset_repository=SqlAlchemyAssetRepository(db_session),
        settings=test_settings,
    )


@pytest.fixture
def sample_asset(db_session: Session) -> Asset:
    """Create a sample mutual fund asset."""
    repository = SqlAlchemyAssetRepository(db_session)
    return repository.save(
        Asset(
            symbol="MIF",
            display_name="Meezan Islamic Fund",
            asset_type=AssetType.MUTUAL_FUND,
        )
    )


def test_record_transaction_updates_holdings(
    portfolio_service: PortfolioService,
    sample_asset: Asset,
) -> None:
    """Recording a buy should create holdings from transactions."""
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=sample_asset.id,
            transaction_type=TransactionType.ADJUSTMENT,
            units=Decimal("0"),
            price=Decimal("0"),
            gross_amount=Decimal("10000"),
        )
    )
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=sample_asset.id,
            transaction_type=TransactionType.BUY,
            units=Decimal("100"),
            price=Decimal("50"),
        )
    )

    holdings = portfolio_service.get_holdings()
    assert len(holdings) == 1
    assert holdings[0].quantity == Decimal("100")
    assert holdings[0].current_value == Decimal("5000")


def test_get_summary_includes_metrics(
    portfolio_service: PortfolioService,
    sample_asset: Asset,
) -> None:
    """Portfolio summary should include valuation and allocation."""
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=sample_asset.id,
            transaction_type=TransactionType.ADJUSTMENT,
            units=Decimal("0"),
            price=Decimal("0"),
            gross_amount=Decimal("5000"),
        )
    )
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=sample_asset.id,
            transaction_type=TransactionType.BUY,
            units=Decimal("100"),
            price=Decimal("50"),
        )
    )

    summary = portfolio_service.get_summary()
    assert summary.valuation.investment_value == Decimal("5000")
    assert summary.valuation.total_value == Decimal("5000")
    assert AssetType.MUTUAL_FUND.value in summary.allocation.by_asset_type


def test_rejects_negative_cash_balance(
    portfolio_service: PortfolioService,
    sample_asset: Asset,
) -> None:
    """Buys without cash deposit should be rejected."""
    with pytest.raises(PortfolioValidationError):
        portfolio_service.record_transaction(
            RecordTransactionCommand(
                asset_id=sample_asset.id,
                transaction_type=TransactionType.BUY,
                units=Decimal("10"),
                price=Decimal("50"),
            )
        )


def test_generate_snapshot(
    portfolio_service: PortfolioService,
    sample_asset: Asset,
) -> None:
    """Snapshot generation should persist portfolio state."""
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=sample_asset.id,
            transaction_type=TransactionType.ADJUSTMENT,
            units=Decimal("0"),
            price=Decimal("0"),
            gross_amount=Decimal("5000"),
        )
    )
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=sample_asset.id,
            transaction_type=TransactionType.BUY,
            units=Decimal("100"),
            price=Decimal("50"),
        )
    )

    snapshot = portfolio_service.generate_snapshot()
    assert snapshot.total_value == Decimal("5000")
    snapshots = portfolio_service.get_snapshots()
    assert len(snapshots) == 1
