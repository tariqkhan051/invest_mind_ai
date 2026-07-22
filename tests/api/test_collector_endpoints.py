"""API tests for collector endpoints."""

from fastapi.testclient import TestClient


def test_collector_status_endpoint(client: TestClient) -> None:
    """Collector status endpoint should return configured providers."""
    response = client.get("/api/v1/collectors/status")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    providers = {item["provider"] for item in body["data"]}
    assert "mufap" in providers
    assert "psx" in providers
    assert "sbp" in providers
    assert "news" in providers


def test_news_collector_endpoint(client: TestClient) -> None:
    """POST /collectors/news should invoke the news collector."""
    response = client.post("/api/v1/collectors/news")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "News import completed"
