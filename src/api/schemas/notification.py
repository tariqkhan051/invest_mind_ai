"""Notification API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.enums import NotificationType


class NotificationResponse(BaseModel):
    """Notification API representation."""

    id: UUID
    channel: str
    notification_type: str
    title: str
    body: str
    status: str
    metadata: dict[str, str] = Field(default_factory=dict)
    sent_at: datetime | None
    created_at: datetime


class NotificationHistoryMeta(BaseModel):
    """Pagination metadata for notifications."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class NotificationHistoryResponse(BaseModel):
    """Paginated notification history."""

    items: list[NotificationResponse]
    meta: NotificationHistoryMeta


class SendNotificationRequest(BaseModel):
    """Request body for sending a notification."""

    title: str
    body: str
    notification_type: NotificationType = NotificationType.SYSTEM
