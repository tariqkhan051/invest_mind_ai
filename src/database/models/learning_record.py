"""Learning record ORM model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from src.database.base import Base
from src.database.mixins import UUIDPrimaryKeyMixin


class LearningRecordModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for learning_record table."""

    __tablename__ = "learning_record"
    __table_args__ = (
        Index("ix_learning_record_recommendation_id", "recommendation_id"),
        Index("ix_learning_record_strategy_id", "strategy_id"),
        Index("ix_learning_record_outcome", "outcome"),
        Index("ix_learning_record_evaluated_at", "evaluated_at"),
    )

    recommendation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recommendation.id"),
        nullable=False,
    )
    portfolio_snapshot_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("portfolio_snapshot.id"),
    )
    strategy_id: Mapped[str | None] = mapped_column(String(50))
    outcome: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )
    expected_return: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    actual_return: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    prediction_error: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    learning_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    confidence_adjustment: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    reward: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    penalty: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    feedback: Mapped[str | None] = mapped_column(String(50))
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class LearningWeightModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for per-strategy weight multipliers."""

    __tablename__ = "learning_weight"
    __table_args__ = (
        Index("ix_learning_weight_strategy_key", "strategy_key", unique=True),
    )

    strategy_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    weight_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), nullable=False, default=Decimal("1.0")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
