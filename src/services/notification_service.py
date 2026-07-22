"""Notification application service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import ceil
from uuid import UUID

from src.config.settings import Settings
from src.core.exceptions import NotificationNotFoundError
from src.core.logging import get_logger
from src.domain.entities.notification import Notification
from src.domain.enums import NotificationChannel, NotificationType
from src.notifications.registry import build_notification_providers
from src.repositories.interfaces.notification_repository import NotificationRepository

logger = get_logger("services.notification")


@dataclass
class PaginatedNotifications:
    """Paginated notification history."""

    items: list[Notification]
    page: int
    page_size: int
    total_items: int
    total_pages: int


class NotificationService:
    """Send and track user notifications across replaceable providers."""

    def __init__(
        self,
        notification_repository: NotificationRepository,
        settings: Settings,
    ) -> None:
        self._notification_repository = notification_repository
        self._settings = settings
        self._providers = build_notification_providers(settings)

    def is_enabled(self) -> bool:
        """Return True when notifications feature flag is on."""
        return bool(
            self._settings.features_config.get("features", {}).get(
                "notifications",
                False,
            )
        )

    def send(
        self,
        title: str,
        body: str,
        notification_type: NotificationType,
        *,
        channel: NotificationChannel | None = None,
        metadata: dict[str, str] | None = None,
    ) -> list[Notification]:
        """Send a notification through enabled providers."""
        if not self.is_enabled():
            logger.info("notifications_disabled skipping title={}", title)
            return []

        providers = self._providers
        if channel is not None:
            providers = [item for item in providers if item.channel == channel]

        saved: list[Notification] = []
        for provider in providers:
            notification = Notification(
                channel=provider.channel,
                notification_type=notification_type,
                title=title,
                body=body,
                metadata=metadata or {},
            )
            result = provider.send(title, body)
            if result.success:
                notification.mark_sent(datetime.now(UTC))
            else:
                notification.mark_failed()
            saved.append(self._notification_repository.save(notification))
        return saved

    def get_notification(self, notification_id: UUID) -> Notification:
        """Return one notification by id."""
        notification = self._notification_repository.get_by_id(notification_id)
        if notification is None:
            raise NotificationNotFoundError(
                f"Notification {notification_id} not found."
            )
        return notification

    def get_history(
        self,
        page: int = 1,
        page_size: int = 25,
    ) -> PaginatedNotifications:
        """Return paginated notification history."""
        total_items = self._notification_repository.count()
        offset = (page - 1) * page_size
        items = self._notification_repository.list_recent(
            limit=page_size,
            offset=offset,
        )
        total_pages = ceil(total_items / page_size) if page_size else 0
        return PaginatedNotifications(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )
