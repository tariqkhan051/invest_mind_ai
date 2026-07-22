"""Integration tests for mutual fund service."""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from src.collectors.base.models import NavRecord
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.enums import AssetType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)
from src.services.mutual_fund_service import MutualFundService


def _seed_fund(
    db_session: Session,
    symbol: str,
    asset_type: AssetType = AssetType.EQUITY_FUND,
    yearly_growth: Decimal = Decimal("1.15"),
) -> Asset:
    asset_repo = SqlAlchemyAssetRepository(db_session)
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    asset = Asset(symbol=symbol, display_name=f"{symbol} Fund", asset_type=asset_type)
    mutual_fund = MutualFund(
        asset_id=asset.id,
        asset=asset,
        management_company="Test AMC",
        expense_ratio=Decimal("1.5"),
        aum=Decimal("5000000000"),
    )
    saved = asset_repo.save_mutual_fund(mutual_fund)
    market_repo.save_nav(
        NavRecord(
            symbol=symbol,
            nav_date=date(2025, 1, 1),
            nav=Decimal("100"),
            source="test",
        ),
        saved.asset_id,
    )
    market_repo.save_nav(
        NavRecord(
            symbol=symbol,
            nav_date=date(2026, 1, 1),
            nav=Decimal("100") * yearly_growth,
            source="test",
        ),
        saved.asset_id,
    )
    return saved.asset


def test_list_mutual_funds_returns_analyses(db_session: Session) -> None:
    """Service should list and analyze persisted mutual funds."""
    _seed_fund(db_session, "FUND1")
    _seed_fund(db_session, "FUND2")
    service = MutualFundService(
        asset_repository=SqlAlchemyAssetRepository(db_session),
        market_data_repository=SqlAlchemyMarketDataRepository(db_session),
    )

    funds = service.list_funds()
    assert len(funds) == 2
    assert all(fund.ai_score is not None for fund in funds)


def test_get_nav_history_returns_ordered_points(db_session: Session) -> None:
    """Market data repository should return ascending NAV history."""
    saved = _seed_fund(db_session, "HIST")
    market_repo = SqlAlchemyMarketDataRepository(db_session)

    history = market_repo.get_nav_history(saved.id)
    assert len(history) == 2
    assert history[0].nav_date < history[1].nav_date


def test_compare_and_rank_funds(db_session: Session) -> None:
    """Service should rank and compare funds."""
    first = _seed_fund(db_session, "TOP", yearly_growth=Decimal("1.25"))
    second = _seed_fund(db_session, "BOTTOM", yearly_growth=Decimal("1.05"))
    service = MutualFundService(
        asset_repository=SqlAlchemyAssetRepository(db_session),
        market_data_repository=SqlAlchemyMarketDataRepository(db_session),
    )

    rankings = service.get_rankings()
    assert rankings[0].symbol == "TOP"

    comparison = service.compare_funds([first.id, second.id])
    assert len(comparison.funds) == 2

    opportunities = service.get_switch_opportunities()
    assert any(item.from_symbol == "BOTTOM" for item in opportunities)
