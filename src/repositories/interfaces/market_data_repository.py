"""Market data repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.collectors.base.models import MacroIndicatorRecord, NavRecord, PriceRecord
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.domain.read_models.nav_history import NavHistoryPoint
from src.domain.read_models.price_history import PriceHistoryPoint


class MarketDataRepository(ABC):
    """Persistence contract for imported market data."""

    @abstractmethod
    def save_nav(self, record: NavRecord, asset_id: UUID) -> bool:
        """Save a NAV record. Returns False when duplicate exists."""

    @abstractmethod
    def save_price(self, record: PriceRecord, asset_id: UUID) -> bool:
        """Save a price record. Returns False when duplicate exists."""

    @abstractmethod
    def save_macro(self, record: MacroIndicatorRecord) -> bool:
        """Save a macro indicator. Returns False when duplicate exists."""

    @abstractmethod
    def nav_exists(self, asset_id: UUID, nav_date: date) -> bool:
        """Return True when NAV already exists for asset and date."""

    @abstractmethod
    def price_exists(self, asset_id: UUID, price_date: date) -> bool:
        """Return True when price already exists for asset and date."""

    @abstractmethod
    def macro_exists(
        self, indicator_name: str, release_date: date, country: str
    ) -> bool:
        """Return True when macro record already exists."""

    @abstractmethod
    def get_nav_history(
        self,
        asset_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[NavHistoryPoint]:
        """Load NAV history for a fund ordered by date ascending."""

    @abstractmethod
    def get_latest_nav(self, asset_id: UUID) -> NavHistoryPoint | None:
        """Return the most recent NAV observation for a fund."""

    @abstractmethod
    def get_price_history(
        self,
        asset_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[PriceHistoryPoint]:
        """Load price history for a stock ordered by date ascending."""

    @abstractmethod
    def get_latest_price(self, asset_id: UUID) -> PriceHistoryPoint | None:
        """Return the most recent price observation for a stock."""

    @abstractmethod
    def get_macro_indicators(
        self,
        country: str = "PK",
        indicator_name: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[MacroIndicatorPoint]:
        """Load macro indicators ordered by release date ascending."""

    @abstractmethod
    def get_latest_macro(
        self,
        indicator_name: str,
        country: str = "PK",
    ) -> MacroIndicatorPoint | None:
        """Return the most recent macro observation for an indicator."""
