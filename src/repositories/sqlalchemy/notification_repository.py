"""SQLAlchemy notification repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.mappers.notification_mapper import NotificationMapper
from src.database.models.notification import NotificationModel
from src.domain.entities.notification import Notification
from src.repositories.interfaces.notification_repository import NotificationRepository


class SqlAlchemyNotificationRepository(NotificationRepository):
    """Persist and query notifications."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, notification: Notification) -> Notification:
        model = self._session.get(NotificationModel, notification.id)
        if model is None:
            model = NotificationMapper.to_model(notification)
            self._session.add(model)
        else:
            NotificationMapper.update_model(model, notification)
        self._session.flush()
        return NotificationMapper.to_entity(model)

    def get_by_id(self, notification_id: UUID) -> Notification | None:
        model = self._session.get(NotificationModel, notification_id)
        return NotificationMapper.to_entity(model) if model else None

    def list_recent(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        stmt = (
            select(NotificationModel)
            .order_by(NotificationModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [
            NotificationMapper.to_entity(row) for row in self._session.scalars(stmt)
        ]

    def count(self) -> int:
        stmt = select(func.count()).select_from(NotificationModel)
        return int(self._session.scalar(stmt) or 0)
