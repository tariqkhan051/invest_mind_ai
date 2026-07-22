"""Mutual fund engine orchestration."""

from __future__ import annotations

from datetime import date

from src.domain.entities.mutual_fund import MutualFund
from src.domain.read_models.nav_history import NavHistoryPoint
from src.engines.mutual_fund.comparison_engine import compare_funds
from src.engines.mutual_fund.models import (
    FundAnalysis,
    FundComparison,
    FundRanking,
    SwitchOpportunity,
)
from src.engines.mutual_fund.performance_calculator import calculate_performance
from src.engines.mutual_fund.ranking_engine import rank_funds
from src.engines.mutual_fund.risk_calculator import calculate_risk
from src.engines.mutual_fund.scoring_engine import calculate_ai_score
from src.engines.mutual_fund.switch_analyzer import find_switch_opportunities


class MutualFundEngine:
    """Analyze mutual funds from NAV history and metadata."""

    def analyze_fund(
        self,
        mutual_fund: MutualFund,
        history: list[NavHistoryPoint],
        as_of: date | None = None,
    ) -> FundAnalysis:
        """Produce a complete analysis for one fund."""
        performance = calculate_performance(history, as_of=as_of)
        risk = calculate_risk(history)
        latest = history[-1] if history else None

        analysis = FundAnalysis(
            asset_id=mutual_fund.asset_id,
            symbol=mutual_fund.asset.symbol,
            display_name=mutual_fund.asset.display_name,
            asset_type=mutual_fund.asset.asset_type.value,
            is_shariah=mutual_fund.asset.is_shariah,
            management_company=mutual_fund.management_company,
            expense_ratio=mutual_fund.expense_ratio,
            aum=mutual_fund.aum,
            latest_nav=latest.nav if latest else None,
            latest_nav_date=latest.nav_date if latest else None,
            performance=performance,
            risk=risk,
        )
        analysis.ai_score = calculate_ai_score(
            performance,
            risk,
            mutual_fund.aum,
            mutual_fund.expense_ratio,
        )
        return analysis

    def rank_funds(
        self,
        analyses: list[FundAnalysis],
        limit: int | None = None,
    ) -> list[FundRanking]:
        """Rank analyzed funds."""
        return rank_funds(analyses, limit=limit)

    def compare_funds(self, analyses: list[FundAnalysis]) -> FundComparison:
        """Compare multiple analyzed funds."""
        return compare_funds(analyses)

    def find_switch_opportunities(
        self,
        analyses: list[FundAnalysis],
    ) -> list[SwitchOpportunity]:
        """Detect switch opportunities across analyzed funds."""
        return find_switch_opportunities(analyses)

    def group_by_category(
        self,
        analyses: list[FundAnalysis],
    ) -> dict[str, list[FundAnalysis]]:
        """Group fund analyses by asset type (category proxy)."""
        grouped: dict[str, list[FundAnalysis]] = {}
        for analysis in analyses:
            grouped.setdefault(analysis.asset_type, []).append(analysis)
        return grouped

    def filter_analyses(
        self,
        analyses: list[FundAnalysis],
        shariah_only: bool = False,
        category: str | None = None,
    ) -> list[FundAnalysis]:
        """Filter analyses by Shariah status and category."""
        filtered = analyses
        if shariah_only:
            filtered = [item for item in filtered if item.is_shariah]
        if category:
            filtered = [item for item in filtered if item.asset_type == category]
        return filtered
