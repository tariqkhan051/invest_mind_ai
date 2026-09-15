"""Parse live SBP homepage and World Bank inflation payloads."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

_POLICY_RATE_RE = re.compile(
    r"SBP\s+Policy\s+Rate.*?([0-9]+(?:\.[0-9]+)?)\s*%",
    re.IGNORECASE | re.DOTALL,
)
_USD_PKR_RE = re.compile(
    r"M2M\s+Revaluation\s+Rate.*?([0-9]{2,3}(?:\.[0-9]+)?)",
    re.IGNORECASE | re.DOTALL,
)
_USD_DATE_RE = re.compile(
    r"USD/\s*PKR\s+Rates.*?As on\s+([0-9]{1,2}\s*-\s*[A-Za-z]{3,9}\s*-\s*[0-9]{2,4})",
    re.IGNORECASE | re.DOTALL,
)


def parse_sbp_homepage(html: str, today: date | None = None) -> list[dict[str, Any]]:
    """Extract policy rate and USD/PKR from the SBP homepage HTML."""
    today = today or date.today()
    records: list[dict[str, Any]] = []

    policy_match = _POLICY_RATE_RE.search(html)
    if policy_match:
        records.append(
            {
                "indicator_name": "policy rate",
                "date": today.isoformat(),
                "value": policy_match.group(1),
                "unit": "percent",
                "frequency": "daily",
                "importance": "high",
                "source": "sbp",
            }
        )

    usd_match = _USD_PKR_RE.search(html)
    if usd_match:
        usd_date = _parse_sbp_date(_first_group(_USD_DATE_RE.search(html))) or today
        records.append(
            {
                "indicator_name": "usd pkr",
                "date": usd_date.isoformat(),
                "value": usd_match.group(1),
                "unit": "PKR",
                "frequency": "daily",
                "importance": "high",
                "source": "sbp",
            }
        )

    return records


def parse_world_bank_inflation(payload: Any) -> list[dict[str, Any]]:
    """Extract annual CPI inflation points from a World Bank API response."""
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else payload
    if not isinstance(rows, list):
        return []

    records: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        value = row.get("value")
        year = str(row.get("date", "")).strip()
        if value is None or not year.isdigit():
            continue
        records.append(
            {
                "indicator_name": "inflation cpi",
                "date": f"{year}-12-31",
                "value": value,
                "unit": "percent",
                "frequency": "annual",
                "importance": "high",
                "source": "world_bank",
            }
        )
    return records


def _first_group(match: re.Match[str] | None) -> str | None:
    if match is None:
        return None
    return match.group(1)


def _parse_sbp_date(value: str | None) -> date | None:
    if not value:
        return None
    text = re.sub(r"\s+", "", value).replace("--", "-")
    for fmt in ("%d-%b-%Y", "%d-%b-%y", "%d-%B-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
