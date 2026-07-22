"""Portfolio snapshot entity for historical state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class PortfolioSnapshot:
    """Portfolio state captured at a point in time."""

    id: UUID = field(default_factory=uuid4)
    portfolio_id: UUID = field(default_factory=uuid4)
    snapshot_date: date = field(default_factory=date.today)
    total_value: Decimal = Decimal("0")
    investment_value: Decimal = Decimal("0")
    cash_value: Decimal = Decimal("0")
    daily_return: Decimal | None = None
    monthly_return: Decimal | None = None
    yearly_return: Decimal | None = None
    xirr: Decimal | None = None
    cagr: Decimal | None = None
    volatility: Decimal | None = None
    drawdown: Decimal | None = None
    sharpe_ratio: Decimal | None = None
    sortino_ratio: Decimal | None = None
    allocation_json: dict[str, Decimal] | None = None
    sector_allocation_json: dict[str, Decimal] | None = None
    notes: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
