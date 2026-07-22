"""Report application service."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from uuid import UUID

from src.config.settings import Settings
from src.core.exceptions import ConfigurationError, ReportNotFoundError
from src.core.logging import get_logger
from src.domain.entities.report import Report
from src.domain.enums import NotificationType, ReportType
from src.engines.reporting.generator import build_report_content, generated_timestamp
from src.engines.reporting.renderers import render_html, render_markdown
from src.repositories.interfaces.report_repository import ReportRepository
from src.services.learning_service import LearningService
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.notification_service import NotificationService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService

logger = get_logger("services.report")


@dataclass
class PaginatedReports:
    """Paginated report history."""

    items: list[Report]
    page: int
    page_size: int
    total_items: int
    total_pages: int


class ReportService:
    """Generate, persist, and retrieve investment reports."""

    def __init__(
        self,
        report_repository: ReportRepository,
        portfolio_service: PortfolioService,
        market_intelligence_service: MarketIntelligenceService,
        recommendation_service: RecommendationService,
        settings: Settings,
        learning_service: LearningService | None = None,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._report_repository = report_repository
        self._portfolio_service = portfolio_service
        self._market_intelligence_service = market_intelligence_service
        self._recommendation_service = recommendation_service
        self._learning_service = learning_service
        self._notification_service = notification_service
        self._settings = settings

    def is_enabled(self) -> bool:
        """Return True when reports feature flag is on."""
        return bool(
            self._settings.features_config.get("features", {}).get("reports", True)
        )

    def generate(
        self,
        report_type: ReportType,
        portfolio_id: UUID | None = None,
    ) -> Report:
        """Generate and persist a new report."""
        if not self.is_enabled():
            raise ConfigurationError("Reports feature is disabled.")

        portfolio_summary = self._portfolio_service.get_summary(portfolio_id)
        market_summary = self._market_intelligence_service.get_summary()
        recommendations = self._recommendation_service.get_latest(portfolio_id)
        learning_report = None
        if self._learning_service is not None:
            learning_report = self._learning_service.get_self_evaluation()

        content = build_report_content(
            report_type,
            portfolio_summary,
            market_summary,
            recommendations,
            learning_report=learning_report,
        )
        report = Report(
            portfolio_id=portfolio_summary.portfolio.id,
            report_type=report_type,
            title=content.title,
            markdown_content=render_markdown(content),
            html_content=render_html(content),
            period_start=content.period_start,
            period_end=content.period_end,
            generated_at=generated_timestamp(),
        )
        saved = self._report_repository.save(report)
        self._write_report_files(saved)
        self._notify_report_ready(saved)
        logger.info(
            "report_generated type={} portfolio_id={}",
            report_type.value,
            saved.portfolio_id,
        )
        return saved

    def get_report(self, report_id: UUID) -> Report:
        """Return one report by id."""
        report = self._report_repository.get_by_id(report_id)
        if report is None:
            raise ReportNotFoundError(f"Report {report_id} not found.")
        return report

    def get_latest(self, report_type: ReportType) -> Report:
        """Return the latest report of a given type."""
        report = self._report_repository.get_latest(report_type)
        if report is None:
            raise ReportNotFoundError(f"No {report_type.value} report found.")
        return report

    def list_reports(
        self,
        page: int = 1,
        page_size: int = 25,
        report_type: ReportType | None = None,
    ) -> PaginatedReports:
        """Return paginated report history."""
        total_items = self._report_repository.count(report_type=report_type)
        offset = (page - 1) * page_size
        items = self._report_repository.list_reports(
            limit=page_size,
            offset=offset,
            report_type=report_type,
        )
        total_pages = ceil(total_items / page_size) if page_size else 0
        return PaginatedReports(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )

    def _write_report_files(self, report: Report) -> None:
        reports_root = (
            self._settings.project_root / "reports" / report.report_type.value
        )
        reports_root.mkdir(parents=True, exist_ok=True)
        period_label = (
            report.period_end.isoformat()
            if report.period_end is not None
            else report.generated_at.date().isoformat()
        )
        stem = f"report_{period_label}_{report.id}"
        (reports_root / f"{stem}.md").write_text(
            report.markdown_content,
            encoding="utf-8",
        )
        (reports_root / f"{stem}.html").write_text(
            report.html_content,
            encoding="utf-8",
        )

    def _notify_report_ready(self, report: Report) -> None:
        if self._notification_service is None:
            return
        self._notification_service.send(
            title=f"{report.report_type.value.title()} report ready",
            body=report.title,
            notification_type=NotificationType.REPORT_READY,
            metadata={"report_id": str(report.id)},
        )
