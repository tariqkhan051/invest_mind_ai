"""SQLAlchemy report repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.mappers.report_mapper import ReportMapper
from src.database.models.report import ReportModel
from src.domain.entities.report import Report
from src.domain.enums import ReportType
from src.repositories.interfaces.report_repository import ReportRepository


class SqlAlchemyReportRepository(ReportRepository):
    """Persist and query investment reports."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, report: Report) -> Report:
        model = ReportMapper.to_model(report)
        self._session.add(model)
        self._session.flush()
        return ReportMapper.to_entity(model)

    def get_by_id(self, report_id: UUID) -> Report | None:
        model = self._session.get(ReportModel, report_id)
        return ReportMapper.to_entity(model) if model else None

    def get_latest(self, report_type: ReportType) -> Report | None:
        stmt = (
            select(ReportModel)
            .where(ReportModel.report_type == report_type.value)
            .order_by(ReportModel.generated_at.desc())
            .limit(1)
        )
        model = self._session.scalar(stmt)
        return ReportMapper.to_entity(model) if model else None

    def list_reports(
        self,
        limit: int = 25,
        offset: int = 0,
        report_type: ReportType | None = None,
    ) -> list[Report]:
        stmt = select(ReportModel).order_by(ReportModel.generated_at.desc())
        if report_type is not None:
            stmt = stmt.where(ReportModel.report_type == report_type.value)
        stmt = stmt.offset(offset).limit(limit)
        return [ReportMapper.to_entity(row) for row in self._session.scalars(stmt)]

    def count(self, report_type: ReportType | None = None) -> int:
        stmt = select(func.count()).select_from(ReportModel)
        if report_type is not None:
            stmt = stmt.where(ReportModel.report_type == report_type.value)
        return int(self._session.scalar(stmt) or 0)
