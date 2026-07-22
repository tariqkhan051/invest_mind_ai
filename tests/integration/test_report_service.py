"""Integration tests for report and notification services."""

from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.domain.enums import NotificationType, ReportType
from src.scheduler.job_context import build_notification_service, build_report_service


def test_generate_daily_report_creates_notification(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Generating a report should persist report and send notification."""
    report_service = build_report_service(test_settings, db_session)
    notification_service = build_notification_service(test_settings, db_session)

    report = report_service.generate(ReportType.DAILY)
    assert report.markdown_content
    assert report.html_content

    history = notification_service.get_history()
    assert history.total_items >= 1
    assert history.items[0].notification_type == NotificationType.REPORT_READY
