"""PSX stock price collector."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from src.collectors.base.asset_factory import ensure_stock
from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.local_source import load_local_payload, resolve_local_path
from src.collectors.base.models import PriceRecord, ProviderHealth
from src.collectors.base.validator import validate_price_record
from src.collectors.psx.parser import parse_psx_eod_series
from src.config.settings import Settings
from src.domain.enums import AssetType
from src.repositories.interfaces.asset_repository import AssetRepository
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class PsxCollector(BaseCollector):
    """Collect PSX stock price data from PSX or local imports."""

    provider_name = "psx"

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

    def collect(self) -> Any:
        """Download stock price data from local imports or live PSX timeseries."""
        source = self._get_config_value("source", "live")
        if source == "local":
            path = resolve_local_path(
                self._settings.project_root,
                self._get_config_value("local_path", "data/imports/psx_prices.json"),
            )
            return load_local_payload(path)
        if source == "live":
            base_url = self._get_config_value(
                "base_url", "https://dps.psx.com.pk"
            ).rstrip("/")
            eod_path = self._get_config_value("eod_path", "/timeseries/eod/{symbol}")
            series: dict[str, Any] = {}
            errors: list[str] = []
            for symbol in self._symbols():
                url = f"{base_url}{eod_path.format(symbol=symbol)}"
                try:
                    series[symbol] = self._http_client.get_json(url)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{symbol}: {exc}")
            return {"source": "live", "series": series, "errors": errors}
        base_url = self._get_config_value("base_url").rstrip("/")
        prices_path = self._get_config_value("prices_path", "/historical")
        url = f"{base_url}{prices_path}"
        return self._http_client.get_json(url)

    def normalize(self, raw_data: Any) -> list[PriceRecord]:
        """Normalize provider payload into price records."""
        if isinstance(raw_data, dict) and raw_data.get("source") == "live":
            return self._normalize_live_series(raw_data.get("series", {}))
        rows = (
            raw_data.get("records", raw_data)
            if isinstance(raw_data, dict)
            else raw_data
        )
        if not isinstance(rows, list):
            return []

        records: list[PriceRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            symbol = str(row.get("symbol", "")).strip().upper()
            price_date = self._parse_date(row.get("date") or row.get("price_date"))
            close_price = self._parse_decimal(
                row.get("close") or row.get("close_price")
            )
            if not symbol or price_date is None or close_price is None:
                continue
            records.append(
                PriceRecord(
                    symbol=symbol,
                    price_date=price_date,
                    close_price=close_price,
                    source=self.provider_name,
                    open_price=self._parse_decimal(row.get("open")),
                    high_price=self._parse_decimal(row.get("high")),
                    low_price=self._parse_decimal(row.get("low")),
                    adjusted_close=self._parse_decimal(row.get("adjusted_close")),
                    volume=self._parse_decimal(row.get("volume")),
                )
            )
        return records

    def save(self, records: list[PriceRecord]) -> tuple[int, int]:
        """Persist validated price records."""
        saved = 0
        duplicates = 0
        auto_create = bool(self._provider_config.get("auto_create_assets", True))
        for record in records:
            asset = self._asset_repository.get_by_symbol(record.symbol)
            if asset is None:
                if not auto_create:
                    continue
                asset = ensure_stock(
                    self._asset_repository,
                    symbol=record.symbol,
                    display_name=record.symbol,
                )
            if self._market_data_repository.save_price(record, asset.id):
                saved += 1
            else:
                duplicates += 1
        return saved, duplicates

    def _validate_record(self, record: PriceRecord) -> list[str]:
        return validate_price_record(record)

    def health_check(self) -> ProviderHealth:
        source = self._get_config_value("source", "live")
        if source == "local":
            path = resolve_local_path(
                self._settings.project_root,
                self._get_config_value("local_path", "data/imports/psx_prices.json"),
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
        base_url = self._get_config_value(
            "base_url", "https://dps.psx.com.pk"
        ).rstrip("/")
        healthy = self._http_client.health_check(base_url)
        return ProviderHealth(
            provider=self.provider_name,
            healthy=healthy,
            message="Provider reachable." if healthy else "Provider unreachable.",
        )

    def _normalize_live_series(self, series: Any) -> list[PriceRecord]:
        if not isinstance(series, dict):
            return []
        history_days = int(self._provider_config.get("history_days", 400))
        records: list[PriceRecord] = []
        for symbol, payload in series.items():
            for row in parse_psx_eod_series(str(symbol), payload, history_days):
                price_date = self._parse_date(row.get("date"))
                close_price = self._parse_decimal(row.get("close"))
                if price_date is None or close_price is None:
                    continue
                records.append(
                    PriceRecord(
                        symbol=str(row["symbol"]),
                        price_date=price_date,
                        close_price=close_price,
                        source=self.provider_name,
                        open_price=self._parse_decimal(row.get("open")),
                        volume=self._parse_decimal(row.get("volume")),
                    )
                )
        return records

    def _symbols(self) -> list[str]:
        configured = self._provider_config.get("symbols", [])
        symbols: list[str] = []
        if isinstance(configured, list):
            symbols.extend(str(item).strip().upper() for item in configured if str(item).strip())
        existing = [
            asset.symbol.upper()
            for asset in self._asset_repository.find_by_type(AssetType.STOCK)
        ]
        merged = list(dict.fromkeys([*symbols, *existing]))
        return merged

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
