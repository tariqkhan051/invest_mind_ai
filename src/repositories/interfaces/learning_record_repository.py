"""Learning record repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from src.domain.entities.learning_record import LearningRecord
from src.domain.enums import LearningOutcome


class LearningRecordRepository(ABC):
    """Persistence contract for learning records and weights."""

    @abstractmethod
    def save(self, record: LearningRecord) -> LearningRecord:
        """Persist a learning record."""

    @abstractmethod
    def get_by_id(self, record_id: UUID) -> LearningRecord | None:
        """Load a learning record by id."""

    @abstractmethod
    def get_by_recommendation_id(
        self, recommendation_id: UUID
    ) -> LearningRecord | None:
        """Load the learning record for a recommendation."""

    @abstractmethod
    def list_pending(self, limit: int = 100) -> list[LearningRecord]:
        """Return learning records awaiting outcome evaluation."""

    @abstractmethod
    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LearningRecord]:
        """Return paginated learning history."""

    @abstractmethod
    def count_all(self) -> int:
        """Return total learning record count."""

    @abstractmethod
    def count_by_outcome(self, outcome: LearningOutcome) -> int:
        """Return count of records with a given outcome."""

    @abstractmethod
    def get_weight(self, strategy_key: str) -> Decimal:
        """Return weight multiplier for a strategy, defaulting to 1.0."""

    @abstractmethod
    def save_weight(self, strategy_key: str, weight_multiplier: Decimal) -> Decimal:
        """Persist updated strategy weight multiplier."""
