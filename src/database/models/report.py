"""Report ORM model."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from src.database.base import Base
from src.database.mixins import UUIDPrimaryKeyMixin


class ReportModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for report table."""

    __tablename__ = "report"
    __table_args__ = (
        Index("ix_report_report_type", "report_type"),
        Index("ix_report_generated_at", "generated_at"),
        Index("ix_report_portfolio_id", "portfolio_id"),
    )

    portfolio_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("portfolio.id")
    )
    report_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    html_content: Mapped[str] = mapped_column(Text, nullable=False)
    period_start: Mapped[date | None] = mapped_column(Date)
    period_end: Mapped[date | None] = mapped_column(Date)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
