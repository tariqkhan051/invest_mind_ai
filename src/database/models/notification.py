"""Notification ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from src.database.base import Base
from src.database.mixins import UUIDPrimaryKeyMixin


class NotificationModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for notification table."""

    __tablename__ = "notification"
    __table_args__ = (
        Index("ix_notification_channel", "channel"),
        Index("ix_notification_status", "status"),
        Index("ix_notification_created_at", "created_at"),
    )

    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    metadata_json: Mapped[dict[str, str] | None] = mapped_column(JSON)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
