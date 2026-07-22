"""Generate realistic sample market-data import files for local collectors."""

from __future__ import annotations

import json
import math
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any


def _decimal_str(value: float) -> str:
    return f"{Decimal(str(round(value, 4))):f}"


def _trading_days(end: date, count: int) -> list[date]:
    days: list[date] = []
    cursor = end
    while len(days) < count:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor -= timedelta(days=1)
    days.reverse()
    return days


def _series(
    start_price: float,
    days: list[date],
    annual_return: float,
    volatility: float,
    seed: int,
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    price = start_price
    daily_drift = annual_return / 252
    for index, day in enumerate(days):
        shock = math.sin((index + seed) / 7.0) * volatility
        price = max(price * (1 + daily_drift + shock), 1.0)
        records.append(
            {
                "date": day.isoformat(),
                "value": _decimal_str(price),
            }
        )
    return records


def build_nav_payload(days: list[date]) -> dict[str, Any]:
    """Build MUFAP-compatible NAV payload."""
    funds = [
        ("MIF", 95.0, 0.14, 0.004, 1),
        ("MEF", 78.0, 0.18, 0.006, 3),
        ("AMMF", 52.0, 0.11, 0.003, 5),
    ]
    records: list[dict[str, str]] = []
    for symbol, start, annual, vol, seed in funds:
        for point in _series(start, days, annual, vol, seed):
            records.append(
                {
                    "symbol": symbol,
                    "date": point["date"],
                    "nav": point["value"],
                }
            )
    return {"records": records}


def build_price_payload(days: list[date]) -> dict[str, Any]:
    """Build PSX-compatible price payload."""
    stocks = [
        ("ENGRO", 320.0, 0.12, 0.008, 2),
        ("MARI", 2450.0, 0.16, 0.01, 4),
        ("MEBL", 210.0, 0.10, 0.007, 6),
    ]
    records: list[dict[str, str]] = []
    for symbol, start, annual, vol, seed in stocks:
        for point in _series(start, days, annual, vol, seed):
            close = float(point["value"])
            records.append(
                {
                    "symbol": symbol,
                    "date": point["date"],
                    "open": _decimal_str(close * 0.995),
                    "high": _decimal_str(close * 1.01),
                    "low": _decimal_str(close * 0.99),
                    "close": _decimal_str(close),
                    "volume": "1000000",
                }
            )
    return {"records": records}


def build_macro_payload(end: date) -> dict[str, Any]:
    """Build SBP-compatible macro indicator payload."""
    months = [end.replace(day=1) - timedelta(days=30 * offset) for offset in range(11, -1, -1)]
    records: list[dict[str, Any]] = []
    for index, month in enumerate(months):
        release = month.replace(day=min(28, month.day))
        records.extend(
            [
                {
                    "indicator_name": "policy rate",
                    "date": release.isoformat(),
                    "value": _decimal_str(15.0 - index * 0.25),
                    "unit": "percent",
                    "frequency": "monthly",
                    "importance": "high",
                },
                {
                    "indicator_name": "inflation cpi",
                    "date": release.isoformat(),
                    "value": _decimal_str(20.0 - index * 0.4),
                    "unit": "percent",
                    "frequency": "monthly",
                    "importance": "high",
                },
                {
                    "indicator_name": "usd pkr",
                    "date": release.isoformat(),
                    "value": _decimal_str(278.0 + index * 0.5),
                    "unit": "PKR",
                    "frequency": "monthly",
                    "importance": "high",
                },
            ]
        )
    return {"records": records}


def write_sample_imports(imports_dir: Path, trading_days: int = 180) -> dict[str, Path]:
    """Generate local collector import files and return their paths."""
    imports_dir.mkdir(parents=True, exist_ok=True)
    end = date.today()
    days = _trading_days(end, trading_days)

    paths = {
        "mufap": imports_dir / "mufap_nav.json",
        "psx": imports_dir / "psx_prices.json",
        "sbp": imports_dir / "sbp_macro.json",
    }
    paths["mufap"].write_text(json.dumps(build_nav_payload(days), indent=2), encoding="utf-8")
    paths["psx"].write_text(json.dumps(build_price_payload(days), indent=2), encoding="utf-8")
    paths["sbp"].write_text(json.dumps(build_macro_payload(end), indent=2), encoding="utf-8")
    return paths
