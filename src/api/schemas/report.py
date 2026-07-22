"""Report API schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from src.domain.enums import ReportType


class ReportSummaryResponse(BaseModel):
    """Report list item without full content."""

    id: UUID
    portfolio_id: UUID | None
    report_type: str
    title: str
    period_start: date | None
    period_end: date | None
    generated_at: datetime


class ReportDetailResponse(ReportSummaryResponse):
    """Full report with rendered content."""

    markdown_content: str
    html_content: str


class ReportHistoryMeta(BaseModel):
    """Pagination metadata for report history."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class ReportHistoryResponse(BaseModel):
    """Paginated report history."""

    items: list[ReportSummaryResponse]
    meta: ReportHistoryMeta


class GenerateReportRequest(BaseModel):
    """Request body for manual report generation."""

    report_type: ReportType = ReportType.DAILY
    portfolio_id: UUID | None = None
