"""Market alert generation."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from src.domain.enums import AlertSeverity
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.engines.market_intelligence.models import MarketAlert

INFLATION_SURPRISE_THRESHOLD = Decimal("1")
RATE_CHANGE_THRESHOLD = Decimal("0.5")
FX_MOVE_THRESHOLD = Decimal("2")


def generate_alerts(indicators: list[MacroIndicatorPoint]) -> list[MarketAlert]:
    """Generate alerts from macro indicator changes."""
    alerts: list[MarketAlert] = []
    now = datetime.now(UTC)

    for indicator in indicators:
        alerts.extend(_macro_alerts(indicator, now))

    return alerts


def _macro_alerts(
    indicator: MacroIndicatorPoint,
    detected_at: datetime,
) -> list[MarketAlert]:
    alerts: list[MarketAlert] = []
    name = indicator.indicator_name.lower()

    if (
        indicator.forecast_value is not None
        and abs(indicator.actual_value - indicator.forecast_value)
        >= INFLATION_SURPRISE_THRESHOLD
        and "inflation" in name
    ):
        alerts.append(
            MarketAlert(
                alert_type="inflation_surprise",
                severity=AlertSeverity.HIGH,
                message=(
                    f"{indicator.indicator_name} came in at "
                    f"{indicator.actual_value} vs forecast "
                    f"{indicator.forecast_value}."
                ),
                detected_at=detected_at,
            )
        )

    if (
        indicator.previous_value is not None
        and abs(indicator.actual_value - indicator.previous_value)
        >= RATE_CHANGE_THRESHOLD
        and ("rate" in name or "policy" in name)
    ):
        alerts.append(
            MarketAlert(
                alert_type="interest_rate_change",
                severity=AlertSeverity.MEDIUM,
                message=(
                    f"{indicator.indicator_name} moved from "
                    f"{indicator.previous_value} to {indicator.actual_value}."
                ),
                detected_at=detected_at,
            )
        )

    if (
        indicator.previous_value is not None
        and indicator.previous_value > Decimal("0")
        and abs(
            (indicator.actual_value - indicator.previous_value)
            / indicator.previous_value
            * Decimal("100")
        )
        >= FX_MOVE_THRESHOLD
        and ("usd" in name or "exchange" in name)
    ):
        alerts.append(
            MarketAlert(
                alert_type="currency_movement",
                severity=AlertSeverity.MEDIUM,
                message=(
                    f"{indicator.indicator_name} moved significantly to "
                    f"{indicator.actual_value}."
                ),
                detected_at=detected_at,
            )
        )

    return alerts
