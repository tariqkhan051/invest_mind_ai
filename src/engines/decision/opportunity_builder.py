"""Build opportunity candidates from engine outputs."""

from __future__ import annotations

from decimal import Decimal

from src.domain.enums import MarketRegime, RecommendationType, RiskLevel
from src.engines.decision.models import DecisionContext, OpportunityCandidate


def build_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    """Build scored opportunity candidates from decision context."""
    candidates: list[OpportunityCandidate] = []

    candidates.extend(_risk_candidates(context))
    candidates.extend(_switch_candidates(context))
    candidates.extend(_fund_invest_candidates(context))
    candidates.extend(_stock_buy_candidates(context))
    candidates.extend(_cash_candidates(context))

    if not candidates:
        candidates.append(_no_action_candidate(context))

    return candidates


def _risk_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    allocation = context.portfolio.allocation
    cash_pct = allocation.cash_percentage or Decimal("0")
    if cash_pct < Decimal("5") and context.market.regime.regime in {
        MarketRegime.BEAR,
        MarketRegime.STRONG_BEAR,
        MarketRegime.VOLATILE,
    }:
        return [
            OpportunityCandidate(
                recommendation_type=RecommendationType.HOLD_CASH,
                score=Decimal("72"),
                priority=100,
                reason=(
                    "Bearish or volatile market regime suggests preserving liquidity."
                ),
                expected_risk=RiskLevel.LOW,
                evidence={
                    "regime": context.market.regime.regime.value,
                    "cash_allocation_pct": str(cash_pct),
                },
            )
        ]
    return []


def _switch_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    results: list[OpportunityCandidate] = []
    for opportunity in context.switch_opportunities[:3]:
        score = opportunity.confidence * Decimal("100")
        results.append(
            OpportunityCandidate(
                recommendation_type=RecommendationType.SWITCH,
                score=score,
                priority=80,
                reason=opportunity.reason,
                from_asset_id=opportunity.from_asset_id,
                to_asset_id=opportunity.to_asset_id,
                from_symbol=opportunity.from_symbol,
                to_symbol=opportunity.to_symbol,
                expected_return=opportunity.expected_benefit_pct,
                expected_risk=RiskLevel.MODERATE,
                evidence={
                    "from_symbol": opportunity.from_symbol,
                    "to_symbol": opportunity.to_symbol,
                    "expected_benefit_pct": str(opportunity.expected_benefit_pct),
                },
            )
        )
    return results


def _fund_invest_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    if context.market.regime.regime in {
        MarketRegime.BEAR,
        MarketRegime.STRONG_BEAR,
        MarketRegime.HIGH_INTEREST_RATE,
    }:
        return []

    ranked = sorted(
        context.funds,
        key=lambda fund: fund.ai_score or Decimal("0"),
        reverse=True,
    )
    if not ranked:
        return []

    top = ranked[0]
    if top.ai_score is None:
        return []

    return [
        OpportunityCandidate(
            recommendation_type=RecommendationType.INVEST,
            score=top.ai_score,
            priority=70,
            reason=(
                f"{top.symbol} ranks highest among analyzed funds with strong "
                "risk-adjusted performance."
            ),
            asset_id=top.asset_id,
            symbol=top.symbol,
            recommended_amount=context.monthly_investment,
            expected_return=top.performance.yearly_return,
            expected_risk=RiskLevel.MODERATE,
            evidence={
                "symbol": top.symbol,
                "ai_score": str(top.ai_score),
                "regime": context.market.regime.regime.value,
            },
        )
    ]


def _stock_buy_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    if context.market.regime.regime in {
        MarketRegime.BEAR,
        MarketRegime.STRONG_BEAR,
    }:
        return []

    results: list[OpportunityCandidate] = []
    for opportunity in context.buy_opportunities[:2]:
        stock = next(
            (item for item in context.stocks if item.symbol == opportunity.symbol),
            None,
        )
        score = opportunity.confidence * Decimal("100")
        results.append(
            OpportunityCandidate(
                recommendation_type=RecommendationType.BUY,
                score=score,
                priority=60,
                reason=opportunity.reason,
                asset_id=opportunity.asset_id,
                symbol=opportunity.symbol,
                expected_return=opportunity.expected_return_pct,
                expected_risk=RiskLevel(opportunity.risk_level),
                evidence={
                    "symbol": opportunity.symbol,
                    "opportunity_type": opportunity.opportunity_type,
                    "pe": (
                        str(stock.fundamentals.pe)
                        if stock and stock.fundamentals.pe
                        else ""
                    ),
                },
            )
        )
    return results


def _cash_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    for signal in context.market.signals:
        if signal.signal_type.value == "increase_money_market":
            return [
                OpportunityCandidate(
                    recommendation_type=RecommendationType.CONTINUE_SIP,
                    score=Decimal("65"),
                    priority=75,
                    reason=signal.message,
                    expected_risk=RiskLevel.LOW,
                    evidence={"signal": signal.signal_type.value},
                )
            ]
    return []


def _no_action_candidate(context: DecisionContext) -> OpportunityCandidate:
    return OpportunityCandidate(
        recommendation_type=RecommendationType.NO_ACTION,
        score=Decimal("55"),
        priority=10,
        reason="No high-conviction opportunities identified for today.",
        expected_risk=RiskLevel.LOW,
        evidence={
            "regime": context.market.regime.regime.value,
            "market_score": str(context.market.score.overall_score),
        },
    )
