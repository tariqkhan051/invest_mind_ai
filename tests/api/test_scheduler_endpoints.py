"""API tests for scheduler endpoints."""

from fastapi.testclient import TestClient


def test_scheduler_jobs_endpoint(client: TestClient) -> None:
    """GET /scheduler/jobs should list configured jobs."""
    response = client.get("/api/v1/scheduler/jobs")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    job_ids = {item["job_id"] for item in body["data"]}
    assert "portfolio_snapshot" in job_ids
    assert "recommendation_cycle" in job_ids


def test_scheduler_run_and_history(client: TestClient) -> None:
    """Manual job run should appear in scheduler history."""
    run = client.post("/api/v1/scheduler/jobs/run/portfolio_snapshot")
    assert run.status_code == 200
    assert run.json()["data"]["status"] == "success"

    history = client.get("/api/v1/scheduler/history")
    assert history.status_code == 200
    assert history.json()["data"]["meta"]["total_items"] >= 1
