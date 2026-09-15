"""Technical indicator calculations."""

from __future__ import annotations

from decimal import Decimal

from src.domain.read_models.price_history import PriceHistoryPoint
from src.engines.stock.models import TechnicalIndicators


def calculate_technicals(history: list[PriceHistoryPoint]) -> TechnicalIndicators:
    """Calculate technical indicators from price history."""
    if len(history) < 2:
        return TechnicalIndicators()

    sorted_history = sorted(history, key=lambda point: point.price_date)
    closes = [point.close_price for point in sorted_history]
    volumes = [point.volume for point in sorted_history if point.volume is not None]

    return TechnicalIndicators(
        sma_20=_sma(closes, 20),
        sma_50=_sma(closes, 50),
        ema_12=_ema(closes, 12),
        rsi_14=_rsi(closes, 14),
        momentum=_momentum(closes, 10),
        volume_trend=_volume_trend(volumes),
    )


def _sma(values: list[Decimal], period: int) -> Decimal | None:
    if len(values) < period:
        return None
    window = values[-period:]
    return sum(window, Decimal("0")) / Decimal(period)


def _ema(values: list[Decimal], period: int) -> Decimal | None:
    if len(values) < period:
        return None
    multiplier = Decimal("2") / Decimal(period + 1)
    ema = sum(values[:period], Decimal("0")) / Decimal(period)
    for value in values[period:]:
        ema = (value - ema) * multiplier + ema
    return ema


def _rsi(values: list[Decimal], period: int) -> Decimal | None:
    if len(values) <= period:
        return None
    gains: list[Decimal] = []
    losses: list[Decimal] = []
    for index in range(1, len(values)):
        change = values[index] - values[index - 1]
        if change >= Decimal("0"):
            gains.append(change)
            losses.append(Decimal("0"))
        else:
            gains.append(Decimal("0"))
            losses.append(abs(change))
    if len(gains) < period:
        return None
    avg_gain = sum(gains[-period:], Decimal("0")) / Decimal(period)
    avg_loss = sum(losses[-period:], Decimal("0")) / Decimal(period)
    if avg_loss == Decimal("0"):
        return Decimal("100")
    relative_strength = avg_gain / avg_loss
    return Decimal("100") - (Decimal("100") / (Decimal("1") + relative_strength))


def _momentum(values: list[Decimal], period: int) -> Decimal | None:
    if len(values) <= period:
        return None
    start = values[-period - 1]
    end = values[-1]
    if start <= Decimal("0"):
        return None
    return ((end / start) - Decimal("1")) * Decimal("100")


def _volume_trend(volumes: list[Decimal]) -> Decimal | None:
    if len(volumes) < 20:
        return None
    recent = sum(volumes[-5:], Decimal("0")) / Decimal("5")
    prior = sum(volumes[-20:-5], Decimal("0")) / Decimal("15")
    if prior <= Decimal("0"):
        return None
    return ((recent / prior) - Decimal("1")) * Decimal("100")
