"""API tests for report and notification endpoints."""

from fastapi.testclient import TestClient


def test_generate_and_list_reports(client: TestClient) -> None:
    """POST /reports/generate and GET /reports should work."""
    generate = client.post(
        "/api/v1/reports/generate",
        json={"report_type": "daily"},
    )
    assert generate.status_code == 200
    body = generate.json()
    assert body["success"] is True
    assert "Portfolio Summary" in body["data"]["markdown_content"]

    listing = client.get("/api/v1/reports")
    assert listing.status_code == 200
    assert listing.json()["data"]["meta"]["total_items"] >= 1

    daily = client.get("/api/v1/reports/daily")
    assert daily.status_code == 200


def test_notification_send_and_history(client: TestClient) -> None:
    """Notification send endpoint should persist delivery records."""
    send = client.post(
        "/api/v1/notifications/send",
        json={
            "title": "Test alert",
            "body": "Portfolio review reminder",
            "notification_type": "system",
        },
    )
    assert send.status_code == 200
    assert len(send.json()["data"]) >= 1

    history = client.get("/api/v1/notifications")
    assert history.status_code == 200
    assert history.json()["data"]["meta"]["total_items"] >= 1
