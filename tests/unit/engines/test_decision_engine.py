"""Unit tests for decision engine."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.portfolio import Portfolio
from src.domain.enums import MarketRegime, RecommendationType, SentimentLabel
from src.engines.decision.generator import generate_recommendations
from src.engines.decision.models import DecisionContext
from src.engines.decision.opportunity_builder import build_candidates
from src.engines.market_intelligence.models import (
    EconomySnapshot,
    MarketScore,
    MarketSummary,
    RegimeAssessment,
    SentimentSummary,
)
from src.engines.mutual_fund.models import FundAnalysis, FundPerformanceMetrics
from src.engines.portfolio.allocation_calculator import AllocationBreakdown
from src.engines.portfolio.engine import (
    PortfolioPerformance,
    PortfolioValuation,
)
from src.services.portfolio_service import PortfolioSummary


def _portfolio_summary() -> PortfolioSummary:
    portfolio = Portfolio(name="Primary Portfolio")
    return PortfolioSummary(
        portfolio=portfolio,
        valuation=PortfolioValuation(
            total_value=Decimal("100000"),
            investment_value=Decimal("90000"),
            total_invested=Decimal("90000"),
            cash_balance=Decimal("10000"),
            unrealized_gain=Decimal("5000"),
            realized_gain=Decimal("0"),
        ),
        performance=PortfolioPerformance(
            absolute_return=Decimal("5000"),
            percentage_return=Decimal("5.5"),
            xirr=None,
            cagr=None,
        ),
        allocation=AllocationBreakdown(
            by_asset_type={},
            by_holding=[],
            cash_percentage=Decimal("10"),
        ),
    )


def _market_summary(regime: MarketRegime = MarketRegime.BULL) -> MarketSummary:
    return MarketSummary(
        score=MarketScore(
            overall_score=Decimal("70"),
            macro_score=Decimal("65"),
            sentiment_score=Decimal("72"),
            regime_score=Decimal("70"),
            calculation_date=datetime(2026, 7, 10).date(),
        ),
        regime=RegimeAssessment(
            regime=regime,
            confidence=Decimal("0.75"),
            explanation="Bullish environment.",
        ),
        sentiment=SentimentSummary(
            average_score=Decimal("20"),
            positive_count=3,
            neutral_count=1,
            negative_count=0,
            dominant_sentiment=SentimentLabel.POSITIVE,
        ),
        signals=[],
        alerts=[],
        latest_news=[],
        economy=EconomySnapshot(indicators=[]),
    )


def test_build_candidates_includes_fund_invest_opportunity() -> None:
    """Bull regime with ranked funds should produce invest candidates."""
    fund = FundAnalysis(
        asset_id=uuid4(),
        symbol="MIF",
        display_name="Meezan Islamic Fund",
        asset_type="mutual_fund",
        is_shariah=True,
        management_company="Meezan",
        expense_ratio=Decimal("1.5"),
        aum=Decimal("10000000000"),
        latest_nav=Decimal("100"),
        latest_nav_date=datetime(2026, 1, 1).date(),
        performance=FundPerformanceMetrics(yearly_return=Decimal("18")),
        ai_score=Decimal("82"),
    )
    context = DecisionContext(
        portfolio=_portfolio_summary(),
        market=_market_summary(),
        funds=[fund],
        stocks=[],
        switch_opportunities=[],
        buy_opportunities=[],
        monthly_investment=Decimal("50000"),
    )
    candidates = build_candidates(context)
    assert any(
        candidate.recommendation_type == RecommendationType.INVEST
        for candidate in candidates
    )


def test_generate_recommendations_returns_no_action_when_empty() -> None:
    """Empty opportunity set should still return a no-action recommendation."""
    context = DecisionContext(
        portfolio=_portfolio_summary(),
        market=_market_summary(regime=MarketRegime.NEUTRAL),
        funds=[],
        stocks=[],
        switch_opportunities=[],
        buy_opportunities=[],
        monthly_investment=Decimal("50000"),
    )
    recommendations = generate_recommendations(
        context,
        _portfolio_summary().portfolio.id,
        min_confidence=Decimal("60"),
        generated_at=datetime(2026, 7, 10, tzinfo=UTC),
    )
    assert len(recommendations) == 1
    assert recommendations[0].recommendation_type == RecommendationType.NO_ACTION
    assert recommendations[0].confidence >= Decimal("0")
