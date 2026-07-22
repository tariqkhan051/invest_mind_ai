"""API tests for dashboard endpoint."""

from fastapi.testclient import TestClient


def test_dashboard_endpoint(client: TestClient) -> None:
    """GET /dashboard should return aggregated dashboard data."""
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert "portfolio_summary" in data
    assert "market_summary" in data
    assert "latest_recommendations" in data
    assert "charts" in data
    assert "recent_activity" in data
    assert data["portfolio_summary"]["portfolio"]["name"]
