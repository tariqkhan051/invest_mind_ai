"""Email notification provider (basic stub)."""

from __future__ import annotations

from loguru import logger

from src.domain.enums import NotificationChannel
from src.notifications.base import DeliveryResult, NotificationProvider

_email_logger = logger.bind(channel="notifications.email")


class EmailNotificationProvider(NotificationProvider):
    """Email provider stub that logs until SMTP is configured."""

    channel = NotificationChannel.EMAIL

    def __init__(
        self,
        enabled: bool = False,
        smtp_host: str | None = None,
        recipient: str | None = None,
    ) -> None:
        self._enabled = enabled and bool(smtp_host and recipient)
        self._smtp_host = smtp_host
        self._recipient = recipient

    def is_enabled(self) -> bool:
        return self._enabled

    def send(self, title: str, body: str) -> DeliveryResult:
        """Log email notification; real SMTP delivery is future work."""
        if not self.is_enabled():
            return DeliveryResult(
                success=False,
                message="Email provider is not configured",
            )
        _email_logger.info(
            "email_notification host={} recipient={} title={} body={}",
            self._smtp_host,
            self._recipient,
            title,
            body,
        )
        return DeliveryResult(success=True, message="Email logged for delivery")
