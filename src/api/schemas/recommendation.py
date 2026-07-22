"""Recommendation API schemas — docs/18_API.md §9."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.enums import FeedbackAction


class RecommendationResponse(BaseModel):
    """AI recommendation payload."""

    id: UUID
    portfolio_id: UUID
    recommendation_type: str
    priority: int
    asset_id: UUID | None = None
    from_asset_id: UUID | None = None
    to_asset_id: UUID | None = None
    symbol: str | None = None
    from_symbol: str | None = None
    to_symbol: str | None = None
    recommended_amount: Decimal | None = None
    expected_return: Decimal | None = None
    expected_risk: str
    confidence: Decimal
    reason: str
    explanation: str
    supporting_evidence: dict[str, str] = Field(default_factory=dict)
    status: str
    feedback_action: str | None = None
    generated_at: datetime
    expires_at: datetime | None = None


class RecommendationExplanationResponse(BaseModel):
    """Detailed recommendation explanation."""

    recommendation_id: UUID
    summary: str
    detailed_explanation: str
    supporting_evidence: dict[str, str] = Field(default_factory=dict)


class RecommendationFeedbackRequest(BaseModel):
    """User feedback on a recommendation."""

    action: FeedbackAction
    notes: str | None = None


class RecommendationListMeta(BaseModel):
    """Pagination metadata for recommendation history."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class RecommendationHistoryResponse(BaseModel):
    """Paginated recommendation history."""

    items: list[RecommendationResponse]
    meta: RecommendationListMeta
