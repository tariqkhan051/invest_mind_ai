"""Build opportunity candidates from engine outputs."""

from __future__ import annotations

from decimal import Decimal

from src.domain.enums import AssetType, MarketRegime, RecommendationType, RiskLevel
from src.engines.decision.models import DecisionContext, OpportunityCandidate
from src.engines.mutual_fund.models import FundAnalysis

_DEFENSIVE_REGIMES = {
    MarketRegime.BEAR,
    MarketRegime.STRONG_BEAR,
    MarketRegime.VOLATILE,
    MarketRegime.HIGH_INTEREST_RATE,
    MarketRegime.HIGH_INFLATION,
}

_MONEY_MARKET_TYPES = {
    AssetType.MONEY_MARKET_FUND.value,
    AssetType.CASH_MANAGEMENT_FUND.value,
    AssetType.INCOME_FUND.value,
}


def build_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    """Build scored opportunity candidates from decision context."""
    candidates: list[OpportunityCandidate] = []

    candidates.extend(_risk_candidates(context))
    candidates.extend(_deploy_cash_candidates(context))
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


def _deploy_cash_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    """Turn idle cash into a concrete fund action for today."""
    cash = context.portfolio.valuation.cash_balance or Decimal("0")
    cash_pct = context.portfolio.allocation.cash_percentage or Decimal("0")
    if cash < Decimal("25000") or cash_pct < Decimal("15"):
        return []

    defensive = context.market.regime.regime in _DEFENSIVE_REGIMES
    target = _pick_fund(
        context.funds,
        prefer_money_market=defensive,
    )
    if target is None:
        return []

    deploy_pct = Decimal("0.40") if defensive else Decimal("0.30")
    amount = (cash * deploy_pct).quantize(Decimal("1"))
    if amount <= 0:
        return []

    as_of = (
        target.latest_nav_date.isoformat() if target.latest_nav_date else "unknown"
    )
    category = target.asset_type.replace("_", " ")
    action = "Park idle cash" if defensive else "Deploy idle cash"
    reason = (
        f"{action}: move PKR {amount:,.0f} into {target.symbol} ({category}). "
        f"Data as of {as_of}."
    )
    if target.performance.yearly_return is not None:
        reason += f" FYTD/annual signal {target.performance.yearly_return}%."

    evidence = {
        "symbol": target.symbol,
        "as_of_date": as_of,
        "cash_pkr": str(cash),
        "cash_allocation_pct": str(cash_pct),
        "regime": context.market.regime.regime.value,
        "latest_nav": str(target.latest_nav or ""),
        "category": target.asset_type,
    }
    return [
        OpportunityCandidate(
            recommendation_type=RecommendationType.INVEST,
            score=max(target.ai_score or Decimal("60"), Decimal("68")),
            priority=95,
            reason=reason,
            asset_id=target.asset_id,
            symbol=target.symbol,
            recommended_amount=amount,
            expected_return=target.performance.yearly_return,
            expected_risk=RiskLevel.LOW if defensive else RiskLevel.MODERATE,
            evidence=evidence,
        )
    ]


def _switch_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    results: list[OpportunityCandidate] = []
    total_value = context.portfolio.valuation.total_value or Decimal("0")
    for opportunity in context.switch_opportunities[:3]:
        score = opportunity.confidence * Decimal("100")
        from_pct = context.portfolio.allocation.by_holding.get(
            str(opportunity.from_asset_id),
            Decimal("0"),
        )
        holding_value = (total_value * from_pct / Decimal("100")).quantize(Decimal("1"))
        # Move a meaningful slice of the weaker holding, not the entire position.
        amount = (holding_value * Decimal("0.25")).quantize(Decimal("1"))
        if amount <= 0:
            amount = min(context.monthly_investment, holding_value or context.monthly_investment)

        reason = (
            f"Move PKR {amount:,.0f} from {opportunity.from_symbol} "
            f"to {opportunity.to_symbol}. {opportunity.reason}"
        )
        results.append(
            OpportunityCandidate(
                recommendation_type=RecommendationType.SWITCH,
                score=score,
                priority=80,
                reason=reason,
                from_asset_id=opportunity.from_asset_id,
                to_asset_id=opportunity.to_asset_id,
                from_symbol=opportunity.from_symbol,
                to_symbol=opportunity.to_symbol,
                recommended_amount=amount,
                expected_return=opportunity.expected_benefit_pct,
                expected_risk=RiskLevel.MODERATE,
                evidence={
                    "from_symbol": opportunity.from_symbol,
                    "to_symbol": opportunity.to_symbol,
                    "expected_benefit_pct": str(opportunity.expected_benefit_pct),
                    "recommended_amount": str(amount),
                    "holding_value_pkr": str(holding_value),
                },
            )
        )
    return results


def _fund_invest_candidates(context: DecisionContext) -> list[OpportunityCandidate]:
    # Idle-cash deployment already covers the main fund action in defensive regimes.
    if context.market.regime.regime in _DEFENSIVE_REGIMES:
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

    as_of = top.latest_nav_date.isoformat() if top.latest_nav_date else "unknown"
    amount = context.monthly_investment
    return [
        OpportunityCandidate(
            recommendation_type=RecommendationType.INVEST,
            score=top.ai_score,
            priority=70,
            reason=(
                f"Invest PKR {amount:,.0f} into {top.symbol}. "
                f"It ranks highest among analyzed funds (as of {as_of})."
            ),
            asset_id=top.asset_id,
            symbol=top.symbol,
            recommended_amount=amount,
            expected_return=top.performance.yearly_return,
            expected_risk=RiskLevel.MODERATE,
            evidence={
                "symbol": top.symbol,
                "ai_score": str(top.ai_score),
                "regime": context.market.regime.regime.value,
                "as_of_date": as_of,
                "latest_nav": str(top.latest_nav or ""),
                "recommended_amount": str(amount),
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
        amount = context.monthly_investment
        latest_price = stock.latest_price if stock else None
        reason = (
            f"Buy PKR {amount:,.0f} of {opportunity.symbol}. {opportunity.reason}"
        )
        results.append(
            OpportunityCandidate(
                recommendation_type=RecommendationType.BUY,
                score=score,
                priority=60,
                reason=reason,
                asset_id=opportunity.asset_id,
                symbol=opportunity.symbol,
                recommended_amount=amount,
                expected_return=opportunity.expected_return_pct,
                expected_risk=RiskLevel(opportunity.risk_level),
                evidence={
                    "symbol": opportunity.symbol,
                    "opportunity_type": opportunity.opportunity_type,
                    "recommended_amount": str(amount),
                    "latest_price": str(latest_price or ""),
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


def _pick_fund(
    funds: list[FundAnalysis],
    *,
    prefer_money_market: bool,
) -> FundAnalysis | None:
    if not funds:
        return None

    def rank_key(fund: FundAnalysis) -> tuple[Decimal, Decimal]:
        fytd = fund.performance.yearly_return or Decimal("0")
        score = fund.ai_score or Decimal("0")
        return (score, fytd)

    if prefer_money_market:
        money_market = [
            fund for fund in funds if fund.asset_type in _MONEY_MARKET_TYPES
        ]
        if money_market:
            return max(money_market, key=rank_key)
    equity_like = [
        fund
        for fund in funds
        if fund.asset_type
        in {
            AssetType.EQUITY_FUND.value,
            AssetType.BALANCED_FUND.value,
            AssetType.MUTUAL_FUND.value,
        }
    ]
    pool = equity_like or funds
    return max(pool, key=rank_key)
