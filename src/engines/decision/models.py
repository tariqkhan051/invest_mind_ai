"""AI decision engine data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from src.domain.enums import RecommendationType, RiskLevel
from src.engines.market_intelligence.models import MarketSummary
from src.engines.mutual_fund.models import FundAnalysis, SwitchOpportunity
from src.engines.stock.models import BuyOpportunity, StockAnalysis
from src.services.portfolio_service import PortfolioSummary


@dataclass
class OpportunityCandidate:
    """Scored investment opportunity before recommendation creation."""

    recommendation_type: RecommendationType
    score: Decimal
    priority: int
    reason: str
    asset_id: UUID | None = None
    from_asset_id: UUID | None = None
    to_asset_id: UUID | None = None
    symbol: str | None = None
    from_symbol: str | None = None
    to_symbol: str | None = None
    recommended_amount: Decimal | None = None
    expected_return: Decimal | None = None
    expected_risk: RiskLevel = RiskLevel.MODERATE
    evidence: dict[str, str] = field(default_factory=dict)


@dataclass
class DecisionContext:
    """Inputs gathered for recommendation generation."""

    portfolio: PortfolioSummary
    market: MarketSummary
    funds: list[FundAnalysis]
    stocks: list[StockAnalysis]
    switch_opportunities: list[SwitchOpportunity]
    buy_opportunities: list[BuyOpportunity]
    monthly_investment: Decimal
    shariah_only: bool = True
