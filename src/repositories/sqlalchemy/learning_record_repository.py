"""SQLAlchemy learning record repository."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.mappers.learning_record_mapper import LearningRecordMapper
from src.database.models.learning_record import LearningRecordModel, LearningWeightModel
from src.domain.entities.learning_record import LearningRecord
from src.domain.enums import LearningOutcome
from src.repositories.interfaces.learning_record_repository import (
    LearningRecordRepository,
)

DEFAULT_WEIGHT = Decimal("1.0")


class SqlAlchemyLearningRecordRepository(LearningRecordRepository):
    """Persist and query learning records and strategy weights."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, record: LearningRecord) -> LearningRecord:
        record.validate()
        model = self._session.get(LearningRecordModel, record.id)
        if model is None:
            model = LearningRecordMapper.to_model(record)
            self._session.add(model)
        else:
            LearningRecordMapper.update_model(model, record)
        self._session.flush()
        return LearningRecordMapper.to_entity(model)

    def get_by_id(self, record_id: UUID) -> LearningRecord | None:
        model = self._session.get(LearningRecordModel, record_id)
        return LearningRecordMapper.to_entity(model) if model else None

    def get_by_recommendation_id(
        self, recommendation_id: UUID
    ) -> LearningRecord | None:
        stmt = select(LearningRecordModel).where(
            LearningRecordModel.recommendation_id == recommendation_id
        )
        model = self._session.scalar(stmt)
        return LearningRecordMapper.to_entity(model) if model else None

    def list_pending(self, limit: int = 100) -> list[LearningRecord]:
        stmt = (
            select(LearningRecordModel)
            .where(LearningRecordModel.outcome == LearningOutcome.PENDING.value)
            .order_by(LearningRecordModel.created_at.asc())
            .limit(limit)
        )
        return [
            LearningRecordMapper.to_entity(row) for row in self._session.scalars(stmt)
        ]

    def list_all(self, limit: int = 50, offset: int = 0) -> list[LearningRecord]:
        stmt = (
            select(LearningRecordModel)
            .order_by(LearningRecordModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [
            LearningRecordMapper.to_entity(row) for row in self._session.scalars(stmt)
        ]

    def count_all(self) -> int:
        stmt = select(func.count()).select_from(LearningRecordModel)
        return int(self._session.scalar(stmt) or 0)

    def count_by_outcome(self, outcome: LearningOutcome) -> int:
        stmt = (
            select(func.count())
            .select_from(LearningRecordModel)
            .where(LearningRecordModel.outcome == outcome.value)
        )
        return int(self._session.scalar(stmt) or 0)

    def get_weight(self, strategy_key: str) -> Decimal:
        stmt = select(LearningWeightModel).where(
            LearningWeightModel.strategy_key == strategy_key
        )
        model = self._session.scalar(stmt)
        return model.weight_multiplier if model else DEFAULT_WEIGHT

    def save_weight(self, strategy_key: str, weight_multiplier: Decimal) -> Decimal:
        stmt = select(LearningWeightModel).where(
            LearningWeightModel.strategy_key == strategy_key
        )
        model = self._session.scalar(stmt)
        now = datetime.now(UTC)
        if model is None:
            model = LearningWeightModel(
                strategy_key=strategy_key,
                weight_multiplier=weight_multiplier,
                updated_at=now,
            )
            self._session.add(model)
        else:
            model.weight_multiplier = weight_multiplier
            model.updated_at = now
        self._session.flush()
        return model.weight_multiplier
