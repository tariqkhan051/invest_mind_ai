"""Mutual fund application service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.core.exceptions import FundNotFoundError
from src.core.logging import get_logger
from src.domain.entities.mutual_fund import MutualFund
from src.domain.enums import AssetType
from src.domain.read_models.nav_history import NavHistoryPoint
from src.engines.mutual_fund.engine import MutualFundEngine
from src.engines.mutual_fund.models import (
    FundAnalysis,
    FundComparison,
    FundRanking,
    SwitchOpportunity,
)
from src.repositories.interfaces.asset_repository import AssetRepository
from src.repositories.interfaces.market_data_repository import MarketDataRepository

logger = get_logger("services.mutual_fund")


@dataclass
class FundCategorySummary:
    """Summary metrics for a fund category."""

    category: str
    fund_count: int
    average_yearly_return: float | None
    average_volatility: float | None
    top_performer: str | None


class MutualFundService:
    """Mutual fund use cases coordinating persistence and analysis."""

    def __init__(
        self,
        asset_repository: AssetRepository,
        market_data_repository: MarketDataRepository,
        engine: MutualFundEngine | None = None,
    ) -> None:
        self._asset_repository = asset_repository
        self._market_data_repository = market_data_repository
        self._engine = engine or MutualFundEngine()

    def list_funds(
        self,
        shariah_only: bool = False,
        category: AssetType | None = None,
    ) -> list[FundAnalysis]:
        """List and analyze all mutual funds."""
        mutual_funds = self._asset_repository.list_mutual_funds(
            shariah_only=shariah_only,
            asset_type=category,
        )
        return [self._analyze_mutual_fund(fund) for fund in mutual_funds]

    def get_fund(self, asset_id: UUID) -> FundAnalysis:
        """Get analyzed details for one fund."""
        mutual_fund = self._asset_repository.get_mutual_fund(asset_id)
        if mutual_fund is None:
            raise FundNotFoundError(f"Mutual fund {asset_id} not found.")
        return self._analyze_mutual_fund(mutual_fund)

    def get_nav_history(
        self,
        asset_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[NavHistoryPoint]:
        """Return NAV history for a fund."""
        mutual_fund = self._asset_repository.get_mutual_fund(asset_id)
        if mutual_fund is None:
            raise FundNotFoundError(f"Mutual fund {asset_id} not found.")
        return self._market_data_repository.get_nav_history(
            asset_id,
            from_date=from_date,
            to_date=to_date,
        )

    def get_rankings(
        self,
        shariah_only: bool = False,
        category: AssetType | None = None,
        limit: int | None = None,
    ) -> list[FundRanking]:
        """Return ranked funds."""
        analyses = self.list_funds(shariah_only=shariah_only, category=category)
        return self._engine.rank_funds(analyses, limit=limit)

    def compare_funds(self, asset_ids: list[UUID]) -> FundComparison:
        """Compare multiple funds side by side."""
        if not asset_ids:
            raise FundNotFoundError("At least one fund id is required for comparison.")
        analyses = [self.get_fund(asset_id) for asset_id in asset_ids]
        return self._engine.compare_funds(analyses)

    def get_switch_opportunities(
        self,
        shariah_only: bool = False,
        category: AssetType | None = None,
    ) -> list[SwitchOpportunity]:
        """Detect potential fund switch opportunities."""
        analyses = self.list_funds(shariah_only=shariah_only, category=category)
        return self._engine.find_switch_opportunities(analyses)

    def get_categories(
        self,
        shariah_only: bool = False,
    ) -> list[FundCategorySummary]:
        """Return category-level summaries."""
        analyses = self.list_funds(shariah_only=shariah_only)
        grouped = self._engine.group_by_category(analyses)
        summaries: list[FundCategorySummary] = []
        for category, items in sorted(grouped.items()):
            yearly_returns = [
                float(item.performance.yearly_return)
                for item in items
                if item.performance.yearly_return is not None
            ]
            volatilities = [
                float(item.risk.volatility)
                for item in items
                if item.risk.volatility is not None
            ]
            top = max(
                items,
                key=lambda item: item.ai_score or item.performance.yearly_return or 0,
                default=None,
            )
            summaries.append(
                FundCategorySummary(
                    category=category,
                    fund_count=len(items),
                    average_yearly_return=(
                        sum(yearly_returns) / len(yearly_returns)
                        if yearly_returns
                        else None
                    ),
                    average_volatility=(
                        sum(volatilities) / len(volatilities) if volatilities else None
                    ),
                    top_performer=top.symbol if top else None,
                )
            )
        return summaries

    def _analyze_mutual_fund(self, mutual_fund: MutualFund) -> FundAnalysis:
        history = self._market_data_repository.get_nav_history(mutual_fund.asset_id)
        return self._engine.analyze_fund(mutual_fund, history)
