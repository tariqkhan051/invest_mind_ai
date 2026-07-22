"""Learning API schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class LearningRecordResponse(BaseModel):
    """Learning record API representation."""

    id: UUID
    recommendation_id: UUID
    portfolio_snapshot_id: UUID | None
    strategy_id: str | None
    outcome: str
    expected_return: Decimal | None
    actual_return: Decimal | None
    prediction_error: Decimal | None
    learning_score: Decimal | None
    confidence_adjustment: Decimal | None
    reward: Decimal | None
    penalty: Decimal | None
    feedback: str | None
    evaluated_at: datetime | None
    created_at: datetime


class LearningListMeta(BaseModel):
    """Pagination metadata for learning history."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class LearningHistoryResponse(BaseModel):
    """Paginated learning history response."""

    items: list[LearningRecordResponse]
    meta: LearningListMeta


class SelfEvaluationResponse(BaseModel):
    """Self-evaluation report response."""

    total_records: int
    evaluated_records: int
    pending_records: int
    accurate_count: int
    partially_accurate_count: int
    inaccurate_count: int
    accuracy_rate: Decimal
    average_prediction_error: Decimal | None
    average_reward: Decimal | None
    average_learning_score: Decimal | None
    feedback_breakdown: dict[str, int] = Field(default_factory=dict)
    strategy_weights: dict[str, Decimal] = Field(default_factory=dict)
