"""Stock API routes — docs/18_API.md §7."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_stock_service
from src.api.schemas import ApiResponse
from src.api.schemas.stock import (
    BuyOpportunityResponse,
    CompareStocksRequest,
    FundamentalMetricsResponse,
    PriceHistoryPointResponse,
    StockAnalysisResponse,
    StockComparisonResponse,
    StockPerformanceResponse,
    StockRankingResponse,
    TechnicalIndicatorsResponse,
)
from src.domain.read_models.price_history import PriceHistoryPoint
from src.engines.stock.models import StockAnalysis, StockRanking
from src.services.stock_service import StockService

router = APIRouter(prefix="/stocks", tags=["Stocks"])


def _map_performance(analysis: StockAnalysis) -> StockPerformanceResponse:
    return StockPerformanceResponse(
        daily_return=analysis.performance.daily_return,
        weekly_return=analysis.performance.weekly_return,
        monthly_return=analysis.performance.monthly_return,
        quarterly_return=analysis.performance.quarterly_return,
        yearly_return=analysis.performance.yearly_return,
        cagr_3y=analysis.performance.cagr_3y,
        volatility=analysis.performance.volatility,
        max_drawdown=analysis.performance.max_drawdown,
    )


def _map_technicals(analysis: StockAnalysis) -> TechnicalIndicatorsResponse:
    return TechnicalIndicatorsResponse(
        sma_20=analysis.technicals.sma_20,
        sma_50=analysis.technicals.sma_50,
        ema_12=analysis.technicals.ema_12,
        rsi_14=analysis.technicals.rsi_14,
        momentum=analysis.technicals.momentum,
        volume_trend=analysis.technicals.volume_trend,
    )


def _map_fundamentals(analysis: StockAnalysis) -> FundamentalMetricsResponse:
    return FundamentalMetricsResponse(
        eps=analysis.fundamentals.eps,
        pe=analysis.fundamentals.pe,
        pbv=analysis.fundamentals.pbv,
        roe=analysis.fundamentals.roe,
        roa=analysis.fundamentals.roa,
        debt_ratio=analysis.fundamentals.debt_ratio,
        dividend_yield=analysis.fundamentals.dividend_yield,
        market_cap=analysis.fundamentals.market_cap,
    )


def _map_analysis(analysis: StockAnalysis) -> StockAnalysisResponse:
    return StockAnalysisResponse(
        asset_id=analysis.asset_id,
        symbol=analysis.symbol,
        display_name=analysis.display_name,
        company_name=analysis.company_name,
        sector=analysis.sector,
        industry=analysis.industry,
        is_shariah=analysis.is_shariah,
        latest_price=analysis.latest_price,
        latest_price_date=analysis.latest_price_date,
        performance=_map_performance(analysis),
        technicals=_map_technicals(analysis),
        fundamentals=_map_fundamentals(analysis),
        ai_score=analysis.ai_score,
    )


def _map_ranking(ranking: StockRanking) -> StockRankingResponse:
    return StockRankingResponse(
        rank=ranking.rank,
        asset_id=ranking.asset_id,
        symbol=ranking.symbol,
        display_name=ranking.display_name,
        ai_score=ranking.ai_score,
        yearly_return=ranking.yearly_return,
        rsi_14=ranking.rsi_14,
    )


def _map_price_point(point: PriceHistoryPoint) -> PriceHistoryPointResponse:
    return PriceHistoryPointResponse(
        price_date=point.price_date,
        close_price=point.close_price,
        open_price=point.open_price,
        high_price=point.high_price,
        low_price=point.low_price,
        adjusted_close=point.adjusted_close,
        volume=point.volume,
    )


@router.get("", response_model=ApiResponse[list[StockAnalysisResponse]])
def list_stocks(
    service: Annotated[StockService, Depends(get_stock_service)],
    shariah_only: bool = Query(default=False),
    sector: str | None = Query(default=None),
) -> ApiResponse[list[StockAnalysisResponse]]:
    """List all stocks with analysis."""
    stocks = service.list_stocks(shariah_only=shariah_only, sector=sector)
    return ApiResponse(
        message="Stocks retrieved",
        data=[_map_analysis(stock) for stock in stocks],
    )


@router.get("/rankings", response_model=ApiResponse[list[StockRankingResponse]])
def get_rankings(
    service: Annotated[StockService, Depends(get_stock_service)],
    shariah_only: bool = Query(default=False),
    sector: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=100),
) -> ApiResponse[list[StockRankingResponse]]:
    """Return ranked stocks."""
    rankings = service.get_rankings(
        shariah_only=shariah_only,
        sector=sector,
        limit=limit,
    )
    return ApiResponse(
        message="Stock rankings retrieved",
        data=[_map_ranking(item) for item in rankings],
    )


@router.get(
    "/opportunities",
    response_model=ApiResponse[list[BuyOpportunityResponse]],
)
def get_buy_opportunities(
    service: Annotated[StockService, Depends(get_stock_service)],
    shariah_only: bool = Query(default=False),
    sector: str | None = Query(default=None),
) -> ApiResponse[list[BuyOpportunityResponse]]:
    """Return potential stock buy opportunities."""
    opportunities = service.get_buy_opportunities(
        shariah_only=shariah_only,
        sector=sector,
    )
    return ApiResponse(
        message="Buy opportunities retrieved",
        data=[
            BuyOpportunityResponse(
                asset_id=item.asset_id,
                symbol=item.symbol,
                opportunity_type=item.opportunity_type,
                reason=item.reason,
                confidence=item.confidence,
                expected_return_pct=item.expected_return_pct,
                risk_level=item.risk_level,
            )
            for item in opportunities
        ],
    )


@router.post("/compare", response_model=ApiResponse[StockComparisonResponse])
def compare_stocks(
    request: CompareStocksRequest,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> ApiResponse[StockComparisonResponse]:
    """Compare multiple stocks."""
    comparison = service.compare_stocks(request.symbols)
    return ApiResponse(
        message="Stock comparison completed",
        data=StockComparisonResponse(
            stocks=[_map_analysis(stock) for stock in comparison.stocks],
        ),
    )


@router.get("/{symbol}", response_model=ApiResponse[StockAnalysisResponse])
def get_stock(
    symbol: str,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> ApiResponse[StockAnalysisResponse]:
    """Get analyzed details for one stock."""
    stock = service.get_stock(symbol.upper())
    return ApiResponse(message="Stock retrieved", data=_map_analysis(stock))


@router.get(
    "/{symbol}/history",
    response_model=ApiResponse[list[PriceHistoryPointResponse]],
)
def get_stock_history(
    symbol: str,
    service: Annotated[StockService, Depends(get_stock_service)],
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> ApiResponse[list[PriceHistoryPointResponse]]:
    """Get price history for a stock."""
    history = service.get_price_history(
        symbol.upper(),
        from_date=from_date,
        to_date=to_date,
    )
    return ApiResponse(
        message="Price history retrieved",
        data=[_map_price_point(point) for point in history],
    )
