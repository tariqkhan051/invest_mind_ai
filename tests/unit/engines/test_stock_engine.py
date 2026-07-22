"""Unit tests for stock engine."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.asset import Asset
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType
from src.domain.read_models.price_history import PriceHistoryPoint
from src.engines.stock.engine import StockEngine
from src.engines.stock.models import (
    FundamentalMetrics,
    StockAnalysis,
    StockPerformanceMetrics,
    TechnicalIndicators,
)
from src.engines.stock.opportunity_detector import find_buy_opportunities
from src.engines.stock.scoring_engine import calculate_ai_score
from src.engines.stock.technical_calculator import calculate_technicals


def _analysis(
    symbol: str,
    yearly_return: Decimal,
    rsi: Decimal,
    pe: Decimal | None = None,
) -> StockAnalysis:
    asset_id = uuid4()
    return StockAnalysis(
        asset_id=asset_id,
        symbol=symbol,
        display_name=symbol,
        company_name=symbol,
        sector="Banking",
        industry="Banking",
        is_shariah=True,
        latest_price=Decimal("100"),
        latest_price_date=date(2026, 1, 1),
        performance=StockPerformanceMetrics(yearly_return=yearly_return),
        technicals=TechnicalIndicators(rsi_14=rsi),
        fundamentals=FundamentalMetrics(pe=pe),
        ai_score=calculate_ai_score(
            StockPerformanceMetrics(yearly_return=yearly_return),
            TechnicalIndicators(rsi_14=rsi),
            FundamentalMetrics(pe=pe),
        ),
    )


def test_calculate_ai_score_within_bounds() -> None:
    """AI score should stay between 0 and 100."""
    score = calculate_ai_score(
        StockPerformanceMetrics(yearly_return=Decimal("20")),
        TechnicalIndicators(rsi_14=Decimal("55"), momentum=Decimal("5")),
        FundamentalMetrics(pe=Decimal("10"), roe=Decimal("18")),
    )
    assert Decimal("0") <= score <= Decimal("100")


def test_calculate_technicals_computes_rsi() -> None:
    """Technical calculator should compute RSI for sufficient history."""
    history = [
        PriceHistoryPoint(
            price_date=date(2025, 1, 1) + timedelta(days=index),
            close_price=Decimal("100") + Decimal(index),
        )
        for index in range(30)
    ]
    technicals = calculate_technicals(history)
    assert technicals.rsi_14 is not None


def test_find_buy_opportunities_detects_oversold() -> None:
    """Opportunity detector should flag oversold RSI."""
    analyses = [_analysis("HBL", Decimal("10"), Decimal("30"))]
    opportunities = find_buy_opportunities(analyses)
    assert any(item.opportunity_type == "oversold" for item in opportunities)


def test_analyze_stock_with_history() -> None:
    """Engine should produce a complete analysis from price history."""
    asset = Asset(
        symbol="HBL",
        display_name="Habib Bank Limited",
        asset_type=AssetType.STOCK,
        exchange="PSX",
    )
    stock = Stock(
        asset_id=asset.id,
        asset=asset,
        company_name="Habib Bank Limited",
        industry="Banking",
        pe=Decimal("8.5"),
        roe=Decimal("20"),
    )
    history = [
        PriceHistoryPoint(price_date=date(2025, 1, 1), close_price=Decimal("100")),
        PriceHistoryPoint(price_date=date(2026, 1, 1), close_price=Decimal("120")),
    ]
    analysis = StockEngine().analyze_stock(stock, history)
    assert analysis.symbol == "HBL"
    assert analysis.ai_score is not None
    assert analysis.performance.yearly_return == Decimal("20")
