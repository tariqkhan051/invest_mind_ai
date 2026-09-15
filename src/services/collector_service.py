"""Collector orchestration service."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.collectors.base.models import (
    CollectorRunResult,
    CollectorStatus,
    ProviderHealth,
)
from src.collectors.registry import build_collectors
from src.config.settings import Settings
from src.core.logging import get_logger

logger = get_logger("services.collector")


@dataclass
class CollectorStatusSnapshot:
    """Latest collector execution status."""

    provider: str
    last_status: CollectorStatus
    last_run_at: datetime | None
    rows_saved: int = 0
    rows_rejected: int = 0
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)
    healthy: bool | None = None


class CollectorService:
    """Run and monitor external data collectors."""

    def __init__(self, settings: Settings, session: Session) -> None:
        self._settings = settings
        self._session = session
        self._collectors = build_collectors(settings, session)
        self._status: dict[str, CollectorStatusSnapshot] = {
            name: CollectorStatusSnapshot(
                provider=name,
                last_status=CollectorStatus.IDLE,
                last_run_at=None,
            )
            for name in self._collectors
        }

    def run_nav_import(self) -> CollectorRunResult:
        """Run MUFAP then Al Meezan NAV collectors and return a combined result."""
        results = [
            self._run_collector("mufap"),
            self._run_collector("almeezan"),
        ]
        errors = [error for result in results for error in result.errors]
        failed = all(result.status == CollectorStatus.FAILED for result in results)
        degraded = any(
            result.status in {CollectorStatus.FAILED, CollectorStatus.DEGRADED}
            for result in results
        )
        status = (
            CollectorStatus.FAILED
            if failed
            else (CollectorStatus.DEGRADED if degraded else CollectorStatus.SUCCESS)
        )
        started = min(result.started_at for result in results)
        finished = max(
            (
                result.finished_at
                for result in results
                if result.finished_at is not None
            ),
            default=datetime.now(UTC),
        )
        return CollectorRunResult(
            provider="nav",
            status=status,
            rows_collected=sum(result.rows_collected for result in results),
            rows_saved=sum(result.rows_saved for result in results),
            rows_rejected=sum(result.rows_rejected for result in results),
            rows_duplicates=sum(result.rows_duplicates for result in results),
            duration_ms=sum(result.duration_ms for result in results),
            errors=errors,
            started_at=started,
            finished_at=finished,
        )

    def run_almeezan_import(self) -> CollectorRunResult:
        """Run the Al Meezan fund-prices collector."""
        return self._run_collector("almeezan")

    def run_stock_import(self) -> CollectorRunResult:
        """Run the PSX stock price collector."""
        return self._run_collector("psx")

    def run_macro_import(self) -> CollectorRunResult:
        """Run the SBP macro indicator collector."""
        return self._run_collector("sbp")

    def run_news_import(self) -> CollectorRunResult:
        """Run the news collector."""
        return self._run_collector("news")

    def get_status(self) -> list[CollectorStatusSnapshot]:
        """Return status for all configured collectors."""
        snapshots: list[CollectorStatusSnapshot] = []
        for name, collector in self._collectors.items():
            snapshot = self._status[name]
            health = collector.health_check()
            snapshots.append(
                CollectorStatusSnapshot(
                    provider=name,
                    last_status=snapshot.last_status,
                    last_run_at=snapshot.last_run_at,
                    rows_saved=snapshot.rows_saved,
                    rows_rejected=snapshot.rows_rejected,
                    duration_ms=snapshot.duration_ms,
                    errors=list(snapshot.errors),
                    healthy=health.healthy,
                )
            )
        return snapshots

    def health_checks(self) -> list[ProviderHealth]:
        """Run health checks for all collectors."""
        return [collector.health_check() for collector in self._collectors.values()]

    def _run_collector(self, name: str) -> CollectorRunResult:
        collector = self._collectors.get(name)
        if collector is None:
            result = CollectorRunResult(
                provider=name,
                status=CollectorStatus.FAILED,
                errors=[f"Unknown collector: {name}"],
                finished_at=datetime.now(UTC),
            )
            return result

        logger.info("collector_started provider={}", name)
        result = collector.run()
        if result.status != CollectorStatus.FAILED:
            self._session.commit()
        else:
            self._session.rollback()

        self._status[name] = CollectorStatusSnapshot(
            provider=name,
            last_status=result.status,
            last_run_at=result.finished_at,
            rows_saved=result.rows_saved,
            rows_rejected=result.rows_rejected,
            duration_ms=result.duration_ms,
            errors=list(result.errors),
        )
        return result
