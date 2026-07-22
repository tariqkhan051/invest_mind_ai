"""Switch opportunity detection."""

from __future__ import annotations

from decimal import Decimal

from src.engines.mutual_fund.models import FundAnalysis, SwitchOpportunity

MIN_RETURN_GAP = Decimal("3")
MAX_VOLATILITY_GAP = Decimal("5")


def find_switch_opportunities(
    analyses: list[FundAnalysis],
) -> list[SwitchOpportunity]:
    """Identify funds that may benefit from switching to a better peer."""
    opportunities: list[SwitchOpportunity] = []
    by_category: dict[str, list[FundAnalysis]] = {}
    for analysis in analyses:
        by_category.setdefault(analysis.asset_type, []).append(analysis)

    for category_analyses in by_category.values():
        if len(category_analyses) < 2:
            continue
        ranked = sorted(
            category_analyses,
            key=lambda item: item.performance.yearly_return or Decimal("-999"),
            reverse=True,
        )
        best = ranked[0]
        best_return = best.performance.yearly_return
        best_volatility = best.risk.volatility
        if best_return is None:
            continue

        for candidate in ranked[1:]:
            candidate_return = candidate.performance.yearly_return
            if candidate_return is None:
                continue
            return_gap = best_return - candidate_return
            if return_gap < MIN_RETURN_GAP:
                continue

            volatility_ok = True
            if best_volatility is not None and candidate.risk.volatility is not None:
                volatility_ok = (
                    candidate.risk.volatility - best_volatility
                ) <= MAX_VOLATILITY_GAP
            if not volatility_ok:
                continue

            opportunities.append(
                SwitchOpportunity(
                    from_asset_id=candidate.asset_id,
                    from_symbol=candidate.symbol,
                    to_asset_id=best.asset_id,
                    to_symbol=best.symbol,
                    expected_benefit_pct=return_gap,
                    reason=(
                        f"{best.symbol} outperformed {candidate.symbol} by "
                        f"{return_gap:.2f}% over the past year in "
                        f"{category_analyses[0].asset_type}."
                    ),
                    confidence=_confidence(return_gap),
                )
            )
    return opportunities


def _confidence(return_gap: Decimal) -> Decimal:
    if return_gap >= Decimal("10"):
        return Decimal("0.9")
    if return_gap >= Decimal("5"):
        return Decimal("0.75")
    return Decimal("0.6")
