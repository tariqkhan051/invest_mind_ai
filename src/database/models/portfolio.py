"""Portfolio ORM models — docs/05_DATABASE_DESIGN.md Part 2."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
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
from src.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PortfolioModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for portfolio table."""

    __tablename__ = "portfolio"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_portfolio_owner_name"),
        Index("ix_portfolio_owner_id", "owner_id"),
        Index("ix_portfolio_status", "status"),
    )

    owner_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PKR")
    risk_profile: Mapped[str] = mapped_column(String(50), nullable=False)
    investment_preference: Mapped[str] = mapped_column(String(50), nullable=False)
    investment_objective: Mapped[str] = mapped_column(String(50), nullable=False)
    investment_horizon: Mapped[str] = mapped_column(String(50), nullable=False)
    monthly_sip: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    holdings: Mapped[list[HoldingModel]] = relationship(back_populates="portfolio")
    transactions: Mapped[list[TransactionModel]] = relationship(
        back_populates="portfolio"
    )
    snapshots: Mapped[list[PortfolioSnapshotModel]] = relationship(
        back_populates="portfolio"
    )
    goals: Mapped[list[InvestmentGoalModel]] = relationship(back_populates="portfolio")


class HoldingModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for holding table."""

    __tablename__ = "holding"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "asset_id", name="uq_holding_portfolio_asset"),
        Index("ix_holding_portfolio_id", "portfolio_id"),
        Index("ix_holding_asset_id", "asset_id"),
        Index("ix_holding_status", "status"),
    )

    portfolio_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("portfolio.id"), nullable=False
    )
    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id"), nullable=False
    )
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(19, 6), nullable=False)
    average_cost: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    current_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    unrealized_gain: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    realized_gain: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    allocation_percentage: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PKR")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    last_price_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    portfolio: Mapped[PortfolioModel] = relationship(back_populates="holdings")


class TransactionModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for transaction table."""

    __tablename__ = "transaction"
    __table_args__ = (
        Index("ix_transaction_portfolio_id", "portfolio_id"),
        Index("ix_transaction_asset_id", "asset_id"),
        Index("ix_transaction_date", "transaction_date"),
        Index("ix_transaction_status", "status"),
        Index("ix_transaction_portfolio_date", "portfolio_id", "transaction_date"),
    )

    portfolio_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("portfolio.id"), nullable=False
    )
    holding_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("holding.id")
    )
    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("asset.id"), nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    units: Mapped[Decimal] = mapped_column(Numeric(19, 6), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    fees: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False, default=0)
    taxes: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False, default=0)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(100))
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    settlement_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    portfolio: Mapped[PortfolioModel] = relationship(back_populates="transactions")


class PortfolioSnapshotModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for portfolio_snapshot table."""

    __tablename__ = "portfolio_snapshot"
    __table_args__ = (
        UniqueConstraint(
            "portfolio_id", "snapshot_date", name="uq_snapshot_portfolio_date"
        ),
        Index("ix_snapshot_portfolio_id", "portfolio_id"),
        Index("ix_snapshot_date", "snapshot_date"),
    )

    portfolio_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("portfolio.id"), nullable=False
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    investment_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    cash_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    daily_return: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    monthly_return: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    yearly_return: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    xirr: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    cagr: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    volatility: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    drawdown: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    sharpe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    sortino_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    allocation_json: Mapped[dict[str, float] | None] = mapped_column(JSON)
    sector_allocation_json: Mapped[dict[str, float] | None] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    portfolio: Mapped[PortfolioModel] = relationship(back_populates="snapshots")


class InvestmentGoalModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for investment_goal table."""

    __tablename__ = "investment_goal"
    __table_args__ = (
        Index("ix_goal_portfolio_id", "portfolio_id"),
        Index("ix_goal_status", "status"),
    )

    portfolio_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("portfolio.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date)
    monthly_contribution: Mapped[Decimal] = mapped_column(
        Numeric(19, 4), nullable=False, default=0
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    risk_preference: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    portfolio: Mapped[PortfolioModel] = relationship(back_populates="goals")
