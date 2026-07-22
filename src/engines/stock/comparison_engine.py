"""Stock comparison logic."""

from __future__ import annotations

from src.engines.stock.models import StockAnalysis, StockComparison


def compare_stocks(analyses: list[StockAnalysis]) -> StockComparison:
    """Build a side-by-side comparison from analyzed stocks."""
    return StockComparison(stocks=list(analyses))
