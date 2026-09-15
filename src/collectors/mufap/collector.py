"""MUFAP mutual fund NAV collector."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from src.collectors.base.asset_factory import ensure_mutual_fund
from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.local_source import load_local_payload, resolve_local_path
from src.collectors.base.models import NavRecord, ProviderHealth
from src.collectors.base.validator import validate_nav_record
from src.collectors.mufap.parser import (
    parse_alias_config,
    parse_mufap_nav_html,
    resolve_fund_symbol,
)
from src.config.settings import Settings
from src.domain.enums import AssetType
from src.repositories.interfaces.asset_repository import AssetRepository
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class MufapCollector(BaseCollector):
    """Collect daily mutual fund NAV data from MUFAP or local imports."""

    provider_name = "mufap"

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
        timeout = int(self._provider_config.get("timeout_seconds", 30))
        retries = int(self._provider_config.get("retry_attempts", 3))
        self._http_client = http_client or CollectorHttpClient(timeout, retries)
        self._fund_meta: dict[str, dict[str, Any]] = {}

    def collect(self) -> Any:
        """Download NAV data from local imports or live MUFAP pages."""
        source = self._get_config_value("source", "live")
        if source == "local":
            path = resolve_local_path(
                self._settings.project_root,
                self._get_config_value("local_path", "data/imports/mufap_nav.json"),
            )
            return load_local_payload(path)
        if source == "live":
            urls = self._live_urls()
            pages: list[str] = []
            for url in urls:
                pages.append(self._http_client.get_text(url))
            return {"html_pages": pages, "source": "live"}
        base_url = self._get_config_value("base_url").rstrip("/")
        nav_path = self._get_config_value("nav_path", "/api/nav/daily")
        url = f"{base_url}{nav_path}"
        return self._http_client.get_json(url)

    def normalize(self, raw_data: Any) -> list[NavRecord]:
        """Normalize provider payload into NAV records."""
        if isinstance(raw_data, dict) and raw_data.get("source") == "live":
            return self._normalize_live_pages(raw_data.get("html_pages", []))
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
            symbol = str(row.get("symbol", "")).strip().upper()
            nav_date = self._parse_date(row.get("date") or row.get("nav_date"))
            nav_value = self._parse_decimal(row.get("nav"))
            if not symbol or nav_date is None or nav_value is None:
                continue
            records.append(
                NavRecord(
                    symbol=symbol,
                    nav_date=nav_date,
                    nav=nav_value,
                    source=self.provider_name,
                    adjusted_nav=self._parse_decimal(row.get("adjusted_nav")),
                    daily_return=self._parse_decimal(row.get("daily_return")),
                    dividend=self._parse_decimal(row.get("dividend")),
                )
            )
        return records

    def save(self, records: list[NavRecord]) -> tuple[int, int]:
        """Persist validated NAV records, creating watchlist assets when enabled."""
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
                    management_company=meta.get("amc"),
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
                self._get_config_value("local_path", "data/imports/mufap_nav.json"),
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
        url = (
            self._live_urls()[0]
            if source == "live"
            else self._get_config_value("base_url").rstrip("/")
        )
        healthy = self._http_client.health_check(url)
        return ProviderHealth(
            provider=self.provider_name,
            healthy=healthy,
            message="Provider reachable." if healthy else "Provider unreachable.",
        )

    def _normalize_live_pages(self, pages: Any) -> list[NavRecord]:
        if not isinstance(pages, list):
            return []
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
        shariah_only = bool(
            self._provider_config.get("shariah_only", self._settings.shariah_mode)
        )
        watchlist_only = not bool(
            self._provider_config.get("auto_create_assets", False)
        )
        self._fund_meta: dict[str, dict[str, Any]] = {}
        records: list[NavRecord] = []
        seen: set[tuple[str, date]] = set()
        for page in pages:
            if not isinstance(page, str):
                continue
            for row in parse_mufap_nav_html(page):
                if shariah_only and not row.get("is_shariah"):
                    continue
                symbol = resolve_fund_symbol(
                    str(row.get("name", "")), aliases, known_names
                )
                if symbol is None:
                    if watchlist_only:
                        continue
                    symbol = self._slug_symbol(str(row.get("name", "")))
                nav_date = self._parse_date(row.get("date")) or date.today()
                nav_value = self._parse_decimal(row.get("nav"))
                if not symbol or nav_value is None:
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
                    )
                )
        return records

    def _live_urls(self) -> list[str]:
        configured = self._provider_config.get("nav_urls")
        if isinstance(configured, list) and configured:
            return [str(url).strip() for url in configured if str(url).strip()]
        base_url = self._get_config_value(
            "base_url", "https://www.mufap.com.pk"
        ).rstrip("/")
        nav_path = self._get_config_value(
            "nav_path", "/Industry/IndustryStatDaily?tab=3"
        )
        return [f"{base_url}{nav_path}"]

    def _log_missing_asset(self, symbol: str) -> None:
        from src.core.logging import get_logger

        get_logger("collectors.mufap").warning(
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
            if word not in {"THE", "FUND", "LIMITED", "LTD", "OF", "AND", "PLAN"}
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
