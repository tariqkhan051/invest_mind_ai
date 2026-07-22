"""Notification entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.enums import NotificationChannel, NotificationStatus, NotificationType


@dataclass
class Notification:
    """User-facing notification record."""

    channel: NotificationChannel
    notification_type: NotificationType
    title: str
    body: str
    id: UUID = field(default_factory=uuid4)
    status: NotificationStatus = NotificationStatus.PENDING
    metadata: dict[str, str] = field(default_factory=dict)
    sent_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_sent(self, sent_at: datetime) -> None:
        """Mark notification as successfully delivered."""
        self.status = NotificationStatus.SENT
        self.sent_at = sent_at

    def mark_failed(self) -> None:
        """Mark notification delivery as failed."""
        self.status = NotificationStatus.FAILED
