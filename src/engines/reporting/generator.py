"""Report content generation."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from src.domain.entities.recommendation import Recommendation
from src.domain.enums import ReportType
from src.engines.learning.models import SelfEvaluationReport
from src.engines.market_intelligence.models import MarketSummary
from src.engines.reporting.models import (
    MarketReportData,
    PortfolioReportData,
    RecommendationReportItem,
    ReportContent,
    ReportSection,
)
from src.services.portfolio_service import PortfolioSummary


def period_for_report(
    report_type: ReportType,
    reference_date: date | None = None,
) -> tuple[date, date]:
    """Return inclusive period bounds for a report type."""
    end = reference_date or date.today()
    if report_type == ReportType.DAILY:
        return end, end
    if report_type == ReportType.WEEKLY:
        return end - timedelta(days=6), end
    if report_type == ReportType.MONTHLY:
        return end.replace(day=1), end
    return date(end.year, 1, 1), end


def build_report_content(
    report_type: ReportType,
    portfolio: PortfolioSummary,
    market: MarketSummary,
    recommendations: list[Recommendation],
    learning_report: SelfEvaluationReport | None = None,
    reference_date: date | None = None,
) -> ReportContent:
    """Build structured report content from application data."""
    period_start, period_end = period_for_report(report_type, reference_date)
    portfolio_data = PortfolioReportData(
        portfolio_name=portfolio.portfolio.name,
        total_value=portfolio.valuation.total_value,
        investment_value=portfolio.valuation.investment_value,
        cash_balance=portfolio.valuation.cash_balance,
        percentage_return=portfolio.performance.percentage_return,
        cash_percentage=portfolio.allocation.cash_percentage,
    )
    market_data = MarketReportData(
        regime=market.regime.regime.value,
        market_score=market.score.overall_score,
        dominant_sentiment=market.sentiment.dominant_sentiment.value,
        headline_count=len(market.latest_news),
    )
    recommendation_items = [
        RecommendationReportItem(
            recommendation_type=item.recommendation_type.value,
            symbol=item.symbol,
            confidence=item.confidence,
            reason=item.reason,
        )
        for item in recommendations
    ]
    return ReportContent(
        title=_title_for_type(report_type, period_end),
        report_type=report_type.value,
        period_start=period_start,
        period_end=period_end,
        summary_line=(
            f"Portfolio value PKR {portfolio_data.total_value:,.2f} with "
            f"{portfolio_data.percentage_return:.2f}% return."
        ),
        sections=[
            _portfolio_section(portfolio_data),
            _market_section(market_data),
            _recommendations_section(recommendation_items),
            *_learning_sections(learning_report),
        ],
    )


def _title_for_type(report_type: ReportType, period_end: date) -> str:
    label = report_type.value.replace("_", " ").title()
    return f"{label} Investment Report — {period_end.isoformat()}"


def _portfolio_section(data: PortfolioReportData) -> ReportSection:
    return ReportSection(
        heading="Portfolio Summary",
        lines=[
            f"Portfolio: {data.portfolio_name}",
            f"Total value: PKR {data.total_value:,.2f}",
            f"Invested value: PKR {data.investment_value:,.2f}",
            f"Cash balance: PKR {data.cash_balance:,.2f}",
            f"Return: {data.percentage_return:.2f}%",
            f"Cash allocation: {data.cash_percentage:.2f}%",
        ],
    )


def _market_section(data: MarketReportData) -> ReportSection:
    return ReportSection(
        heading="Market Intelligence",
        lines=[
            f"Market regime: {data.regime}",
            f"Market score: {data.market_score:.1f}",
            f"Dominant sentiment: {data.dominant_sentiment}",
            f"Recent headlines tracked: {data.headline_count}",
        ],
    )


def _recommendations_section(items: list[RecommendationReportItem]) -> ReportSection:
    if not items:
        return ReportSection(
            heading="AI Recommendations",
            lines=["No active recommendations for this period."],
        )
    lines: list[str] = []
    for item in items:
        symbol = item.symbol or "N/A"
        lines.append(
            f"{item.recommendation_type.upper()} {symbol} "
            f"(confidence {item.confidence:.0f}%): {item.reason}"
        )
    return ReportSection(heading="AI Recommendations", lines=lines)


def _learning_sections(
    learning_report: SelfEvaluationReport | None,
) -> list[ReportSection]:
    if learning_report is None or learning_report.total_records == 0:
        return []
    return [
        ReportSection(
            heading="Learning Performance",
            lines=[
                f"Total learning records: {learning_report.total_records}",
                f"Accuracy rate: {learning_report.accuracy_rate:.2f}%",
                f"Average prediction error: "
                f"{learning_report.average_prediction_error or Decimal('0'):.2f}",
            ],
        )
    ]


def generated_timestamp() -> datetime:
    """Return current UTC timestamp for report generation."""
    return datetime.now(UTC)
