"""API tests for stock endpoints."""

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.collectors.base.models import PriceRecord
from src.domain.entities.asset import Asset
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)


def _seed_stock(db_session: Session, symbol: str = "HBL") -> Stock:
    asset_repo = SqlAlchemyAssetRepository(db_session)
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    asset = Asset(
        symbol=symbol,
        display_name="Habib Bank Limited",
        asset_type=AssetType.STOCK,
        exchange="PSX",
    )
    stock = Stock(
        asset_id=asset.id,
        asset=asset,
        company_name="Habib Bank Limited",
        industry="Banking",
        pe=Decimal("8.5"),
        roe=Decimal("20"),
    )
    saved = asset_repo.save_stock(stock)
    market_repo.save_price(
        PriceRecord(
            symbol=symbol,
            price_date=date(2025, 1, 1),
            close_price=Decimal("100"),
            source="test",
        ),
        saved.asset_id,
    )
    market_repo.save_price(
        PriceRecord(
            symbol=symbol,
            price_date=date(2026, 1, 1),
            close_price=Decimal("120"),
            source="test",
        ),
        saved.asset_id,
    )
    return saved


def test_list_stocks_endpoint(client: TestClient, db_session: Session) -> None:
    """GET /stocks should return analyzed stocks."""
    _seed_stock(db_session)
    db_session.commit()

    response = client.get("/api/v1/stocks")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["symbol"] == "HBL"


def test_get_stock_details_and_history(
    client: TestClient,
    db_session: Session,
) -> None:
    """Stock detail and history endpoints should return data."""
    _seed_stock(db_session)
    db_session.commit()

    detail = client.get("/api/v1/stocks/HBL")
    assert detail.status_code == 200
    assert detail.json()["data"]["ai_score"] is not None

    history = client.get("/api/v1/stocks/HBL/history")
    assert history.status_code == 200
    assert len(history.json()["data"]) == 2


def test_rankings_and_compare_endpoints(
    client: TestClient,
    db_session: Session,
) -> None:
    """Rankings and compare endpoints should work."""
    _seed_stock(db_session, "HBL")
    _seed_stock(db_session, "UBL")
    db_session.commit()

    rankings = client.get("/api/v1/stocks/rankings")
    assert rankings.status_code == 200
    assert len(rankings.json()["data"]) == 2

    compare = client.post(
        "/api/v1/stocks/compare",
        json={"symbols": ["HBL", "UBL"]},
    )
    assert compare.status_code == 200
    assert len(compare.json()["data"]["stocks"]) == 2


def test_opportunities_endpoint(client: TestClient, db_session: Session) -> None:
    """Opportunities endpoint should return a valid payload."""
    _seed_stock(db_session)
    db_session.commit()

    response = client.get("/api/v1/stocks/opportunities")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
