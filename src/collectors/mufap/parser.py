"""Parse live MUFAP NAV HTML tables."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from src.domain.enums import AssetType

_DATE_FORMATS = (
    "%b %d, %Y",
    "%B %d, %Y",
    "%d-%b-%Y",
    "%d %b %Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%d-%m-%Y",
)

_CATEGORY_TYPES: tuple[tuple[str, AssetType], ...] = (
    ("money market", AssetType.MONEY_MARKET_FUND),
    ("cash", AssetType.CASH_MANAGEMENT_FUND),
    ("equity", AssetType.EQUITY_FUND),
    ("income", AssetType.INCOME_FUND),
    ("balanced", AssetType.BALANCED_FUND),
    ("asset allocation", AssetType.BALANCED_FUND),
)


def parse_mufap_nav_html(html: str) -> list[dict[str, Any]]:
    """Extract NAV rows from a MUFAP IndustryStatDaily HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, Any]] = []
    for table in soup.find_all("table"):
        header_map = _header_map(table)
        if "fund" not in header_map or "nav" not in header_map:
            continue
        body_rows = table.find_all("tr")[1:]
        for row in body_rows:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) <= max(header_map.values()):
                continue
            fund_name = cells[header_map["fund"]]
            nav_text = cells[header_map["nav"]]
            if not fund_name or not nav_text:
                continue
            category = cells[header_map["category"]] if "category" in header_map else ""
            amc = cells[header_map["amc"]] if "amc" in header_map else ""
            validity = (
                cells[header_map["validity"]] if "validity" in header_map else ""
            )
            rows.append(
                {
                    "name": fund_name,
                    "amc": amc,
                    "category": category,
                    "nav": _clean_number(nav_text),
                    "date": _parse_date_text(validity),
                    "is_shariah": "shariah" in category.lower()
                    or "islamic" in fund_name.lower(),
                    "asset_type": _asset_type(category).value,
                }
            )
    return rows


def resolve_fund_symbol(
    fund_name: str,
    aliases: dict[str, list[str]],
    known_names: dict[str, str],
) -> str | None:
    """Map a MUFAP fund name to a known symbol using aliases or display names."""
    lowered = _normalize_name(fund_name)
    for symbol, names in aliases.items():
        for alias in names:
            if _names_match(lowered, _normalize_name(alias)):
                return symbol.upper()
    for symbol, display_name in known_names.items():
        if _names_match(lowered, _normalize_name(display_name)):
            return symbol.upper()
    return None


def parse_alias_config(raw_aliases: Any) -> dict[str, list[str]]:
    """Normalize YAML alias config into symbol -> name list."""
    if not isinstance(raw_aliases, dict):
        return {}
    parsed: dict[str, list[str]] = {}
    for symbol, value in raw_aliases.items():
        key = str(symbol).strip().upper()
        if isinstance(value, list):
            parsed[key] = [str(item).strip() for item in value if str(item).strip()]
        elif value:
            parsed[key] = [str(value).strip()]
    return parsed


def _header_map(table: Any) -> dict[str, int]:
    first_row = table.find("tr")
    if first_row is None:
        return {}
    headers = [
        cell.get_text(" ", strip=True).lower()
        for cell in first_row.find_all(["th", "td"])
    ]
    mapping: dict[str, int] = {}
    for index, header in enumerate(headers):
        if "fund" in header and "fund" not in mapping:
            mapping["fund"] = index
        elif header in {"amc", "company"} or "amc" in header:
            mapping["amc"] = index
        elif "category" in header:
            mapping["category"] = index
        elif header == "nav" or header.startswith("nav"):
            mapping["nav"] = index
        elif "validity" in header or header == "date":
            mapping["validity"] = index
    return mapping


def _asset_type(category: str) -> AssetType:
    lowered = category.lower()
    for needle, asset_type in _CATEGORY_TYPES:
        if needle in lowered:
            return asset_type
    return AssetType.MUTUAL_FUND


def _clean_number(value: str) -> str:
    return re.sub(r"[^\d.\-]", "", value)


def _parse_date_text(value: str) -> str | None:
    text = re.sub(r"\s+", " ", value or "").strip()
    if not text:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _names_match(left: str, right: str) -> bool:
    if not left or not right:
        return False
    return left == right or left in right or right in left
