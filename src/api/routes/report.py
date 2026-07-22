"""Report API routes — docs/18_API.md §10."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_report_service
from src.api.schemas import ApiResponse
from src.api.schemas.report import (
    GenerateReportRequest,
    ReportDetailResponse,
    ReportHistoryMeta,
    ReportHistoryResponse,
    ReportSummaryResponse,
)
from src.core.constants import DEFAULT_PAGE_SIZE
from src.domain.entities.report import Report
from src.domain.enums import ReportType
from src.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])

ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]


def _map_summary(report: Report) -> ReportSummaryResponse:
    return ReportSummaryResponse(
        id=report.id,
        portfolio_id=report.portfolio_id,
        report_type=report.report_type.value,
        title=report.title,
        period_start=report.period_start,
        period_end=report.period_end,
        generated_at=report.generated_at,
    )


def _map_detail(report: Report) -> ReportDetailResponse:
    return ReportDetailResponse(
        **_map_summary(report).model_dump(),
        markdown_content=report.markdown_content,
        html_content=report.html_content,
    )


@router.get("", response_model=ApiResponse[ReportHistoryResponse])
def list_reports(
    service: ReportServiceDep,
    report_type: ReportType | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
) -> ApiResponse[ReportHistoryResponse]:
    """Return paginated report history."""
    history = service.list_reports(
        page=page,
        page_size=page_size,
        report_type=report_type,
    )
    return ApiResponse(
        message="Reports retrieved",
        data=ReportHistoryResponse(
            items=[_map_summary(item) for item in history.items],
            meta=ReportHistoryMeta(
                page=history.page,
                page_size=history.page_size,
                total_items=history.total_items,
                total_pages=history.total_pages,
            ),
        ),
    )


@router.get("/daily", response_model=ApiResponse[ReportDetailResponse])
def get_daily_report(service: ReportServiceDep) -> ApiResponse[ReportDetailResponse]:
    """Return the latest daily report."""
    report = service.get_latest(ReportType.DAILY)
    return ApiResponse(
        message="Daily report retrieved",
        data=_map_detail(report),
    )


@router.get("/monthly", response_model=ApiResponse[ReportDetailResponse])
def get_monthly_report(service: ReportServiceDep) -> ApiResponse[ReportDetailResponse]:
    """Return the latest monthly report."""
    report = service.get_latest(ReportType.MONTHLY)
    return ApiResponse(
        message="Monthly report retrieved",
        data=_map_detail(report),
    )


@router.get("/{report_id}", response_model=ApiResponse[ReportDetailResponse])
def get_report(
    report_id: UUID,
    service: ReportServiceDep,
) -> ApiResponse[ReportDetailResponse]:
    """Return one report by id."""
    report = service.get_report(report_id)
    return ApiResponse(
        message="Report retrieved",
        data=_map_detail(report),
    )


@router.post("/generate", response_model=ApiResponse[ReportDetailResponse])
def generate_report(
    request: GenerateReportRequest,
    service: ReportServiceDep,
) -> ApiResponse[ReportDetailResponse]:
    """Generate a new investment report."""
    report = service.generate(
        request.report_type,
        portfolio_id=request.portfolio_id,
    )
    return ApiResponse(
        message="Report generated",
        data=_map_detail(report),
    )
