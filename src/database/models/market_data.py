"""Market data ORM models — NAV and price history."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from src.database.base import Base
from src.database.mixins import UUIDPrimaryKeyMixin


class NavHistoryModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for nav_history table."""

    __tablename__ = "nav_history"
    __table_args__ = (
        UniqueConstraint("asset_id", "nav_date", name="uq_nav_asset_date"),
        Index("ix_nav_asset_id", "asset_id"),
        Index("ix_nav_date", "nav_date"),
    )

    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id"), nullable=False
    )
    nav_date: Mapped[date] = mapped_column(Date, nullable=False)
    nav: Mapped[Decimal] = mapped_column(Numeric(19, 6), nullable=False)
    adjusted_nav: Mapped[Decimal | None] = mapped_column(Numeric(19, 6))
    daily_return: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    dividend: Mapped[Decimal | None] = mapped_column(Numeric(19, 6))
    source: Mapped[str | None] = mapped_column(String(100))
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class PriceHistoryModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for price_history table."""

    __tablename__ = "price_history"
    __table_args__ = (
        UniqueConstraint("asset_id", "price_date", name="uq_price_asset_date"),
        Index("ix_price_asset_id", "asset_id"),
        Index("ix_price_date", "price_date"),
    )

    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id"), nullable=False
    )
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    high_price: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    low_price: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    close_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    adjusted_close: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    volume: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    source: Mapped[str | None] = mapped_column(String(100))
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class MarketMacroIndicatorModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for market_macro_indicator table."""

    __tablename__ = "market_macro_indicator"
    __table_args__ = (
        UniqueConstraint(
            "indicator_name",
            "release_date",
            "country",
            name="uq_macro_indicator_date_country",
        ),
        Index("ix_macro_indicator_name", "indicator_name"),
        Index("ix_macro_release_date", "release_date"),
        Index("ix_macro_country", "country"),
    )

    indicator_name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="PK")
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    frequency: Mapped[str | None] = mapped_column(String(50))
    forecast_value: Mapped[Decimal | None] = mapped_column(Numeric(19, 6))
    actual_value: Mapped[Decimal] = mapped_column(Numeric(19, 6), nullable=False)
    previous_value: Mapped[Decimal | None] = mapped_column(Numeric(19, 6))
    unit: Mapped[str | None] = mapped_column(String(50))
    importance: Mapped[str | None] = mapped_column(String(50))
    trend: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class MarketNewsModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for market_news table."""

    __tablename__ = "market_news"
    __table_args__ = (
        UniqueConstraint("url", name="uq_market_news_url"),
        Index("ix_market_news_publication_time", "publication_time"),
        Index("ix_market_news_category", "category"),
        Index("ix_market_news_country", "country"),
    )

    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    publisher: Mapped[str | None] = mapped_column(String(255))
    publication_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="PK")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    sentiment: Mapped[str] = mapped_column(
        String(20), nullable=False, default="neutral"
    )
    sentiment_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0")
    )
    source: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
