"""Fund ranking logic."""

from __future__ import annotations

from src.engines.mutual_fund.models import FundAnalysis, FundRanking
from src.engines.mutual_fund.scoring_engine import rank_score


def rank_funds(
    analyses: list[FundAnalysis],
    limit: int | None = None,
) -> list[FundRanking]:
    """Rank funds by AI score (fallback: yearly return)."""
    sorted_analyses = sorted(analyses, key=rank_score, reverse=True)
    if limit is not None:
        sorted_analyses = sorted_analyses[:limit]

    rankings: list[FundRanking] = []
    for index, analysis in enumerate(sorted_analyses, start=1):
        rankings.append(
            FundRanking(
                rank=index,
                asset_id=analysis.asset_id,
                symbol=analysis.symbol,
                display_name=analysis.display_name,
                ai_score=analysis.ai_score,
                yearly_return=analysis.performance.yearly_return,
                volatility=analysis.risk.volatility,
            )
        )
    return rankings
