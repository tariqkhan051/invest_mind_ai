"""API tests for asset registration endpoints."""

from fastapi.testclient import TestClient


def test_create_and_list_assets(client: TestClient) -> None:
    """POST funds/stocks should register assets visible via GET /assets."""
    fund = client.post(
        "/api/v1/assets/funds",
        json={
            "symbol": "MIF",
            "display_name": "Meezan Islamic Fund",
            "management_company": "Al Meezan",
            "expense_ratio": "1.8",
            "aum": "10000000000",
        },
    )
    assert fund.status_code == 200
    assert fund.json()["data"]["symbol"] == "MIF"

    stock = client.post(
        "/api/v1/assets/stocks",
        json={
            "symbol": "ENGRO",
            "display_name": "Engro Corporation",
            "company_name": "Engro Corporation Limited",
            "market_cap": "250000000000",
            "pe": "8.5",
        },
    )
    assert stock.status_code == 200
    assert stock.json()["data"]["symbol"] == "ENGRO"

    listed = client.get("/api/v1/assets")
    assert listed.status_code == 200
    symbols = {item["symbol"] for item in listed.json()["data"]}
    assert symbols == {"MIF", "ENGRO"}


def test_duplicate_symbol_rejected(client: TestClient) -> None:
    """Duplicate symbols should return a validation error."""
    payload = {
        "symbol": "AMMF",
        "display_name": "Al Meezan Mutual Fund",
    }
    first = client.post("/api/v1/assets/funds", json=payload)
    assert first.status_code == 200
    second = client.post("/api/v1/assets/funds", json=payload)
    assert second.status_code == 400
