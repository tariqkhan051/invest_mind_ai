"""AI recommendation API routes — docs/18_API.md §9."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_recommendation_service
from src.api.schemas import ApiResponse
from src.api.schemas.recommendation import (
    RecommendationExplanationResponse,
    RecommendationFeedbackRequest,
    RecommendationHistoryResponse,
    RecommendationListMeta,
    RecommendationResponse,
)
from src.core.constants import DEFAULT_PAGE_SIZE
from src.domain.entities.recommendation import Recommendation
from src.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])

RecommendationServiceDep = Annotated[
    RecommendationService,
    Depends(get_recommendation_service),
]


def _map_recommendation(recommendation: Recommendation) -> RecommendationResponse:
    return RecommendationResponse(
        id=recommendation.id,
        portfolio_id=recommendation.portfolio_id,
        recommendation_type=recommendation.recommendation_type.value,
        priority=recommendation.priority,
        asset_id=recommendation.asset_id,
        from_asset_id=recommendation.from_asset_id,
        to_asset_id=recommendation.to_asset_id,
        symbol=recommendation.symbol,
        from_symbol=recommendation.from_symbol,
        to_symbol=recommendation.to_symbol,
        recommended_amount=recommendation.recommended_amount,
        expected_return=recommendation.expected_return,
        expected_risk=recommendation.expected_risk.value,
        confidence=recommendation.confidence,
        reason=recommendation.reason,
        explanation=recommendation.explanation,
        supporting_evidence=recommendation.supporting_evidence,
        status=recommendation.status.value,
        feedback_action=(
            recommendation.feedback_action.value
            if recommendation.feedback_action
            else None
        ),
        generated_at=recommendation.generated_at,
        expires_at=recommendation.expires_at,
    )


@router.get("/latest", response_model=ApiResponse[list[RecommendationResponse]])
def get_latest_recommendations(
    service: RecommendationServiceDep,
    portfolio_id: UUID | None = Query(default=None),
) -> ApiResponse[list[RecommendationResponse]]:
    """Return the latest generated recommendations."""
    recommendations = service.get_latest(portfolio_id=portfolio_id)
    return ApiResponse(
        message="Latest recommendations retrieved",
        data=[_map_recommendation(item) for item in recommendations],
    )


@router.get("", response_model=ApiResponse[RecommendationHistoryResponse])
def get_recommendation_history(
    service: RecommendationServiceDep,
    portfolio_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
) -> ApiResponse[RecommendationHistoryResponse]:
    """Return paginated recommendation history."""
    history = service.get_history(
        portfolio_id=portfolio_id,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        message="Recommendation history retrieved",
        data=RecommendationHistoryResponse(
            items=[_map_recommendation(item) for item in history.items],
            meta=RecommendationListMeta(
                page=history.page,
                page_size=history.page_size,
                total_items=history.total_items,
                total_pages=history.total_pages,
            ),
        ),
    )


@router.post("/run", response_model=ApiResponse[list[RecommendationResponse]])
def run_recommendation_cycle(
    service: RecommendationServiceDep,
    portfolio_id: UUID | None = Query(default=None),
) -> ApiResponse[list[RecommendationResponse]]:
    """Generate a new batch of AI recommendations."""
    recommendations = service.run_recommendation_cycle(portfolio_id=portfolio_id)
    return ApiResponse(
        message="Recommendations generated",
        data=[_map_recommendation(item) for item in recommendations],
    )


@router.get(
    "/explanation/{recommendation_id}",
    response_model=ApiResponse[RecommendationExplanationResponse],
)
def get_recommendation_explanation(
    recommendation_id: UUID,
    service: RecommendationServiceDep,
) -> ApiResponse[RecommendationExplanationResponse]:
    """Return the explanation for a recommendation."""
    explanation = service.get_explanation(recommendation_id)
    return ApiResponse(
        message="Recommendation explanation retrieved",
        data=RecommendationExplanationResponse(
            recommendation_id=explanation.recommendation_id,
            summary=explanation.summary,
            detailed_explanation=explanation.detailed_explanation,
            supporting_evidence=explanation.supporting_evidence,
        ),
    )


@router.get("/{recommendation_id}", response_model=ApiResponse[RecommendationResponse])
def get_recommendation(
    recommendation_id: UUID,
    service: RecommendationServiceDep,
) -> ApiResponse[RecommendationResponse]:
    """Return one recommendation by id."""
    recommendation = service.get_recommendation(recommendation_id)
    return ApiResponse(
        message="Recommendation retrieved",
        data=_map_recommendation(recommendation),
    )


@router.post(
    "/{recommendation_id}/feedback",
    response_model=ApiResponse[RecommendationResponse],
)
def record_recommendation_feedback(
    recommendation_id: UUID,
    request: RecommendationFeedbackRequest,
    service: RecommendationServiceDep,
) -> ApiResponse[RecommendationResponse]:
    """Record user feedback for a recommendation."""
    recommendation = service.record_feedback(
        recommendation_id,
        request.action,
        notes=request.notes,
    )
    return ApiResponse(
        message="Recommendation feedback recorded",
        data=_map_recommendation(recommendation),
    )
