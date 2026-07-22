"""Notification entity ↔ ORM mapper."""

from __future__ import annotations

from src.database.models.notification import NotificationModel
from src.domain.entities.notification import Notification
from src.domain.enums import NotificationChannel, NotificationStatus, NotificationType


class NotificationMapper:
    """Map between Notification entity and ORM model."""

    @staticmethod
    def to_entity(model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            channel=NotificationChannel(model.channel),
            notification_type=NotificationType(model.notification_type),
            title=model.title,
            body=model.body,
            status=NotificationStatus(model.status),
            metadata=model.metadata_json or {},
            sent_at=model.sent_at,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Notification) -> NotificationModel:
        return NotificationModel(
            id=entity.id,
            channel=entity.channel.value,
            notification_type=entity.notification_type.value,
            title=entity.title,
            body=entity.body,
            status=entity.status.value,
            metadata_json=entity.metadata or None,
            sent_at=entity.sent_at,
            created_at=entity.created_at,
        )

    @staticmethod
    def update_model(model: NotificationModel, entity: Notification) -> None:
        updated = NotificationMapper.to_model(entity)
        for column in NotificationModel.__table__.columns:
            if column.name == "id":
                continue
            setattr(model, column.name, getattr(updated, column.name))
