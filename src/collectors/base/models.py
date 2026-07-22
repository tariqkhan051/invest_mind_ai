"""Collector DTOs and result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class CollectorStatus(StrEnum):
    """Execution status for a collector run."""

    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DEGRADED = "degraded"


@dataclass(frozen=True, slots=True)
class NavRecord:
    """Normalized NAV record from any provider."""

    symbol: str
    nav_date: date
    nav: Decimal
    source: str
    adjusted_nav: Decimal | None = None
    daily_return: Decimal | None = None
    dividend: Decimal | None = None


@dataclass(frozen=True, slots=True)
class PriceRecord:
    """Normalized stock price record from any provider."""

    symbol: str
    price_date: date
    close_price: Decimal
    source: str
    open_price: Decimal | None = None
    high_price: Decimal | None = None
    low_price: Decimal | None = None
    adjusted_close: Decimal | None = None
    volume: Decimal | None = None


@dataclass(frozen=True, slots=True)
class MacroIndicatorRecord:
    """Normalized macroeconomic indicator record."""

    indicator_name: str
    release_date: date
    actual_value: Decimal
    source: str
    country: str = "PK"
    frequency: str | None = None
    forecast_value: Decimal | None = None
    previous_value: Decimal | None = None
    unit: str | None = None
    importance: str | None = None
    trend: str | None = None


@dataclass(frozen=True, slots=True)
class NewsRecord:
    """Normalized news article from any provider."""

    headline: str
    url: str
    publication_time: datetime
    source: str
    summary: str | None = None
    publisher: str | None = None
    country: str = "PK"
    language: str = "en"


@dataclass
class CollectorRunResult:
    """Outcome of a collector execution."""

    provider: str
    status: CollectorStatus
    rows_collected: int = 0
    rows_saved: int = 0
    rows_rejected: int = 0
    rows_duplicates: int = 0
    duration_ms: float = 0.0
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None


@dataclass
class ProviderHealth:
    """Health status for an external data provider."""

    provider: str
    healthy: bool
    message: str
    checked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SavedNavRecord:
    """Persisted NAV record reference."""

    asset_id: UUID
    nav_date: date
    nav: Decimal
