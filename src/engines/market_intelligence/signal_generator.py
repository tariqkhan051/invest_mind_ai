"""Investment signal generation."""

from __future__ import annotations

from decimal import Decimal

from src.domain.enums import InvestmentSignalType, MarketRegime
from src.engines.market_intelligence.models import InvestmentSignal, RegimeAssessment


def generate_signals(regime: RegimeAssessment) -> list[InvestmentSignal]:
    """Generate investment signals from the detected market regime."""
    mapping: dict[MarketRegime, list[tuple[InvestmentSignalType, str, Decimal]]] = {
        MarketRegime.STRONG_BULL: [
            (
                InvestmentSignalType.INCREASE_EQUITY,
                "Strong bullish sentiment supports higher equity exposure.",
                Decimal("0.8"),
            ),
            (
                InvestmentSignalType.FAVOR_GROWTH,
                "Favor growth-oriented sectors in a strong bull regime.",
                Decimal("0.75"),
            ),
        ],
        MarketRegime.BULL: [
            (
                InvestmentSignalType.INCREASE_EQUITY,
                "Positive environment supports moderate equity allocation increases.",
                Decimal("0.7"),
            ),
        ],
        MarketRegime.BEAR: [
            (
                InvestmentSignalType.REDUCE_RISK,
                "Bearish sentiment suggests reducing portfolio risk.",
                Decimal("0.75"),
            ),
            (
                InvestmentSignalType.INCREASE_MONEY_MARKET,
                "Increase money market allocation for capital preservation.",
                Decimal("0.7"),
            ),
        ],
        MarketRegime.STRONG_BEAR: [
            (
                InvestmentSignalType.HOLD_CASH,
                "Strong bear regime favors holding elevated cash reserves.",
                Decimal("0.85"),
            ),
            (
                InvestmentSignalType.REDUCE_RISK,
                "Reduce risk exposure until sentiment stabilizes.",
                Decimal("0.8"),
            ),
        ],
        MarketRegime.HIGH_INFLATION: [
            (
                InvestmentSignalType.INCREASE_INCOME_FUND,
                "High inflation favors income-oriented fund allocation.",
                Decimal("0.75"),
            ),
            (
                InvestmentSignalType.FAVOR_DEFENSIVE,
                "Favor defensive sectors during elevated inflation.",
                Decimal("0.7"),
            ),
        ],
        MarketRegime.HIGH_INTEREST_RATE: [
            (
                InvestmentSignalType.INCREASE_MONEY_MARKET,
                "High interest rates improve money market fund attractiveness.",
                Decimal("0.8"),
            ),
            (
                InvestmentSignalType.FAVOR_DEFENSIVE,
                "Defensive positioning recommended in a high-rate environment.",
                Decimal("0.65"),
            ),
        ],
        MarketRegime.RECOVERY: [
            (
                InvestmentSignalType.INCREASE_EQUITY,
                "Recovery phase supports gradual equity accumulation.",
                Decimal("0.65"),
            ),
        ],
        MarketRegime.VOLATILE: [
            (
                InvestmentSignalType.HOLD_CASH,
                "Elevated volatility suggests maintaining liquidity buffers.",
                Decimal("0.7"),
            ),
            (
                InvestmentSignalType.REDUCE_RISK,
                "Reduce risk until volatility subsides.",
                Decimal("0.65"),
            ),
        ],
        MarketRegime.NEUTRAL: [
            (
                InvestmentSignalType.FAVOR_GROWTH,
                "Neutral regime supports balanced growth positioning.",
                Decimal("0.55"),
            ),
        ],
    }

    signals: list[InvestmentSignal] = []
    for signal_type, message, confidence in mapping.get(regime.regime, []):
        signals.append(
            InvestmentSignal(
                signal_type=signal_type,
                message=message,
                confidence=confidence,
            )
        )
    return signals
