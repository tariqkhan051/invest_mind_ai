"""Dashboard API routes — docs/18_API.md §11."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_dashboard_service
from src.api.routes.market_intelligence import _map_summary as map_market_summary
from src.api.routes.portfolio import _map_summary as map_portfolio_summary
from src.api.routes.recommendation import _map_recommendation
from src.api.schemas import ApiResponse
from src.api.schemas.dashboard import (
    ActivityItemResponse,
    ChartPointResponse,
    DashboardChartsResponse,
    DashboardResponse,
)
from src.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]


@router.get("", response_model=ApiResponse[DashboardResponse])
def get_dashboard(
    service: DashboardServiceDep,
    portfolio_id: UUID | None = Query(default=None),
) -> ApiResponse[DashboardResponse]:
    """Return aggregated dashboard data."""
    dashboard = service.get_dashboard(portfolio_id=portfolio_id)
    return ApiResponse(
        message="Dashboard data retrieved",
        data=DashboardResponse(
            portfolio_summary=map_portfolio_summary(dashboard.portfolio_summary),
            market_summary=map_market_summary(dashboard.market_summary),
            latest_recommendations=[
                _map_recommendation(item) for item in dashboard.latest_recommendations
            ],
            charts=DashboardChartsResponse(
                allocation=[
                    ChartPointResponse(label=point.label, value=point.value)
                    for point in dashboard.charts.allocation
                ],
                portfolio_growth=[
                    ChartPointResponse(label=point.label, value=point.value)
                    for point in dashboard.charts.portfolio_growth
                ],
            ),
            recent_activity=[
                ActivityItemResponse(
                    activity_type=item.activity_type,
                    title=item.title,
                    description=item.description,
                    occurred_at=item.occurred_at,
                )
                for item in dashboard.recent_activity
            ],
        ),
    )
