"""Market intelligence API routes — docs/18_API.md §8."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_market_intelligence_service
from src.api.schemas import ApiResponse
from src.api.schemas.market_intelligence import (
    EconomyResponse,
    InvestmentSignalResponse,
    MacroIndicatorResponse,
    MarketAlertResponse,
    MarketScoreResponse,
    MarketSummaryResponse,
    NewsArticleResponse,
    RegimeResponse,
    SentimentSummaryResponse,
)
from src.domain.enums import NewsCategory
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.domain.read_models.news_article import NewsArticle
from src.engines.market_intelligence.models import (
    InvestmentSignal,
    MarketAlert,
    MarketScore,
    MarketSummary,
    RegimeAssessment,
    SentimentSummary,
)
from src.services.market_intelligence_service import MarketIntelligenceService

router = APIRouter(prefix="/market", tags=["Market Intelligence"])

MarketIntelligenceServiceDep = Annotated[
    MarketIntelligenceService,
    Depends(get_market_intelligence_service),
]


def _map_macro(indicator: MacroIndicatorPoint) -> MacroIndicatorResponse:
    return MacroIndicatorResponse(
        indicator_name=indicator.indicator_name,
        release_date=indicator.release_date,
        actual_value=indicator.actual_value,
        country=indicator.country,
        forecast_value=indicator.forecast_value,
        previous_value=indicator.previous_value,
        unit=indicator.unit,
        trend=indicator.trend,
        source=indicator.source,
    )


def _map_news(article: NewsArticle) -> NewsArticleResponse:
    return NewsArticleResponse(
        id=article.id,
        headline=article.headline,
        summary=article.summary,
        publisher=article.publisher,
        publication_time=article.publication_time,
        url=article.url,
        country=article.country,
        category=article.category.value,
        sentiment=article.sentiment.value,
        sentiment_score=article.sentiment_score,
        source=article.source,
    )


def _map_sentiment(sentiment: SentimentSummary) -> SentimentSummaryResponse:
    return SentimentSummaryResponse(
        average_score=sentiment.average_score,
        positive_count=sentiment.positive_count,
        neutral_count=sentiment.neutral_count,
        negative_count=sentiment.negative_count,
        dominant_sentiment=sentiment.dominant_sentiment.value,
    )


def _map_regime(regime: RegimeAssessment) -> RegimeResponse:
    return RegimeResponse(
        regime=regime.regime.value,
        confidence=regime.confidence,
        explanation=regime.explanation,
    )


def _map_score(score: MarketScore) -> MarketScoreResponse:
    return MarketScoreResponse(
        overall_score=score.overall_score,
        macro_score=score.macro_score,
        sentiment_score=score.sentiment_score,
        regime_score=score.regime_score,
        calculation_date=score.calculation_date,
    )


def _map_signal(signal: InvestmentSignal) -> InvestmentSignalResponse:
    return InvestmentSignalResponse(
        signal_type=signal.signal_type.value,
        message=signal.message,
        confidence=signal.confidence,
    )


def _map_alert(alert: MarketAlert) -> MarketAlertResponse:
    return MarketAlertResponse(
        alert_type=alert.alert_type,
        severity=alert.severity.value,
        message=alert.message,
        detected_at=alert.detected_at,
    )


def _map_summary(summary: MarketSummary) -> MarketSummaryResponse:
    return MarketSummaryResponse(
        score=_map_score(summary.score),
        regime=_map_regime(summary.regime),
        sentiment=_map_sentiment(summary.sentiment),
        signals=[_map_signal(item) for item in summary.signals],
        alerts=[_map_alert(item) for item in summary.alerts],
        latest_news=[_map_news(item) for item in summary.latest_news],
        economy=EconomyResponse(
            indicators=[_map_macro(item) for item in summary.economy.indicators],
        ),
        news_by_category={
            category.value: count
            for category, count in summary.news_by_category.items()
        },
    )


@router.get("/summary", response_model=ApiResponse[MarketSummaryResponse])
def get_market_summary(
    service: MarketIntelligenceServiceDep,
    country: str = Query(default="PK"),
) -> ApiResponse[MarketSummaryResponse]:
    """Return the complete market intelligence summary."""
    summary = service.get_summary(country=country)
    return ApiResponse(
        message="Market summary retrieved",
        data=_map_summary(summary),
    )


@router.get("/news", response_model=ApiResponse[list[NewsArticleResponse]])
def get_market_news(
    service: MarketIntelligenceServiceDep,
    limit: int = Query(default=50, ge=1, le=200),
    category: NewsCategory | None = Query(default=None),
    country: str = Query(default="PK"),
) -> ApiResponse[list[NewsArticleResponse]]:
    """Return latest market news."""
    articles = service.get_news(limit=limit, category=category, country=country)
    return ApiResponse(
        message="Market news retrieved",
        data=[_map_news(item) for item in articles],
    )


@router.get("/news/{article_id}", response_model=ApiResponse[NewsArticleResponse])
def get_market_news_article(
    article_id: UUID,
    service: MarketIntelligenceServiceDep,
) -> ApiResponse[NewsArticleResponse]:
    """Return one news article."""
    article = service.get_news_article(article_id)
    return ApiResponse(message="News article retrieved", data=_map_news(article))


@router.get("/economy", response_model=ApiResponse[EconomyResponse])
def get_market_economy(
    service: MarketIntelligenceServiceDep,
    country: str = Query(default="PK"),
) -> ApiResponse[EconomyResponse]:
    """Return latest macroeconomic indicators."""
    economy = service.get_economy(country=country)
    return ApiResponse(
        message="Economic indicators retrieved",
        data=EconomyResponse(
            indicators=[_map_macro(item) for item in economy.indicators],
        ),
    )


@router.get("/regime", response_model=ApiResponse[RegimeResponse])
def get_market_regime(
    service: MarketIntelligenceServiceDep,
    country: str = Query(default="PK"),
) -> ApiResponse[RegimeResponse]:
    """Return the detected market regime."""
    regime = service.get_regime(country=country)
    return ApiResponse(
        message="Market regime retrieved",
        data=_map_regime(regime),
    )


@router.get("/score", response_model=ApiResponse[MarketScoreResponse])
def get_market_score(
    service: MarketIntelligenceServiceDep,
    country: str = Query(default="PK"),
) -> ApiResponse[MarketScoreResponse]:
    """Return the market intelligence score."""
    score = service.get_score(country=country)
    return ApiResponse(
        message="Market score retrieved",
        data=_map_score(score),
    )


@router.get("/signals", response_model=ApiResponse[list[InvestmentSignalResponse]])
def get_market_signals(
    service: MarketIntelligenceServiceDep,
    country: str = Query(default="PK"),
) -> ApiResponse[list[InvestmentSignalResponse]]:
    """Return investment signals for the current regime."""
    signals = service.get_signals(country=country)
    return ApiResponse(
        message="Market signals retrieved",
        data=[_map_signal(item) for item in signals],
    )


@router.get("/alerts", response_model=ApiResponse[list[MarketAlertResponse]])
def get_market_alerts(
    service: MarketIntelligenceServiceDep,
    country: str = Query(default="PK"),
) -> ApiResponse[list[MarketAlertResponse]]:
    """Return market alerts."""
    alerts = service.get_alerts(country=country)
    return ApiResponse(
        message="Market alerts retrieved",
        data=[_map_alert(item) for item in alerts],
    )
