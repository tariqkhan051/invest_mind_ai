"""Notification API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_notification_service
from src.api.schemas import ApiResponse
from src.api.schemas.notification import (
    NotificationHistoryMeta,
    NotificationHistoryResponse,
    NotificationResponse,
    SendNotificationRequest,
)
from src.core.constants import DEFAULT_PAGE_SIZE
from src.domain.entities.notification import Notification
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

NotificationServiceDep = Annotated[
    NotificationService,
    Depends(get_notification_service),
]


def _map_notification(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        channel=notification.channel.value,
        notification_type=notification.notification_type.value,
        title=notification.title,
        body=notification.body,
        status=notification.status.value,
        metadata=notification.metadata,
        sent_at=notification.sent_at,
        created_at=notification.created_at,
    )


@router.get("", response_model=ApiResponse[NotificationHistoryResponse])
def list_notifications(
    service: NotificationServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
) -> ApiResponse[NotificationHistoryResponse]:
    """Return paginated notification history."""
    history = service.get_history(page=page, page_size=page_size)
    return ApiResponse(
        message="Notifications retrieved",
        data=NotificationHistoryResponse(
            items=[_map_notification(item) for item in history.items],
            meta=NotificationHistoryMeta(
                page=history.page,
                page_size=history.page_size,
                total_items=history.total_items,
                total_pages=history.total_pages,
            ),
        ),
    )


@router.get("/{notification_id}", response_model=ApiResponse[NotificationResponse])
def get_notification(
    notification_id: UUID,
    service: NotificationServiceDep,
) -> ApiResponse[NotificationResponse]:
    """Return one notification by id."""
    notification = service.get_notification(notification_id)
    return ApiResponse(
        message="Notification retrieved",
        data=_map_notification(notification),
    )


@router.post("/send", response_model=ApiResponse[list[NotificationResponse]])
def send_notification(
    request: SendNotificationRequest,
    service: NotificationServiceDep,
) -> ApiResponse[list[NotificationResponse]]:
    """Send a notification through enabled providers."""
    notifications = service.send(
        title=request.title,
        body=request.body,
        notification_type=request.notification_type,
    )
    return ApiResponse(
        message="Notification sent",
        data=[_map_notification(item) for item in notifications],
    )
