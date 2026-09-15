"""SBP macroeconomic indicator collector."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.local_source import load_local_payload, resolve_local_path
from src.collectors.base.models import MacroIndicatorRecord, ProviderHealth
from src.collectors.base.validator import validate_macro_record
from src.collectors.sbp.parser import parse_sbp_homepage, parse_world_bank_inflation
from src.config.settings import Settings
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class SbpCollector(BaseCollector):
    """Collect macroeconomic indicators from SBP or local imports."""

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
        """Download macro indicator data from local imports or live SBP sources."""
        source = self._get_config_value("source", "live")
        if source == "local":
            path = resolve_local_path(
                self._settings.project_root,
                self._get_config_value("local_path", "data/imports/sbp_macro.json"),
            )
            return load_local_payload(path)
        if source == "live":
            homepage_url = self._get_config_value(
                "homepage_url", "https://www.sbp.org.pk/"
            )
            inflation_url = self._get_config_value(
                "inflation_url",
                "https://api.worldbank.org/v2/country/PK/indicator/FP.CPI.TOTL.ZG"
                "?format=json&per_page=20",
            )
            payload: dict[str, Any] = {"source": "live", "homepage_html": "", "inflation": []}
            try:
                payload["homepage_html"] = self._http_client.get_text(homepage_url)
            except Exception as exc:  # noqa: BLE001
                payload["homepage_error"] = str(exc)
            try:
                payload["inflation"] = self._http_client.get_json(inflation_url)
            except Exception as exc:  # noqa: BLE001
                payload["inflation_error"] = str(exc)
            return payload
        base_url = self._get_config_value("base_url").rstrip("/")
        macro_path = self._get_config_value("macro_path", "/api/indicators")
        url = f"{base_url}{macro_path}"
        return self._http_client.get_json(url)

    def normalize(self, raw_data: Any) -> list[MacroIndicatorRecord]:
        """Normalize provider payload into macro indicator records."""
        if isinstance(raw_data, dict) and raw_data.get("source") == "live":
            rows = parse_sbp_homepage(str(raw_data.get("homepage_html", "")))
            rows.extend(parse_world_bank_inflation(raw_data.get("inflation")))
            return self._records_from_rows(rows, default_source=self.provider_name)
        rows = (
            raw_data.get("records", raw_data)
            if isinstance(raw_data, dict)
            else raw_data
        )
        return self._records_from_rows(rows if isinstance(rows, list) else [])

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
        source = self._get_config_value("source", "live")
        if source == "local":
            path = resolve_local_path(
                self._settings.project_root,
                self._get_config_value("local_path", "data/imports/sbp_macro.json"),
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
        homepage_url = self._get_config_value("homepage_url", "https://www.sbp.org.pk/")
        healthy = self._http_client.health_check(homepage_url)
        return ProviderHealth(
            provider=self.provider_name,
            healthy=healthy,
            message="Provider reachable." if healthy else "Provider unreachable.",
        )

    def _records_from_rows(
        self,
        rows: list[Any],
        default_source: str | None = None,
    ) -> list[MacroIndicatorRecord]:
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
                    source=str(row.get("source") or default_source or self.provider_name),
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
