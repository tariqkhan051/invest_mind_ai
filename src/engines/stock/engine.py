"""Stock engine orchestration."""

from __future__ import annotations

from datetime import date

from src.domain.entities.stock import Stock
from src.domain.read_models.price_history import PriceHistoryPoint
from src.engines.stock.comparison_engine import compare_stocks
from src.engines.stock.models import (
    BuyOpportunity,
    FundamentalMetrics,
    StockAnalysis,
    StockComparison,
    StockRanking,
)
from src.engines.stock.opportunity_detector import find_buy_opportunities
from src.engines.stock.performance_calculator import calculate_performance
from src.engines.stock.ranking_engine import rank_stocks
from src.engines.stock.scoring_engine import calculate_ai_score
from src.engines.stock.technical_calculator import calculate_technicals


class StockEngine:
    """Analyze PSX stocks from price history and metadata."""

    def analyze_stock(
        self,
        stock: Stock,
        history: list[PriceHistoryPoint],
        sector_name: str | None = None,
        as_of: date | None = None,
    ) -> StockAnalysis:
        """Produce a complete analysis for one stock."""
        performance = calculate_performance(history, as_of=as_of)
        technicals = calculate_technicals(history)
        fundamentals = FundamentalMetrics(
            eps=stock.eps,
            pe=stock.pe,
            pbv=stock.pbv,
            roe=stock.roe,
            roa=stock.roa,
            debt_ratio=stock.debt_ratio,
            dividend_yield=stock.dividend_yield,
            market_cap=stock.market_cap,
        )
        latest = history[-1] if history else None

        analysis = StockAnalysis(
            asset_id=stock.asset_id,
            symbol=stock.asset.symbol,
            display_name=stock.asset.display_name,
            company_name=stock.company_name,
            sector=sector_name or stock.industry,
            industry=stock.industry,
            is_shariah=stock.asset.is_shariah,
            latest_price=latest.close_price if latest else None,
            latest_price_date=latest.price_date if latest else None,
            performance=performance,
            technicals=technicals,
            fundamentals=fundamentals,
        )
        analysis.ai_score = calculate_ai_score(performance, technicals, fundamentals)
        return analysis

    def rank_stocks(
        self,
        analyses: list[StockAnalysis],
        limit: int | None = None,
    ) -> list[StockRanking]:
        """Rank analyzed stocks."""
        return rank_stocks(analyses, limit=limit)

    def compare_stocks(self, analyses: list[StockAnalysis]) -> StockComparison:
        """Compare multiple analyzed stocks."""
        return compare_stocks(analyses)

    def find_buy_opportunities(
        self,
        analyses: list[StockAnalysis],
    ) -> list[BuyOpportunity]:
        """Detect buy opportunities across analyzed stocks."""
        return find_buy_opportunities(analyses)
