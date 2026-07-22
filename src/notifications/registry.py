"""Notification provider registry."""

from __future__ import annotations

from src.config.settings import Settings
from src.notifications.base import NotificationProvider
from src.notifications.console_provider import ConsoleNotificationProvider
from src.notifications.email_provider import EmailNotificationProvider


def build_notification_providers(settings: Settings) -> list[NotificationProvider]:
    """Construct enabled notification providers from configuration."""
    config = settings.notifications_config.get("notifications", {})
    providers: list[NotificationProvider] = []

    console_config = config.get("console", {})
    if console_config.get("enabled", True):
        providers.append(
            ConsoleNotificationProvider(enabled=True),
        )

    email_config = config.get("email", {})
    if email_config.get("enabled", False):
        providers.append(
            EmailNotificationProvider(
                enabled=True,
                smtp_host=email_config.get("smtp_host"),
                recipient=email_config.get("recipient"),
            ),
        )

    return [provider for provider in providers if provider.is_enabled()]
