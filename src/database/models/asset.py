"""Asset ORM models — docs/05_DATABASE_DESIGN.md Part 3."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from src.database.base import Base
from src.database.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class FundCategoryModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for fund_category reference table."""

    __tablename__ = "fund_category"
    __table_args__ = (UniqueConstraint("name", name="uq_fund_category_name"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str | None] = mapped_column(String(50))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class SectorModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for sector reference table."""

    __tablename__ = "sector"
    __table_args__ = (UniqueConstraint("name", name="uq_sector_name"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str | None] = mapped_column(String(50))
    cyclical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    interest_rate_sensitive: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    inflation_sensitive: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )


class BenchmarkModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for benchmark reference table."""

    __tablename__ = "benchmark"
    __table_args__ = (UniqueConstraint("name", name="uq_benchmark_name"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    benchmark_type: Mapped[str | None] = mapped_column(String(50))
    provider: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PKR")


class AssetModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """ORM model for asset table."""

    __tablename__ = "asset"
    __table_args__ = (
        UniqueConstraint("symbol", name="uq_asset_symbol"),
        Index("ix_asset_type", "asset_type"),
        Index("ix_asset_exchange", "exchange"),
        Index("ix_asset_status", "status"),
        Index("ix_asset_is_shariah", "is_shariah"),
    )

    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100))
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PKR")
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="PK")
    exchange: Mapped[str | None] = mapped_column(String(50))
    is_shariah: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    launch_date: Mapped[date | None] = mapped_column(Date)
    provider: Mapped[str | None] = mapped_column(String(100))
    metadata_json: Mapped[dict[str, str] | None] = mapped_column(JSON)

    mutual_fund: Mapped[MutualFundModel | None] = relationship(
        back_populates="asset", uselist=False
    )
    stock: Mapped[StockModel | None] = relationship(
        back_populates="asset", uselist=False
    )


class MutualFundModel(Base):
    """ORM model for mutual_fund table."""

    __tablename__ = "mutual_fund"
    __table_args__ = (
        Index("ix_mutual_fund_category", "fund_category_id"),
        Index("ix_mutual_fund_benchmark", "benchmark_id"),
    )

    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id"), primary_key=True
    )
    management_company: Mapped[str | None] = mapped_column(String(255))
    fund_category_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("fund_category.id")
    )
    benchmark_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("benchmark.id")
    )
    expense_ratio: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    front_load: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    back_load: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    management_fee: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    minimum_investment: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    minimum_sip: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    aum: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    cash_percentage: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    equity_percentage: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    debt_percentage: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    dividend_policy: Mapped[str | None] = mapped_column(String(50))
    dividend_frequency: Mapped[str | None] = mapped_column(String(50))
    website: Mapped[str | None] = mapped_column(String(500))
    factsheet_url: Mapped[str | None] = mapped_column(String(500))
    prospectus_url: Mapped[str | None] = mapped_column(String(500))
    last_nav_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    asset: Mapped[AssetModel] = relationship(back_populates="mutual_fund")


class StockModel(Base):
    """ORM model for stock table."""

    __tablename__ = "stock"
    __table_args__ = (
        Index("ix_stock_sector", "sector_id"),
        Index("ix_stock_industry", "industry"),
        Index("ix_stock_market_cap", "market_cap"),
    )

    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id"), primary_key=True
    )
    isin: Mapped[str | None] = mapped_column(String(20))
    company_name: Mapped[str | None] = mapped_column(String(255))
    sector_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("sector.id")
    )
    industry: Mapped[str | None] = mapped_column(String(100))
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    free_float: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    shares_outstanding: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    eps: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    pe: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    pbv: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    roe: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    roa: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    debt_ratio: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    dividend_yield: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    last_financial_update: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    asset: Mapped[AssetModel] = relationship(back_populates="stock")
