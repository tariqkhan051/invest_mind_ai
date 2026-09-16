"""SQLAlchemy market data repository."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.collectors.base.models import MacroIndicatorRecord, NavRecord, PriceRecord
from src.database.models.market_data import (
    MarketMacroIndicatorModel,
    NavHistoryModel,
    PriceHistoryModel,
)
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.domain.read_models.nav_history import NavHistoryPoint
from src.domain.read_models.price_history import PriceHistoryPoint
from src.repositories.interfaces.market_data_repository import MarketDataRepository


class SqlAlchemyMarketDataRepository(MarketDataRepository):
    """Persist imported NAV, price, and macro data."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save_nav(self, record: NavRecord, asset_id: UUID) -> bool:
        existing = self._session.scalars(
            select(NavHistoryModel).where(
                NavHistoryModel.asset_id == asset_id,
                NavHistoryModel.nav_date == record.nav_date,
            )
        ).first()
        if existing is not None:
            updated = False
            for field_name, value in (
                ("nav", record.nav),
                ("adjusted_nav", record.adjusted_nav),
                ("daily_return", record.daily_return),
                ("dividend", record.dividend),
                ("offer_price", record.offer_price),
                ("repurchase_price", record.repurchase_price),
                ("fytd_return", record.fytd_return),
                ("mtd_return", record.mtd_return),
                ("category", record.category),
                ("source", record.source),
            ):
                if value is None:
                    continue
                if getattr(existing, field_name) != value:
                    setattr(existing, field_name, value)
                    updated = True
            if updated:
                self._session.flush()
            # Existing dates count as duplicates even after refresh.
            return False

        model = NavHistoryModel(
            asset_id=asset_id,
            nav_date=record.nav_date,
            nav=record.nav,
            adjusted_nav=record.adjusted_nav,
            daily_return=record.daily_return,
            dividend=record.dividend,
            offer_price=record.offer_price,
            repurchase_price=record.repurchase_price,
            fytd_return=record.fytd_return,
            mtd_return=record.mtd_return,
            category=record.category,
            source=record.source,
            created_at=datetime.now(UTC),
        )
        self._session.add(model)
        self._session.flush()
        return True

    def save_price(self, record: PriceRecord, asset_id: UUID) -> bool:
        if self.price_exists(asset_id, record.price_date):
            return False
        model = PriceHistoryModel(
            asset_id=asset_id,
            price_date=record.price_date,
            open_price=record.open_price,
            high_price=record.high_price,
            low_price=record.low_price,
            close_price=record.close_price,
            adjusted_close=record.adjusted_close,
            volume=record.volume,
            source=record.source,
            created_at=datetime.now(UTC),
        )
        self._session.add(model)
        self._session.flush()
        return True

    def save_macro(self, record: MacroIndicatorRecord) -> bool:
        if self.macro_exists(
            record.indicator_name, record.release_date, record.country
        ):
            return False
        model = MarketMacroIndicatorModel(
            indicator_name=record.indicator_name,
            country=record.country,
            release_date=record.release_date,
            frequency=record.frequency,
            forecast_value=record.forecast_value,
            actual_value=record.actual_value,
            previous_value=record.previous_value,
            unit=record.unit,
            importance=record.importance,
            trend=record.trend,
            source=record.source,
            created_at=datetime.now(UTC),
        )
        self._session.add(model)
        self._session.flush()
        return True

    def nav_exists(self, asset_id: UUID, nav_date: date) -> bool:
        stmt = select(NavHistoryModel.id).where(
            NavHistoryModel.asset_id == asset_id,
            NavHistoryModel.nav_date == nav_date,
        )
        return self._session.scalar(stmt) is not None

    def price_exists(self, asset_id: UUID, price_date: date) -> bool:
        stmt = select(PriceHistoryModel.id).where(
            PriceHistoryModel.asset_id == asset_id,
            PriceHistoryModel.price_date == price_date,
        )
        return self._session.scalar(stmt) is not None

    def macro_exists(
        self,
        indicator_name: str,
        release_date: date,
        country: str,
    ) -> bool:
        stmt = select(MarketMacroIndicatorModel.id).where(
            MarketMacroIndicatorModel.indicator_name == indicator_name,
            MarketMacroIndicatorModel.release_date == release_date,
            MarketMacroIndicatorModel.country == country,
        )
        return self._session.scalar(stmt) is not None

    def get_nav_history(
        self,
        asset_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[NavHistoryPoint]:
        stmt = (
            select(NavHistoryModel)
            .where(NavHistoryModel.asset_id == asset_id)
            .order_by(NavHistoryModel.nav_date.asc())
        )
        if from_date is not None:
            stmt = stmt.where(NavHistoryModel.nav_date >= from_date)
        if to_date is not None:
            stmt = stmt.where(NavHistoryModel.nav_date <= to_date)

        return [
            NavHistoryPoint(
                nav_date=row.nav_date,
                nav=row.nav,
                daily_return=row.daily_return,
                offer_price=row.offer_price,
                repurchase_price=row.repurchase_price,
                fytd_return=row.fytd_return,
                mtd_return=row.mtd_return,
                category=row.category,
                source=row.source,
            )
            for row in self._session.scalars(stmt)
        ]

    def get_latest_nav(self, asset_id: UUID) -> NavHistoryPoint | None:
        stmt = (
            select(NavHistoryModel)
            .where(NavHistoryModel.asset_id == asset_id)
            .order_by(NavHistoryModel.nav_date.desc())
            .limit(1)
        )
        row = self._session.scalar(stmt)
        if row is None:
            return None
        return NavHistoryPoint(
            nav_date=row.nav_date,
            nav=row.nav,
            daily_return=row.daily_return,
            offer_price=row.offer_price,
            repurchase_price=row.repurchase_price,
            fytd_return=row.fytd_return,
            mtd_return=row.mtd_return,
            category=row.category,
            source=row.source,
        )

    def get_price_history(
        self,
        asset_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[PriceHistoryPoint]:
        stmt = (
            select(PriceHistoryModel)
            .where(PriceHistoryModel.asset_id == asset_id)
            .order_by(PriceHistoryModel.price_date.asc())
        )
        if from_date is not None:
            stmt = stmt.where(PriceHistoryModel.price_date >= from_date)
        if to_date is not None:
            stmt = stmt.where(PriceHistoryModel.price_date <= to_date)

        return [
            PriceHistoryPoint(
                price_date=row.price_date,
                close_price=row.close_price,
                open_price=row.open_price,
                high_price=row.high_price,
                low_price=row.low_price,
                adjusted_close=row.adjusted_close,
                volume=row.volume,
            )
            for row in self._session.scalars(stmt)
        ]

    def get_latest_price(self, asset_id: UUID) -> PriceHistoryPoint | None:
        stmt = (
            select(PriceHistoryModel)
            .where(PriceHistoryModel.asset_id == asset_id)
            .order_by(PriceHistoryModel.price_date.desc())
            .limit(1)
        )
        row = self._session.scalar(stmt)
        if row is None:
            return None
        return PriceHistoryPoint(
            price_date=row.price_date,
            close_price=row.close_price,
            open_price=row.open_price,
            high_price=row.high_price,
            low_price=row.low_price,
            adjusted_close=row.adjusted_close,
            volume=row.volume,
        )

    def get_macro_indicators(
        self,
        country: str = "PK",
        indicator_name: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[MacroIndicatorPoint]:
        stmt = (
            select(MarketMacroIndicatorModel)
            .where(MarketMacroIndicatorModel.country == country)
            .order_by(MarketMacroIndicatorModel.release_date.asc())
        )
        if indicator_name is not None:
            stmt = stmt.where(
                MarketMacroIndicatorModel.indicator_name == indicator_name
            )
        if from_date is not None:
            stmt = stmt.where(MarketMacroIndicatorModel.release_date >= from_date)
        if to_date is not None:
            stmt = stmt.where(MarketMacroIndicatorModel.release_date <= to_date)

        return [
            MacroIndicatorPoint(
                indicator_name=row.indicator_name,
                release_date=row.release_date,
                actual_value=row.actual_value,
                country=row.country,
                forecast_value=row.forecast_value,
                previous_value=row.previous_value,
                unit=row.unit,
                trend=row.trend,
                source=row.source,
            )
            for row in self._session.scalars(stmt)
        ]

    def get_latest_macro(
        self,
        indicator_name: str,
        country: str = "PK",
    ) -> MacroIndicatorPoint | None:
        stmt = (
            select(MarketMacroIndicatorModel)
            .where(
                MarketMacroIndicatorModel.indicator_name == indicator_name,
                MarketMacroIndicatorModel.country == country,
            )
            .order_by(MarketMacroIndicatorModel.release_date.desc())
            .limit(1)
        )
        row = self._session.scalar(stmt)
        if row is None:
            return None
        return MacroIndicatorPoint(
            indicator_name=row.indicator_name,
            release_date=row.release_date,
            actual_value=row.actual_value,
            country=row.country,
            forecast_value=row.forecast_value,
            previous_value=row.previous_value,
            unit=row.unit,
            trend=row.trend,
            source=row.source,
        )
