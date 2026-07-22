"""Mutual fund API routes — docs/18_API.md §6."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_mutual_fund_service
from src.api.schemas import ApiResponse
from src.api.schemas.mutual_fund import (
    CompareFundsRequest,
    FundAnalysisResponse,
    FundCategoryResponse,
    FundComparisonResponse,
    FundPerformanceResponse,
    FundRankingResponse,
    FundRiskResponse,
    NavHistoryPointResponse,
    SwitchOpportunityResponse,
)
from src.domain.enums import AssetType
from src.domain.read_models.nav_history import NavHistoryPoint
from src.engines.mutual_fund.models import FundAnalysis, FundRanking
from src.services.mutual_fund_service import FundCategorySummary, MutualFundService

router = APIRouter(prefix="/funds", tags=["Mutual Funds"])


def _map_performance(analysis: FundAnalysis) -> FundPerformanceResponse:
    return FundPerformanceResponse(
        daily_return=analysis.performance.daily_return,
        weekly_return=analysis.performance.weekly_return,
        monthly_return=analysis.performance.monthly_return,
        quarterly_return=analysis.performance.quarterly_return,
        yearly_return=analysis.performance.yearly_return,
        cagr_3y=analysis.performance.cagr_3y,
        cagr_5y=analysis.performance.cagr_5y,
        since_inception_return=analysis.performance.since_inception_return,
    )


def _map_risk(analysis: FundAnalysis) -> FundRiskResponse:
    return FundRiskResponse(
        volatility=analysis.risk.volatility,
        standard_deviation=analysis.risk.standard_deviation,
        max_drawdown=analysis.risk.max_drawdown,
        downside_risk=analysis.risk.downside_risk,
    )


def _map_analysis(analysis: FundAnalysis) -> FundAnalysisResponse:
    return FundAnalysisResponse(
        asset_id=analysis.asset_id,
        symbol=analysis.symbol,
        display_name=analysis.display_name,
        asset_type=analysis.asset_type,
        is_shariah=analysis.is_shariah,
        management_company=analysis.management_company,
        expense_ratio=analysis.expense_ratio,
        aum=analysis.aum,
        latest_nav=analysis.latest_nav,
        latest_nav_date=analysis.latest_nav_date,
        performance=_map_performance(analysis),
        risk=_map_risk(analysis),
        ai_score=analysis.ai_score,
    )


def _map_ranking(ranking: FundRanking) -> FundRankingResponse:
    return FundRankingResponse(
        rank=ranking.rank,
        asset_id=ranking.asset_id,
        symbol=ranking.symbol,
        display_name=ranking.display_name,
        ai_score=ranking.ai_score,
        yearly_return=ranking.yearly_return,
        volatility=ranking.volatility,
    )


def _map_nav_point(point: NavHistoryPoint) -> NavHistoryPointResponse:
    return NavHistoryPointResponse(
        nav_date=point.nav_date,
        nav=point.nav,
        daily_return=point.daily_return,
    )


def _map_category(summary: FundCategorySummary) -> FundCategoryResponse:
    return FundCategoryResponse(
        category=summary.category,
        fund_count=summary.fund_count,
        average_yearly_return=summary.average_yearly_return,
        average_volatility=summary.average_volatility,
        top_performer=summary.top_performer,
    )


@router.get("", response_model=ApiResponse[list[FundAnalysisResponse]])
def list_funds(
    service: Annotated[MutualFundService, Depends(get_mutual_fund_service)],
    shariah_only: bool = Query(default=False),
    category: AssetType | None = Query(default=None),
) -> ApiResponse[list[FundAnalysisResponse]]:
    """List all mutual funds with analysis."""
    funds = service.list_funds(shariah_only=shariah_only, category=category)
    return ApiResponse(
        message="Funds retrieved",
        data=[_map_analysis(fund) for fund in funds],
    )


@router.get("/rankings", response_model=ApiResponse[list[FundRankingResponse]])
def get_rankings(
    service: Annotated[MutualFundService, Depends(get_mutual_fund_service)],
    shariah_only: bool = Query(default=False),
    category: AssetType | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=100),
) -> ApiResponse[list[FundRankingResponse]]:
    """Return ranked mutual funds."""
    rankings = service.get_rankings(
        shariah_only=shariah_only,
        category=category,
        limit=limit,
    )
    return ApiResponse(
        message="Fund rankings retrieved",
        data=[_map_ranking(item) for item in rankings],
    )


@router.get("/categories", response_model=ApiResponse[list[FundCategoryResponse]])
def get_categories(
    service: Annotated[MutualFundService, Depends(get_mutual_fund_service)],
    shariah_only: bool = Query(default=False),
) -> ApiResponse[list[FundCategoryResponse]]:
    """Return fund category summaries."""
    categories = service.get_categories(shariah_only=shariah_only)
    return ApiResponse(
        message="Fund categories retrieved",
        data=[_map_category(item) for item in categories],
    )


@router.get(
    "/switch-opportunities",
    response_model=ApiResponse[list[SwitchOpportunityResponse]],
)
def get_switch_opportunities(
    service: Annotated[MutualFundService, Depends(get_mutual_fund_service)],
    shariah_only: bool = Query(default=False),
    category: AssetType | None = Query(default=None),
) -> ApiResponse[list[SwitchOpportunityResponse]]:
    """Return potential fund switch opportunities."""
    opportunities = service.get_switch_opportunities(
        shariah_only=shariah_only,
        category=category,
    )
    return ApiResponse(
        message="Switch opportunities retrieved",
        data=[
            SwitchOpportunityResponse(
                from_asset_id=item.from_asset_id,
                from_symbol=item.from_symbol,
                to_asset_id=item.to_asset_id,
                to_symbol=item.to_symbol,
                expected_benefit_pct=item.expected_benefit_pct,
                reason=item.reason,
                confidence=item.confidence,
            )
            for item in opportunities
        ],
    )


@router.post("/compare", response_model=ApiResponse[FundComparisonResponse])
def compare_funds(
    request: CompareFundsRequest,
    service: Annotated[MutualFundService, Depends(get_mutual_fund_service)],
) -> ApiResponse[FundComparisonResponse]:
    """Compare multiple mutual funds."""
    comparison = service.compare_funds(request.fund_ids)
    return ApiResponse(
        message="Fund comparison completed",
        data=FundComparisonResponse(
            funds=[_map_analysis(fund) for fund in comparison.funds],
        ),
    )


@router.get("/{asset_id}", response_model=ApiResponse[FundAnalysisResponse])
def get_fund(
    asset_id: UUID,
    service: Annotated[MutualFundService, Depends(get_mutual_fund_service)],
) -> ApiResponse[FundAnalysisResponse]:
    """Get analyzed details for one fund."""
    fund = service.get_fund(asset_id)
    return ApiResponse(message="Fund retrieved", data=_map_analysis(fund))


@router.get(
    "/{asset_id}/history",
    response_model=ApiResponse[list[NavHistoryPointResponse]],
)
def get_fund_history(
    asset_id: UUID,
    service: Annotated[MutualFundService, Depends(get_mutual_fund_service)],
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> ApiResponse[list[NavHistoryPointResponse]]:
    """Get NAV history for a fund."""
    history = service.get_nav_history(
        asset_id,
        from_date=from_date,
        to_date=to_date,
    )
    return ApiResponse(
        message="NAV history retrieved",
        data=[_map_nav_point(point) for point in history],
    )
