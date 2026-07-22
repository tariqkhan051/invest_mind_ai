"""Macro indicator read model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MacroIndicatorPoint:
    """Single macroeconomic indicator observation."""

    indicator_name: str
    release_date: date
    actual_value: Decimal
    country: str = "PK"
    forecast_value: Decimal | None = None
    previous_value: Decimal | None = None
    unit: str | None = None
    trend: str | None = None
    source: str | None = None
