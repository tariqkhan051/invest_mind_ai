"""Scheduler job run ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from src.database.base import Base
from src.database.mixins import UUIDPrimaryKeyMixin


class SchedulerJobRunModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for scheduler_job_run table."""

    __tablename__ = "scheduler_job_run"
    __table_args__ = (
        Index("ix_scheduler_job_run_job_id", "job_id"),
        Index("ix_scheduler_job_run_started_at", "started_at"),
        Index("ix_scheduler_job_run_status", "status"),
    )

    job_id: Mapped[str] = mapped_column(String(50), nullable=False)
    job_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    trigger: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_ms: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    details: Mapped[dict[str, object] | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
