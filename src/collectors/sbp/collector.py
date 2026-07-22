"""SBP macroeconomic indicator collector."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.models import MacroIndicatorRecord, ProviderHealth
from src.collectors.base.validator import validate_macro_record
from src.config.settings import Settings
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class SbpCollector(BaseCollector):
    """Collect macroeconomic indicators from SBP."""

    provider_name = "sbp"

    def __init__(
        self,
        settings: Settings,
        market_data_repository: MarketDataRepository,
        http_client: CollectorHttpClient | None = None,
    ) -> None:
        super().__init__(settings)
        self._market_data_repository = market_data_repository
        timeout = int(self._provider_config.get("timeout_seconds", 30))
        retries = int(self._provider_config.get("retry_attempts", 3))
        self._http_client = http_client or CollectorHttpClient(timeout, retries)

    def collect(self) -> Any:
        """Download macro indicator data from the configured SBP endpoint."""
        base_url = self._get_config_value("base_url").rstrip("/")
        macro_path = self._get_config_value("macro_path", "/api/indicators")
        url = f"{base_url}{macro_path}"
        return self._http_client.get_json(url)

    def normalize(self, raw_data: Any) -> list[MacroIndicatorRecord]:
        """Normalize provider payload into macro indicator records."""
        rows = (
            raw_data.get("records", raw_data)
            if isinstance(raw_data, dict)
            else raw_data
        )
        if not isinstance(rows, list):
            return []

        records: list[MacroIndicatorRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            indicator_name = str(
                row.get("indicator_name") or row.get("name") or ""
            ).strip()
            release_date = self._parse_date(row.get("release_date") or row.get("date"))
            actual_value = self._parse_decimal(
                row.get("actual_value") or row.get("value")
            )
            if not indicator_name or release_date is None or actual_value is None:
                continue
            records.append(
                MacroIndicatorRecord(
                    indicator_name=indicator_name,
                    release_date=release_date,
                    actual_value=actual_value,
                    source=self.provider_name,
                    country=str(row.get("country", "PK")),
                    frequency=row.get("frequency"),
                    forecast_value=self._parse_decimal(row.get("forecast_value")),
                    previous_value=self._parse_decimal(row.get("previous_value")),
                    unit=row.get("unit"),
                    importance=row.get("importance"),
                    trend=row.get("trend"),
                )
            )
        return records

    def save(self, records: list[MacroIndicatorRecord]) -> tuple[int, int]:
        """Persist validated macro records."""
        saved = 0
        duplicates = 0
        for record in records:
            if self._market_data_repository.save_macro(record):
                saved += 1
            else:
                duplicates += 1
        return saved, duplicates

    def _validate_record(self, record: MacroIndicatorRecord) -> list[str]:
        return validate_macro_record(record)

    def health_check(self) -> ProviderHealth:
        base_url = self._get_config_value("base_url").rstrip("/")
        healthy = self._http_client.health_check(base_url)
        return ProviderHealth(
            provider=self.provider_name,
            healthy=healthy,
            message="Provider reachable." if healthy else "Provider unreachable.",
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
