"""Stock ranking logic."""

from __future__ import annotations

from src.engines.stock.models import StockAnalysis, StockRanking
from src.engines.stock.scoring_engine import rank_score


def rank_stocks(
    analyses: list[StockAnalysis],
    limit: int | None = None,
) -> list[StockRanking]:
    """Rank stocks by AI score (fallback: yearly return)."""
    sorted_analyses = sorted(analyses, key=rank_score, reverse=True)
    if limit is not None:
        sorted_analyses = sorted_analyses[:limit]

    rankings: list[StockRanking] = []
    for index, analysis in enumerate(sorted_analyses, start=1):
        rankings.append(
            StockRanking(
                rank=index,
                asset_id=analysis.asset_id,
                symbol=analysis.symbol,
                display_name=analysis.display_name,
                ai_score=analysis.ai_score,
                yearly_return=analysis.performance.yearly_return,
                rsi_14=analysis.technicals.rsi_14,
            )
        )
    return rankings
