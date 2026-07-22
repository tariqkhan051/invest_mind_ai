"""Learning application service."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from uuid import UUID

from src.core.exceptions import LearningRecordNotFoundError
from src.core.logging import get_logger
from src.domain.entities.learning_record import LearningRecord
from src.domain.entities.recommendation import Recommendation
from src.engines.learning.engine import LearningEngine
from src.engines.learning.models import SelfEvaluationReport
from src.repositories.interfaces.learning_record_repository import (
    LearningRecordRepository,
)
from src.repositories.interfaces.recommendation_repository import (
    RecommendationRepository,
)
from src.services.portfolio_service import PortfolioService

logger = get_logger("services.learning")


@dataclass
class PaginatedLearningRecords:
    """Paginated learning history."""

    items: list[LearningRecord]
    page: int
    page_size: int
    total_items: int
    total_pages: int


class LearningService:
    """Learning use cases for recording and evaluating recommendations."""

    def __init__(
        self,
        learning_repository: LearningRecordRepository,
        recommendation_repository: RecommendationRepository,
        portfolio_service: PortfolioService,
        engine: LearningEngine | None = None,
    ) -> None:
        self._learning_repository = learning_repository
        self._recommendation_repository = recommendation_repository
        self._portfolio_service = portfolio_service
        self._engine = engine

    def record_recommendations(
        self,
        recommendations: list[Recommendation],
        capture_snapshot: bool = True,
    ) -> list[LearningRecord]:
        """Create learning records and optional portfolio snapshots."""
        engine = self._require_engine()
        snapshot = None
        if capture_snapshot and recommendations:
            portfolio_id = recommendations[0].portfolio_id
            snapshot = self._portfolio_service.generate_snapshot(portfolio_id)

        records: list[LearningRecord] = []
        for recommendation in recommendations:
            existing = self._learning_repository.get_by_recommendation_id(
                recommendation.id
            )
            if existing is not None:
                records.append(existing)
                continue
            records.append(engine.create_record(recommendation, snapshot))
        logger.info("learning_records_created count={}", len(records))
        return records

    def sync_feedback(self, recommendation: Recommendation) -> LearningRecord | None:
        """Update learning record when user provides feedback."""
        record = self._learning_repository.get_by_recommendation_id(recommendation.id)
        if record is None or recommendation.feedback_action is None:
            return record
        record.apply_feedback(recommendation.feedback_action)
        return self._learning_repository.save(record)

    def evaluate_pending(self, limit: int = 50) -> list[LearningRecord]:
        """Evaluate all pending learning records against market outcomes."""
        engine = self._require_engine()
        pending = self._learning_repository.list_pending(limit=limit)
        evaluated: list[LearningRecord] = []
        for record in pending:
            recommendation = self._recommendation_repository.get_by_id(
                record.recommendation_id
            )
            if recommendation is None:
                continue
            evaluated.append(engine.evaluate_record(record, recommendation))
        logger.info("learning_records_evaluated count={}", len(evaluated))
        return evaluated

    def get_record(self, record_id: UUID) -> LearningRecord:
        """Return one learning record by id."""
        record = self._learning_repository.get_by_id(record_id)
        if record is None:
            raise LearningRecordNotFoundError(
                f"Learning record {record_id} not found."
            )
        return record

    def get_history(
        self,
        page: int = 1,
        page_size: int = 25,
    ) -> PaginatedLearningRecords:
        """Return paginated learning history."""
        total_items = self._learning_repository.count_all()
        offset = (page - 1) * page_size
        items = self._learning_repository.list_all(
            limit=page_size,
            offset=offset,
        )
        total_pages = ceil(total_items / page_size) if page_size else 0
        return PaginatedLearningRecords(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )

    def get_self_evaluation(self) -> SelfEvaluationReport:
        """Return aggregate learning performance report."""
        return self._require_engine().build_self_evaluation_report()

    def _require_engine(self) -> LearningEngine:
        if self._engine is None:
            raise RuntimeError("LearningEngine is not configured.")
        return self._engine
