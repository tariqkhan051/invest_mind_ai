"""Base collector interface."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from time import perf_counter
from typing import Any

from src.collectors.base.models import (
    CollectorRunResult,
    CollectorStatus,
    ProviderHealth,
)
from src.config.settings import Settings
from src.core.logging import get_logger

logger = get_logger("collectors.base")


class BaseCollector(ABC):
    """Abstract data collector implementing the standard pipeline.

    Flow: collect → validate → normalize → save
    See docs/11_DATA_COLLECTION.md §3–4.
    """

    provider_name: str = "base"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider_config = settings.providers_config.get("providers", {}).get(
            self.provider_name,
            {},
        )

    @property
    def enabled(self) -> bool:
        """Return True when the provider is enabled in configuration."""
        return bool(self._provider_config.get("enabled", True))

    def run(self) -> CollectorRunResult:
        """Execute the full collector pipeline."""
        started_at = datetime.now(UTC)
        start_time = perf_counter()
        result = CollectorRunResult(
            provider=self.provider_name,
            status=CollectorStatus.RUNNING,
            started_at=started_at,
        )

        if not self.enabled:
            result.status = CollectorStatus.FAILED
            result.errors.append("Provider is disabled in configuration.")
            result.finished_at = datetime.now(UTC)
            return result

        try:
            raw_data = self.collect()
            self._store_raw_payload(raw_data)
            normalized = self.normalize(raw_data)
            validated, rejected = self.validate(normalized)
            result.rows_collected = len(normalized)
            result.rows_rejected = rejected
            saved, duplicates = self.save(validated)
            result.rows_saved = saved
            result.rows_duplicates = duplicates
            result.status = (
                CollectorStatus.DEGRADED
                if result.errors or result.rows_rejected
                else CollectorStatus.SUCCESS
            )
        except Exception as exc:
            logger.exception(
                "collector_failed provider={} error={}",
                self.provider_name,
                str(exc),
            )
            result.status = CollectorStatus.FAILED
            result.errors.append(str(exc))

        result.duration_ms = (perf_counter() - start_time) * 1000
        result.finished_at = datetime.now(UTC)
        logger.info(
            "collector_completed provider={} status={} saved={} rejected={} "
            "duration_ms={:.2f}",
            self.provider_name,
            result.status.value,
            result.rows_saved,
            result.rows_rejected,
            result.duration_ms,
        )
        return result

    @abstractmethod
    def collect(self) -> Any:
        """Download raw data from the external provider."""

    @abstractmethod
    def normalize(self, raw_data: Any) -> list[Any]:
        """Convert provider-specific data into internal DTOs."""

    def validate(self, records: list[Any]) -> tuple[list[Any], int]:
        """Validate normalized records and return valid rows plus rejection count."""
        valid: list[Any] = []
        rejected = 0
        for record in records:
            errors = self._validate_record(record)
            if errors:
                rejected += 1
                logger.warning(
                    "collector_validation_failed provider={} errors={}",
                    self.provider_name,
                    errors,
                )
            else:
                valid.append(record)
        return valid, rejected

    @abstractmethod
    def save(self, records: list[Any]) -> tuple[int, int]:
        """Persist validated records. Returns (saved_count, duplicate_count)."""

    @abstractmethod
    def _validate_record(self, record: Any) -> list[str]:
        """Validate a single normalized record."""

    def health_check(self) -> ProviderHealth:
        """Check provider availability."""
        return ProviderHealth(
            provider=self.provider_name,
            healthy=False,
            message="Health check not implemented.",
        )

    def _store_raw_payload(self, raw_data: Any) -> None:
        """Persist raw provider payload for auditability."""
        raw_dir = self._settings.project_root / "data" / "raw" / self.provider_name
        raw_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        file_path = raw_dir / f"{timestamp}.json"
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(raw_data, file, default=str)

    def _get_config_value(self, key: str, default: str = "") -> str:
        return str(self._provider_config.get(key, default))
