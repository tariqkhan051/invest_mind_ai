"""Report repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.report import Report
from src.domain.enums import ReportType


class ReportRepository(ABC):
    """Persistence contract for generated reports."""

    @abstractmethod
    def save(self, report: Report) -> Report:
        """Persist a report."""

    @abstractmethod
    def get_by_id(self, report_id: UUID) -> Report | None:
        """Load a report by id."""

    @abstractmethod
    def get_latest(self, report_type: ReportType) -> Report | None:
        """Return the most recent report of a given type."""

    @abstractmethod
    def list_reports(
        self,
        limit: int = 25,
        offset: int = 0,
        report_type: ReportType | None = None,
    ) -> list[Report]:
        """Return paginated report history."""

    @abstractmethod
    def count(self, report_type: ReportType | None = None) -> int:
        """Return total report count."""
