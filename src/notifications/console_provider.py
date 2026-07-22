"""Console notification provider."""

from __future__ import annotations

from loguru import logger

from src.domain.enums import NotificationChannel
from src.notifications.base import DeliveryResult, NotificationProvider

_console_logger = logger.bind(channel="notifications.console")


class ConsoleNotificationProvider(NotificationProvider):
    """Write notifications to the console and notifications log."""

    channel = NotificationChannel.CONSOLE

    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    def send(self, title: str, body: str) -> DeliveryResult:
        """Log notification to console sink."""
        _console_logger.info("notification title={} body={}", title, body)
        return DeliveryResult(success=True, message="Delivered to console")
