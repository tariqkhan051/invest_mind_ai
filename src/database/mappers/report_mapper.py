"""Report entity ↔ ORM mapper."""

from __future__ import annotations

from src.database.models.report import ReportModel
from src.domain.entities.report import Report
from src.domain.enums import ReportType


class ReportMapper:
    """Map between Report entity and ORM model."""

    @staticmethod
    def to_entity(model: ReportModel) -> Report:
        return Report(
            id=model.id,
            portfolio_id=model.portfolio_id,
            report_type=ReportType(model.report_type),
            title=model.title,
            markdown_content=model.markdown_content,
            html_content=model.html_content,
            period_start=model.period_start,
            period_end=model.period_end,
            generated_at=model.generated_at,
        )

    @staticmethod
    def to_model(entity: Report) -> ReportModel:
        return ReportModel(
            id=entity.id,
            portfolio_id=entity.portfolio_id,
            report_type=entity.report_type.value,
            title=entity.title,
            markdown_content=entity.markdown_content,
            html_content=entity.html_content,
            period_start=entity.period_start,
            period_end=entity.period_end,
            generated_at=entity.generated_at,
        )
