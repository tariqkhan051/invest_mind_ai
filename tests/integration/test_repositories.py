"""Integration tests for SQLAlchemy repositories."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from src.domain.entities.asset import Asset
from src.domain.entities.holding import Holding
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.transaction import Transaction
from src.domain.enums import (
    AssetType,
    PortfolioStatus,
    TransactionStatus,
    TransactionType,
)
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.portfolio_repository import (
    SqlAlchemyPortfolioRepository,
)


def test_portfolio_repository_save_and_load(db_session: Session) -> None:
    """Portfolio repository should persist and reload portfolios."""
    repository = SqlAlchemyPortfolioRepository(db_session)
    owner_id = uuid4()
    portfolio = Portfolio(owner_id=owner_id, name="Growth Portfolio")

    saved = repository.save(portfolio)
    loaded = repository.get_by_id(saved.id)

    assert loaded is not None
    assert loaded.name == "Growth Portfolio"
    assert loaded.owner_id == owner_id
    assert loaded.status == PortfolioStatus.ACTIVE


def test_portfolio_repository_find_by_owner(db_session: Session) -> None:
    """Portfolio repository should find portfolios by owner."""
    repository = SqlAlchemyPortfolioRepository(db_session)
    owner_id = uuid4()
    repository.save(Portfolio(owner_id=owner_id, name="Primary"))
    repository.save(Portfolio(owner_id=owner_id, name="Secondary"))

    portfolios = repository.find_by_owner(owner_id)
    assert len(portfolios) == 2


def test_asset_repository_save_mutual_fund(db_session: Session) -> None:
    """Asset repository should persist mutual fund aggregates."""
    repository = SqlAlchemyAssetRepository(db_session)
    asset = Asset(
        symbol="MIF",
        display_name="Meezan Islamic Fund",
        asset_type=AssetType.MUTUAL_FUND,
    )
    mutual_fund = MutualFund(
        asset_id=asset.id,
        asset=asset,
        management_company="Meezan Asset Management",
        expense_ratio=Decimal("1.95"),
        aum=Decimal("50000000000"),
    )

    saved = repository.save_mutual_fund(mutual_fund)
    loaded = repository.get_mutual_fund(saved.asset_id)

    assert loaded is not None
    assert loaded.asset.symbol == "MIF"
    assert loaded.management_company == "Meezan Asset Management"
    assert repository.get_by_symbol("MIF") is not None


def test_portfolio_repository_transactions_are_immutable(db_session: Session) -> None:
    """Confirmed transactions should not be overwritten on re-save."""
    portfolio_repo = SqlAlchemyPortfolioRepository(db_session)
    asset_repo = SqlAlchemyAssetRepository(db_session)

    asset = asset_repo.save(
        Asset(
            symbol="AMMF",
            display_name="Al Meezan Mutual Fund",
            asset_type=AssetType.MUTUAL_FUND,
        )
    )
    portfolio = portfolio_repo.save(Portfolio(name="Main"))
    holding = portfolio_repo.save_holding(
        Holding(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            asset_type=AssetType.MUTUAL_FUND,
            quantity=Decimal("100"),
            average_cost=Decimal("50"),
            current_price=Decimal("55"),
            current_value=Decimal("5500"),
            cost_basis=Decimal("5000"),
        )
    )

    transaction = Transaction(
        portfolio_id=portfolio.id,
        holding_id=holding.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        units=Decimal("100"),
        price=Decimal("50"),
        gross_amount=Decimal("5000"),
        status=TransactionStatus.CONFIRMED,
        net_amount=Decimal("5000"),
    )
    saved = portfolio_repo.save_transaction(transaction)
    saved.notes = "modified"
    resaved = portfolio_repo.save_transaction(saved)

    assert resaved.notes != "modified"
