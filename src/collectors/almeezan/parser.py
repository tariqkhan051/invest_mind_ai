"""Parse Al Meezan Group fund-prices HTML tables."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from bs4 import BeautifulSoup

from src.domain.enums import AssetType

_DATE_FORMATS = (
    "%d %b %Y",
    "%d-%b-%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%b %d, %Y",
)

_CATEGORY_ASSET_TYPES: tuple[tuple[str, AssetType], ...] = (
    ("money market", AssetType.MONEY_MARKET_FUND),
    ("cash", AssetType.CASH_MANAGEMENT_FUND),
    ("income", AssetType.INCOME_FUND),
    ("equity", AssetType.EQUITY_FUND),
    ("index", AssetType.EQUITY_FUND),
    ("balanced", AssetType.BALANCED_FUND),
    ("asset allocation", AssetType.BALANCED_FUND),
    ("exchange traded", AssetType.EQUITY_FUND),
    ("pension", AssetType.MUTUAL_FUND),
    ("commodit", AssetType.MUTUAL_FUND),
    ("fund of fund", AssetType.MUTUAL_FUND),
)


def parse_almeezan_fund_prices_html(html: str) -> list[dict[str, Any]]:
    """Extract fund price rows from the Al Meezan fund-prices page."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        return []

    category: str | None = None
    rows: list[dict[str, Any]] = []
    body = table.find("tbody") or table
    for tr in body.find_all("tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        classes = cells[0].get("class") or []
        if "table-head" in classes:
            category = cells[0].get_text(" ", strip=True) or category
            continue
        if len(cells) < 6:
            continue

        name = _clean_fund_name(cells[0].get_text(" ", strip=True))
        if not name:
            continue

        validity = _parse_date_text(cells[2].get_text(" ", strip=True))
        repurchase = _parse_decimal(cells[3].get_text(" ", strip=True))
        offer = _parse_decimal(cells[4].get_text(" ", strip=True))
        nav = _parse_decimal(cells[5].get_text(" ", strip=True))
        mtd = _parse_decimal(_cell(cells, 15))
        fytd = _parse_decimal(_cell(cells, 16))
        cytd = _parse_decimal(_cell(cells, 17))

        effective_nav = _effective_nav(nav, offer, repurchase)
        if effective_nav is None or validity is None:
            continue

        asset_type = _category_to_asset_type(category)
        rows.append(
            {
                "name": name,
                "category": category,
                "asset_type": asset_type.value,
                "date": validity.isoformat(),
                "nav": str(effective_nav),
                "offer": str(offer) if offer is not None else None,
                "repurchase": str(repurchase) if repurchase is not None else None,
                "mtd_return": str(mtd) if mtd is not None else None,
                "fytd_return": str(fytd) if fytd is not None else None,
                "cytd_return": str(cytd) if cytd is not None else None,
                "amc": "Al Meezan",
                "is_shariah": True,
            }
        )
    return rows


def parse_alias_config(raw: Any) -> dict[str, str]:
    """Normalize fund_aliases config into lowercase name → symbol map."""
    aliases: dict[str, str] = {}
    if not isinstance(raw, dict):
        return aliases
    for symbol, names in raw.items():
        symbol_key = str(symbol).strip().upper()
        if not symbol_key:
            continue
        if isinstance(names, str):
            aliases[_normalize_name(names)] = symbol_key
            continue
        if isinstance(names, list):
            for name in names:
                aliases[_normalize_name(str(name))] = symbol_key
    return aliases


def resolve_fund_symbol(
    name: str,
    aliases: dict[str, str],
    known_names: dict[str, str],
) -> str | None:
    """Resolve a fund display name to a watchlist symbol."""
    normalized = _normalize_name(name)
    if normalized in aliases:
        return aliases[normalized]
    for symbol, display_name in known_names.items():
        if _normalize_name(display_name) == normalized:
            return symbol.upper()
    return None


def _effective_nav(
    nav: Decimal | None,
    offer: Decimal | None,
    repurchase: Decimal | None,
) -> Decimal | None:
    if nav is not None and nav > 0:
        return nav
    if offer is not None and offer > 0 and repurchase is not None and repurchase > 0:
        return (offer + repurchase) / Decimal("2")
    if offer is not None and offer > 0:
        return offer
    if repurchase is not None and repurchase > 0:
        return repurchase
    return None


def _category_to_asset_type(category: str | None) -> AssetType:
    text = (category or "").lower()
    for needle, asset_type in _CATEGORY_ASSET_TYPES:
        if needle in text:
            return asset_type
    return AssetType.MUTUAL_FUND


def _clean_fund_name(name: str) -> str:
    cleaned = re.sub(r"[*]+$", "", name).strip()
    return cleaned


def _normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def _cell(cells: list[Any], index: int) -> str:
    if index >= len(cells):
        return ""
    return cells[index].get_text(" ", strip=True)


def _parse_decimal(value: str) -> Decimal | None:
    text = value.replace(",", "").replace("%", "").strip()
    if not text or text in {"-", "—", "N/A", "n/a"}:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def _parse_date_text(value: str) -> Any:
    text = re.sub(r"\s+", " ", value.strip())
    if not text:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
