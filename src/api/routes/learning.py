"""Learning engine API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_learning_service
from src.api.schemas import ApiResponse
from src.api.schemas.learning import (
    LearningHistoryResponse,
    LearningListMeta,
    LearningRecordResponse,
    SelfEvaluationResponse,
)
from src.core.constants import DEFAULT_PAGE_SIZE
from src.domain.entities.learning_record import LearningRecord
from src.engines.learning.models import SelfEvaluationReport
from src.services.learning_service import LearningService

router = APIRouter(prefix="/learning", tags=["Learning Engine"])

LearningServiceDep = Annotated[LearningService, Depends(get_learning_service)]


def _map_record(record: LearningRecord) -> LearningRecordResponse:
    return LearningRecordResponse(
        id=record.id,
        recommendation_id=record.recommendation_id,
        portfolio_snapshot_id=record.portfolio_snapshot_id,
        strategy_id=record.strategy_id,
        outcome=record.outcome.value,
        expected_return=record.expected_return,
        actual_return=record.actual_return,
        prediction_error=record.prediction_error,
        learning_score=record.learning_score,
        confidence_adjustment=record.confidence_adjustment,
        reward=record.reward,
        penalty=record.penalty,
        feedback=record.feedback.value if record.feedback else None,
        evaluated_at=record.evaluated_at,
        created_at=record.created_at,
    )


def _map_evaluation(report: SelfEvaluationReport) -> SelfEvaluationResponse:
    return SelfEvaluationResponse(
        total_records=report.total_records,
        evaluated_records=report.evaluated_records,
        pending_records=report.pending_records,
        accurate_count=report.accurate_count,
        partially_accurate_count=report.partially_accurate_count,
        inaccurate_count=report.inaccurate_count,
        accuracy_rate=report.accuracy_rate,
        average_prediction_error=report.average_prediction_error,
        average_reward=report.average_reward,
        average_learning_score=report.average_learning_score,
        feedback_breakdown=report.feedback_breakdown,
        strategy_weights=report.strategy_weights,
    )


@router.get("/records", response_model=ApiResponse[LearningHistoryResponse])
def get_learning_history(
    service: LearningServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
) -> ApiResponse[LearningHistoryResponse]:
    """Return paginated learning record history."""
    history = service.get_history(page=page, page_size=page_size)
    return ApiResponse(
        message="Learning history retrieved",
        data=LearningHistoryResponse(
            items=[_map_record(item) for item in history.items],
            meta=LearningListMeta(
                page=history.page,
                page_size=history.page_size,
                total_items=history.total_items,
                total_pages=history.total_pages,
            ),
        ),
    )


@router.get(
    "/records/{record_id}",
    response_model=ApiResponse[LearningRecordResponse],
)
def get_learning_record(
    record_id: UUID,
    service: LearningServiceDep,
) -> ApiResponse[LearningRecordResponse]:
    """Return one learning record by id."""
    record = service.get_record(record_id)
    return ApiResponse(
        message="Learning record retrieved",
        data=_map_record(record),
    )


@router.get("/evaluation", response_model=ApiResponse[SelfEvaluationResponse])
def get_self_evaluation(
    service: LearningServiceDep,
) -> ApiResponse[SelfEvaluationResponse]:
    """Return aggregate learning self-evaluation report."""
    report = service.get_self_evaluation()
    return ApiResponse(
        message="Learning self-evaluation retrieved",
        data=_map_evaluation(report),
    )


@router.post("/evaluate", response_model=ApiResponse[list[LearningRecordResponse]])
def evaluate_pending_records(
    service: LearningServiceDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> ApiResponse[list[LearningRecordResponse]]:
    """Evaluate pending learning records against market outcomes."""
    records = service.evaluate_pending(limit=limit)
    return ApiResponse(
        message="Learning records evaluated",
        data=[_map_record(item) for item in records],
    )
