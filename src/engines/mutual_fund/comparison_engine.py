"""Fund comparison logic."""

from __future__ import annotations

from src.engines.mutual_fund.models import FundAnalysis, FundComparison


def compare_funds(analyses: list[FundAnalysis]) -> FundComparison:
    """Build a side-by-side comparison from analyzed funds."""
    return FundComparison(funds=list(analyses))
