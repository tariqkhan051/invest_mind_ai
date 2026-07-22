"""Unit tests for reporting engine."""

from decimal import Decimal

from src.domain.entities.portfolio import Portfolio
from src.domain.enums import ReportType
from src.engines.market_intelligence.models import (
    MarketScore,
    MarketSummary,
    RegimeAssessment,
    SentimentSummary,
)
from src.engines.portfolio.allocation_calculator import AllocationBreakdown
from src.engines.portfolio.engine import PortfolioPerformance, PortfolioValuation
from src.engines.reporting.generator import build_report_content, period_for_report
from src.engines.reporting.renderers import render_html, render_markdown
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


def _market_summary() -> MarketSummary:
    from datetime import date

    from src.domain.enums import MarketRegime, SentimentLabel

    return MarketSummary(
        score=MarketScore(
            overall_score=Decimal("72"),
            macro_score=Decimal("70"),
            sentiment_score=Decimal("68"),
            regime_score=Decimal("75"),
            calculation_date=date.today(),
        ),
        regime=RegimeAssessment(
            regime=MarketRegime.BULL,
            confidence=Decimal("80"),
            explanation="Positive macro backdrop.",
        ),
        sentiment=SentimentSummary(
            average_score=Decimal("0.2"),
            positive_count=3,
            neutral_count=2,
            negative_count=1,
            dominant_sentiment=SentimentLabel.POSITIVE,
        ),
        signals=[],
        alerts=[],
        latest_news=[],
        economy=__import__(
            "src.engines.market_intelligence.models",
            fromlist=["EconomySnapshot"],
        ).EconomySnapshot(),
    )


def test_period_for_daily_report() -> None:
    """Daily report period should be a single day."""
    start, end = period_for_report(ReportType.DAILY)
    assert start == end


def test_render_markdown_contains_sections() -> None:
    """Markdown renderer should include portfolio and market sections."""
    content = build_report_content(
        ReportType.DAILY,
        _portfolio_summary(),
        _market_summary(),
        [],
    )
    markdown = render_markdown(content)
    assert "# Daily Investment Report" in markdown
    assert "## Portfolio Summary" in markdown
    assert "## Market Intelligence" in markdown
    html = render_html(content)
    assert "<h1>" in html
