"""MUFAP mutual fund NAV collector."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.models import NavRecord, ProviderHealth
from src.collectors.base.validator import validate_nav_record
from src.config.settings import Settings
from src.repositories.interfaces.asset_repository import AssetRepository
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class MufapCollector(BaseCollector):
    """Collect daily mutual fund NAV data from MUFAP."""

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

    def collect(self) -> Any:
        """Download NAV data from the configured MUFAP endpoint."""
        base_url = self._get_config_value("base_url").rstrip("/")
        nav_path = self._get_config_value("nav_path", "/api/nav/daily")
        url = f"{base_url}{nav_path}"
        return self._http_client.get_json(url)

    def normalize(self, raw_data: Any) -> list[NavRecord]:
        """Normalize provider payload into NAV records."""
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
        """Persist validated NAV records."""
        saved = 0
        duplicates = 0
        for record in records:
            asset = self._asset_repository.get_by_symbol(record.symbol)
            if asset is None:
                self._log_missing_asset(record.symbol)
                continue
            if self._market_data_repository.save_nav(record, asset.id):
                saved += 1
            else:
                duplicates += 1
        return saved, duplicates

    def _validate_record(self, record: NavRecord) -> list[str]:
        return validate_nav_record(record)

    def health_check(self) -> ProviderHealth:
        base_url = self._get_config_value("base_url").rstrip("/")
        healthy = self._http_client.health_check(base_url)
        return ProviderHealth(
            provider=self.provider_name,
            healthy=healthy,
            message="Provider reachable." if healthy else "Provider unreachable.",
        )

    def _log_missing_asset(self, symbol: str) -> None:
        from src.core.logging import get_logger

        get_logger("collectors.mufap").warning(
            "nav_import_skipped_unknown_asset symbol={}", symbol
        )

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
