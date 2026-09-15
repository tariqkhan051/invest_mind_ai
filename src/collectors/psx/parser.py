"""Parse live PSX Data Portal timeseries payloads."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def parse_psx_eod_series(
    symbol: str,
    payload: Any,
    history_days: int | None = None,
) -> list[dict[str, Any]]:
    """Convert PSX `/timeseries/eod/{symbol}` JSON into price rows."""
    rows = payload.get("data", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return []

    cutoff_ts: int | None = None
    if history_days is not None and history_days > 0:
        cutoff_ts = int(datetime.now(UTC).timestamp()) - history_days * 24 * 60 * 60

    records: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 2:
            continue
        try:
            timestamp = int(row[0])
            close_price = row[1]
        except (TypeError, ValueError):
            continue
        if cutoff_ts is not None and timestamp < cutoff_ts:
            continue
        price_date = datetime.fromtimestamp(timestamp, UTC).date().isoformat()
        records.append(
            {
                "symbol": symbol.upper(),
                "date": price_date,
                "close": close_price,
                "volume": row[2] if len(row) > 2 else None,
                "open": row[3] if len(row) > 3 else None,
            }
        )
    return records
