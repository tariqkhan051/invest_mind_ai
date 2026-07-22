"""Notification repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.notification import Notification


class NotificationRepository(ABC):
    """Persistence contract for notifications."""

    @abstractmethod
    def save(self, notification: Notification) -> Notification:
        """Persist a notification."""

    @abstractmethod
    def get_by_id(self, notification_id: UUID) -> Notification | None:
        """Load a notification by id."""

    @abstractmethod
    def list_recent(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """Return recent notifications."""

    @abstractmethod
    def count(self) -> int:
        """Return total notification count."""
