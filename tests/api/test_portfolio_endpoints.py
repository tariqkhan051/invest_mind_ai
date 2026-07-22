"""API tests for portfolio endpoints."""

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.domain.entities.asset import Asset
from src.domain.enums import AssetType, TransactionType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository


def _seed_asset(db_session: Session) -> Asset:
    repository = SqlAlchemyAssetRepository(db_session)
    return repository.save(
        Asset(
            symbol="AMMF",
            display_name="Al Meezan Mutual Fund",
            asset_type=AssetType.MUTUAL_FUND,
        )
    )


def test_get_portfolio_summary_empty(client: TestClient) -> None:
    """Empty portfolio should return a valid summary."""
    response = client.get("/api/v1/portfolio")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["portfolio_value"] == "0"


def test_record_transaction_and_get_holdings(
    client: TestClient,
    db_session: Session,
) -> None:
    """POST transaction should update holdings visible via GET."""
    asset = _seed_asset(db_session)
    db_session.commit()

    deposit = client.post(
        "/api/v1/portfolio/transactions",
        json={
            "asset_id": str(asset.id),
            "transaction_type": TransactionType.ADJUSTMENT.value,
            "units": "0",
            "price": "0",
            "gross_amount": "10000",
        },
    )
    assert deposit.status_code == 200

    buy = client.post(
        "/api/v1/portfolio/transactions",
        json={
            "asset_id": str(asset.id),
            "transaction_type": TransactionType.BUY.value,
            "units": "100",
            "price": "50",
        },
    )
    assert buy.status_code == 200

    holdings = client.get("/api/v1/portfolio/holdings")
    assert holdings.status_code == 200
    data = holdings.json()["data"]
    assert len(data) == 1
    assert Decimal(data[0]["quantity"]) == Decimal("100")


def test_get_performance_endpoint(client: TestClient, db_session: Session) -> None:
    """Performance endpoint should return metrics."""
    asset = _seed_asset(db_session)
    db_session.commit()

    client.post(
        "/api/v1/portfolio/transactions",
        json={
            "asset_id": str(asset.id),
            "transaction_type": TransactionType.ADJUSTMENT.value,
            "units": "0",
            "price": "0",
            "gross_amount": "5000",
        },
    )
    client.post(
        "/api/v1/portfolio/transactions",
        json={
            "asset_id": str(asset.id),
            "transaction_type": TransactionType.BUY.value,
            "units": "100",
            "price": "50",
        },
    )

    response = client.get("/api/v1/portfolio/performance")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "percentage_return" in body["data"]
