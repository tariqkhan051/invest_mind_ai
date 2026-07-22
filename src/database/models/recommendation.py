"""Recommendation ORM model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from src.database.base import Base
from src.database.mixins import UUIDPrimaryKeyMixin


class RecommendationModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for recommendation table."""

    __tablename__ = "recommendation"
    __table_args__ = (
        Index("ix_recommendation_portfolio_id", "portfolio_id"),
        Index("ix_recommendation_status", "status"),
        Index("ix_recommendation_generated_at", "generated_at"),
        Index("ix_recommendation_priority", "priority"),
    )

    portfolio_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("portfolio.id"), nullable=False
    )
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    asset_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id")
    )
    from_asset_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id")
    )
    to_asset_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id")
    )
    symbol: Mapped[str | None] = mapped_column(String(50))
    from_symbol: Mapped[str | None] = mapped_column(String(50))
    to_symbol: Mapped[str | None] = mapped_column(String(50))
    recommended_amount: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    expected_return: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    expected_risk: Mapped[str] = mapped_column(
        String(20), nullable=False, default="moderate"
    )
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_evidence: Mapped[dict[str, str] | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    feedback_action: Mapped[str | None] = mapped_column(String(50))
    feedback_notes: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
