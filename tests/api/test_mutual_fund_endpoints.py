"""API tests for mutual fund endpoints."""

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.collectors.base.models import NavRecord
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.enums import AssetType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)


def _seed_fund(db_session: Session, symbol: str = "MIF") -> Asset:
    asset_repo = SqlAlchemyAssetRepository(db_session)
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    asset = Asset(
        symbol=symbol,
        display_name="Meezan Islamic Fund",
        asset_type=AssetType.MUTUAL_FUND,
    )
    mutual_fund = MutualFund(
        asset_id=asset.id,
        asset=asset,
        management_company="Meezan",
        expense_ratio=Decimal("1.8"),
        aum=Decimal("10000000000"),
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
            nav=Decimal("115"),
            source="test",
        ),
        saved.asset_id,
    )
    return saved.asset


def test_list_funds_endpoint(client: TestClient, db_session: Session) -> None:
    """GET /funds should return analyzed funds."""
    _seed_fund(db_session)
    db_session.commit()

    response = client.get("/api/v1/funds")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["symbol"] == "MIF"


def test_get_fund_details_and_history(
    client: TestClient,
    db_session: Session,
) -> None:
    """Fund detail and history endpoints should return data."""
    asset = _seed_fund(db_session)
    db_session.commit()

    detail = client.get(f"/api/v1/funds/{asset.id}")
    assert detail.status_code == 200
    assert detail.json()["data"]["ai_score"] is not None

    history = client.get(f"/api/v1/funds/{asset.id}/history")
    assert history.status_code == 200
    assert len(history.json()["data"]) == 2


def test_rankings_and_compare_endpoints(
    client: TestClient,
    db_session: Session,
) -> None:
    """Rankings and compare endpoints should work."""
    first = _seed_fund(db_session, "F1")
    second = _seed_fund(db_session, "F2")
    db_session.commit()

    rankings = client.get("/api/v1/funds/rankings")
    assert rankings.status_code == 200
    assert len(rankings.json()["data"]) == 2

    compare = client.post(
        "/api/v1/funds/compare",
        json={"fund_ids": [str(first.id), str(second.id)]},
    )
    assert compare.status_code == 200
    assert len(compare.json()["data"]["funds"]) == 2


def test_categories_and_switch_opportunities(
    client: TestClient,
    db_session: Session,
) -> None:
    """Category and switch endpoints should return valid payloads."""
    _seed_fund(db_session)
    db_session.commit()

    categories = client.get("/api/v1/funds/categories")
    assert categories.status_code == 200
    assert len(categories.json()["data"]) >= 1

    switches = client.get("/api/v1/funds/switch-opportunities")
    assert switches.status_code == 200
    assert isinstance(switches.json()["data"], list)
