"""Reporting engine data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class ReportSection:
    """Single section within a report."""

    heading: str
    lines: list[str] = field(default_factory=list)


@dataclass
class ReportContent:
    """Structured report content before rendering."""

    title: str
    report_type: str
    period_start: date
    period_end: date
    sections: list[ReportSection] = field(default_factory=list)
    summary_line: str = ""


@dataclass
class PortfolioReportData:
    """Portfolio metrics for report generation."""

    portfolio_name: str
    total_value: Decimal
    investment_value: Decimal
    cash_balance: Decimal
    percentage_return: Decimal
    cash_percentage: Decimal


@dataclass
class MarketReportData:
    """Market intelligence metrics for report generation."""

    regime: str
    market_score: Decimal
    dominant_sentiment: str
    headline_count: int


@dataclass
class RecommendationReportItem:
    """Recommendation summary line for reports."""

    recommendation_type: str
    symbol: str | None
    confidence: Decimal
    reason: str
