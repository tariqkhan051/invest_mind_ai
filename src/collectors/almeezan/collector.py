"""Al Meezan mutual fund price collector."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from src.collectors.almeezan.parser import (
    parse_alias_config,
    parse_almeezan_fund_prices_html,
    resolve_fund_symbol,
)
from src.collectors.base.asset_factory import ensure_mutual_fund
from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.local_source import load_local_payload, resolve_local_path
from src.collectors.base.models import NavRecord, ProviderHealth
from src.collectors.base.validator import validate_nav_record
from src.config.settings import Settings
from src.domain.enums import AssetType
from src.repositories.interfaces.asset_repository import AssetRepository
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class AlMeezanCollector(BaseCollector):
    """Collect fund offer/repurchase/NAV from Al Meezan Group."""

    provider_name = "almeezan"

    def __init__(
        self,
        settings: Settings,
        asset_repository: AssetRepository,
        market_data_repository: MarketDataRepository,
        http_client: CollectorHttpClient | None = None,
    ) -> None:
        super().__init__(settings)
        self._asset_repository = asset_repository
        self._market_data_repository = market_data_repository
        timeout = int(self._provider_config.get("timeout_seconds", 45))
        retries = int(self._provider_config.get("retry_attempts", 3))
        self._http_client = http_client or CollectorHttpClient(timeout, retries)
        self._fund_meta: dict[str, dict[str, Any]] = {}

    def collect(self) -> Any:
        source = self._get_config_value("source", "live")
        if source == "local":
            path = resolve_local_path(
                self._settings.project_root,
                self._get_config_value(
                    "local_path", "data/imports/almeezan_nav.json"
                ),
            )
            return load_local_payload(path)
        if source == "live":
            url = self._live_url()
            return {"html": self._http_client.get_text(url), "source": "live"}
        base_url = self._get_config_value("base_url").rstrip("/")
        nav_path = self._get_config_value("nav_path", "/fund-prices/")
        return self._http_client.get_json(f"{base_url}{nav_path}")

    def normalize(self, raw_data: Any) -> list[NavRecord]:
        if isinstance(raw_data, dict) and raw_data.get("source") == "live":
            return self._normalize_live_html(str(raw_data.get("html", "")))
        rows = (
            raw_data.get("records", raw_data)
            if isinstance(raw_data, dict)
            else raw_data
        )
        if not isinstance(rows, list):
            return []
        records: list[NavRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            record = self._row_to_record(row, default_source=self.provider_name)
            if record is not None:
                records.append(record)
        return records

    def save(self, records: list[NavRecord]) -> tuple[int, int]:
        saved = 0
        duplicates = 0
        auto_create = bool(self._provider_config.get("auto_create_assets", False))
        for record in records:
            asset = self._asset_repository.get_by_symbol(record.symbol)
            if asset is None:
                if not auto_create:
                    self._log_missing_asset(record.symbol)
                    continue
                meta = self._fund_meta.get(record.symbol, {})
                asset = ensure_mutual_fund(
                    self._asset_repository,
                    symbol=record.symbol,
                    display_name=str(meta.get("name") or record.symbol),
                    asset_type=self._parse_asset_type(meta.get("asset_type")),
                    is_shariah=bool(meta.get("is_shariah", True)),
                    management_company=str(meta.get("amc") or "Al Meezan"),
                    provider=self.provider_name,
                )
            if self._market_data_repository.save_nav(record, asset.id):
                saved += 1
            else:
                duplicates += 1
        return saved, duplicates

    def _validate_record(self, record: NavRecord) -> list[str]:
        return validate_nav_record(record)

    def health_check(self) -> ProviderHealth:
        source = self._get_config_value("source", "live")
        if source == "local":
            path = resolve_local_path(
                self._settings.project_root,
                self._get_config_value(
                    "local_path", "data/imports/almeezan_nav.json"
                ),
            )
            healthy = path.exists()
            return ProviderHealth(
                provider=self.provider_name,
                healthy=healthy,
                message=(
                    f"Local import ready: {path}"
                    if healthy
                    else f"Local import missing: {path}"
                ),
            )
        url = self._live_url()
        healthy = self._http_client.health_check(url)
        return ProviderHealth(
            provider=self.provider_name,
            healthy=healthy,
            message="Provider reachable." if healthy else "Provider unreachable.",
        )

    def _normalize_live_html(self, html: str) -> list[NavRecord]:
        aliases = parse_alias_config(self._provider_config.get("fund_aliases", {}))
        known_names = {
            asset.symbol: asset.display_name
            for asset_type in (
                AssetType.MUTUAL_FUND,
                AssetType.MONEY_MARKET_FUND,
                AssetType.INCOME_FUND,
                AssetType.EQUITY_FUND,
                AssetType.BALANCED_FUND,
                AssetType.CASH_MANAGEMENT_FUND,
            )
            for asset in self._asset_repository.find_by_type(asset_type)
        }
        watchlist_only = not bool(self._provider_config.get("auto_create_assets", False))
        self._fund_meta = {}
        records: list[NavRecord] = []
        seen: set[tuple[str, date]] = set()
        for row in parse_almeezan_fund_prices_html(html):
            symbol = resolve_fund_symbol(str(row.get("name", "")), aliases, known_names)
            if symbol is None:
                if watchlist_only:
                    continue
                symbol = self._slug_symbol(str(row.get("name", "")))
            if not symbol:
                continue
            nav_date = self._parse_date(row.get("date"))
            nav_value = self._parse_decimal(row.get("nav"))
            if nav_date is None or nav_value is None:
                continue
            key = (symbol, nav_date)
            if key in seen:
                continue
            seen.add(key)
            self._fund_meta[symbol] = row
            records.append(
                NavRecord(
                    symbol=symbol,
                    nav_date=nav_date,
                    nav=nav_value,
                    source=self.provider_name,
                    offer_price=self._parse_decimal(row.get("offer")),
                    repurchase_price=self._parse_decimal(row.get("repurchase")),
                    fytd_return=self._parse_decimal(row.get("fytd_return")),
                    mtd_return=self._parse_decimal(row.get("mtd_return")),
                    category=str(row.get("category") or "") or None,
                )
            )
        return records

    def _row_to_record(self, row: dict[str, Any], default_source: str) -> NavRecord | None:
        symbol = str(row.get("symbol", "")).strip().upper()
        nav_date = self._parse_date(row.get("date") or row.get("nav_date"))
        nav_value = self._parse_decimal(row.get("nav"))
        if not symbol or nav_date is None or nav_value is None:
            return None
        return NavRecord(
            symbol=symbol,
            nav_date=nav_date,
            nav=nav_value,
            source=str(row.get("source") or default_source),
            adjusted_nav=self._parse_decimal(row.get("adjusted_nav")),
            daily_return=self._parse_decimal(row.get("daily_return")),
            dividend=self._parse_decimal(row.get("dividend")),
            offer_price=self._parse_decimal(row.get("offer") or row.get("offer_price")),
            repurchase_price=self._parse_decimal(
                row.get("repurchase") or row.get("repurchase_price")
            ),
            fytd_return=self._parse_decimal(row.get("fytd_return")),
            mtd_return=self._parse_decimal(row.get("mtd_return")),
            category=str(row.get("category") or "") or None,
        )

    def _live_url(self) -> str:
        configured = self._provider_config.get("nav_urls")
        if isinstance(configured, list) and configured:
            return str(configured[0]).strip()
        base_url = self._get_config_value(
            "base_url", "https://www.almeezangroup.com"
        ).rstrip("/")
        nav_path = self._get_config_value("nav_path", "/fund-prices/")
        return f"{base_url}{nav_path}"

    def _log_missing_asset(self, symbol: str) -> None:
        from src.core.logging import get_logger

        get_logger("collectors.almeezan").warning(
            "nav_import_skipped_unknown_asset symbol={}", symbol
        )

    @staticmethod
    def _parse_asset_type(value: Any) -> AssetType:
        if isinstance(value, AssetType):
            return value
        try:
            return AssetType(str(value))
        except ValueError:
            return AssetType.MUTUAL_FUND

    @staticmethod
    def _slug_symbol(name: str) -> str:
        words = [
            word
            for word in "".join(
                ch if ch.isalnum() else " " for ch in name.upper()
            ).split()
            if word not in {"THE", "FUND", "LIMITED", "LTD", "OF", "AND", "PLAN", "UNITS", "TYPE", "B"}
        ]
        if not words:
            return ""
        if len(words) == 1:
            return words[0][:16]
        initials = "".join(word[0] for word in words[:8])
        return initials if len(initials) >= 3 else "".join(words)[:16]

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if value is None:
            return None
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _parse_decimal(value: Any) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
