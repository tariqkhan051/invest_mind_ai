"""Buy opportunity detection."""

from __future__ import annotations

from decimal import Decimal

from src.engines.stock.models import BuyOpportunity, StockAnalysis


def find_buy_opportunities(analyses: list[StockAnalysis]) -> list[BuyOpportunity]:
    """Detect potential buy opportunities across analyzed stocks."""
    opportunities: list[BuyOpportunity] = []
    for analysis in analyses:
        opportunities.extend(_detect_for_stock(analysis))
    return opportunities


def _detect_for_stock(analysis: StockAnalysis) -> list[BuyOpportunity]:
    results: list[BuyOpportunity] = []
    technicals = analysis.technicals
    fundamentals = analysis.fundamentals
    performance = analysis.performance

    if technicals.rsi_14 is not None and technicals.rsi_14 < Decimal("35"):
        results.append(
            BuyOpportunity(
                asset_id=analysis.asset_id,
                symbol=analysis.symbol,
                opportunity_type="oversold",
                reason=(
                    f"{analysis.symbol} RSI is {technicals.rsi_14:.1f}, "
                    "indicating oversold conditions."
                ),
                confidence=Decimal("0.7"),
                expected_return_pct=performance.monthly_return,
                risk_level="moderate",
            )
        )

    if (
        technicals.sma_20 is not None
        and technicals.sma_50 is not None
        and analysis.latest_price is not None
        and analysis.latest_price > technicals.sma_20 > technicals.sma_50
    ):
        results.append(
            BuyOpportunity(
                asset_id=analysis.asset_id,
                symbol=analysis.symbol,
                opportunity_type="breakout",
                reason=(
                    f"{analysis.symbol} price is above rising "
                    "20/50-day moving averages."
                ),
                confidence=Decimal("0.75"),
                expected_return_pct=performance.yearly_return,
                risk_level="moderate",
            )
        )

    if fundamentals.pe is not None and fundamentals.pe < Decimal("10"):
        results.append(
            BuyOpportunity(
                asset_id=analysis.asset_id,
                symbol=analysis.symbol,
                opportunity_type="undervalued",
                reason=(
                    f"{analysis.symbol} trades at a low P/E of "
                    f"{fundamentals.pe:.1f}."
                ),
                confidence=Decimal("0.65"),
                expected_return_pct=performance.yearly_return,
                risk_level="low",
            )
        )

    if (
        technicals.momentum is not None
        and technicals.momentum > Decimal("8")
        and performance.yearly_return is not None
        and performance.yearly_return > Decimal("15")
    ):
        results.append(
            BuyOpportunity(
                asset_id=analysis.asset_id,
                symbol=analysis.symbol,
                opportunity_type="momentum",
                reason=(
                    f"{analysis.symbol} shows strong price momentum "
                    "and annual returns."
                ),
                confidence=Decimal("0.8"),
                expected_return_pct=performance.yearly_return,
                risk_level="high",
            )
        )

    return results
