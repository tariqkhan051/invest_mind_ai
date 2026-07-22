"""API tests for system endpoints."""

from fastapi.testclient import TestClient

from src.core.constants import API_VERSION


def test_root_endpoint(client: TestClient) -> None:
    """Root endpoint should return API navigation info."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "InvestMind AI" in body["message"]
    assert body["health"] == "/api/v1/health"


def test_health_endpoint(client: TestClient) -> None:
    """Health endpoint should return healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert body["data"]["environment"] == "testing"


def test_ready_endpoint(client: TestClient) -> None:
    """Readiness endpoint should confirm database connectivity."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ready"
    assert body["data"]["database"] == "ready"


def test_version_endpoint(client: TestClient) -> None:
    """Version endpoint should return application metadata."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["api_version"] == API_VERSION
    assert body["data"]["environment"] == "testing"
