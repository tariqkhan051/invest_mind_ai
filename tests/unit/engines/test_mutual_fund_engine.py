"""Unit tests for mutual fund engine scoring and rankings."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.enums import AssetType
from src.domain.read_models.nav_history import NavHistoryPoint
from src.engines.mutual_fund.engine import MutualFundEngine
from src.engines.mutual_fund.models import (
    FundAnalysis,
    FundPerformanceMetrics,
    FundRiskMetrics,
)
from src.engines.mutual_fund.scoring_engine import calculate_ai_score
from src.engines.mutual_fund.switch_analyzer import find_switch_opportunities


def _analysis(
    symbol: str,
    yearly_return: Decimal,
    volatility: Decimal,
    asset_type: str = AssetType.EQUITY_FUND.value,
) -> FundAnalysis:
    asset_id = uuid4()
    return FundAnalysis(
        asset_id=asset_id,
        symbol=symbol,
        display_name=symbol,
        asset_type=asset_type,
        is_shariah=True,
        management_company="Test AMC",
        expense_ratio=Decimal("1.5"),
        aum=Decimal("5000000000"),
        latest_nav=Decimal("100"),
        latest_nav_date=date(2026, 1, 1),
        performance=FundPerformanceMetrics(yearly_return=yearly_return),
        risk=FundRiskMetrics(volatility=volatility),
        ai_score=calculate_ai_score(
            FundPerformanceMetrics(yearly_return=yearly_return),
            FundRiskMetrics(volatility=volatility),
            Decimal("5000000000"),
            Decimal("1.5"),
        ),
    )


def test_calculate_ai_score_within_bounds() -> None:
    """AI score should stay between 0 and 100."""
    score = calculate_ai_score(
        FundPerformanceMetrics(yearly_return=Decimal("20")),
        FundRiskMetrics(volatility=Decimal("5")),
        Decimal("20000000000"),
        Decimal("1.2"),
    )
    assert Decimal("0") <= score <= Decimal("100")


def test_rank_funds_orders_by_score() -> None:
    """Higher scoring funds should rank first."""
    engine = MutualFundEngine()
    analyses = [
        _analysis("LOW", Decimal("5"), Decimal("10")),
        _analysis("HIGH", Decimal("25"), Decimal("8")),
    ]
    rankings = engine.rank_funds(analyses)
    assert rankings[0].symbol == "HIGH"
    assert rankings[1].symbol == "LOW"


def test_find_switch_opportunities_detects_gap() -> None:
    """Switch analyzer should flag underperformers in the same category."""
    analyses = [
        _analysis("BEST", Decimal("20"), Decimal("10")),
        _analysis("LAG", Decimal("10"), Decimal("11")),
    ]
    opportunities = find_switch_opportunities(analyses)
    assert len(opportunities) == 1
    assert opportunities[0].from_symbol == "LAG"
    assert opportunities[0].to_symbol == "BEST"


def test_analyze_fund_with_history() -> None:
    """Engine should produce a complete analysis from NAV history."""
    asset = Asset(
        symbol="MIF",
        display_name="Meezan Islamic Fund",
        asset_type=AssetType.MUTUAL_FUND,
    )
    mutual_fund = MutualFund(
        asset_id=asset.id,
        asset=asset,
        management_company="Meezan",
        expense_ratio=Decimal("1.8"),
        aum=Decimal("10000000000"),
    )
    history = [
        NavHistoryPoint(nav_date=date(2025, 1, 1), nav=Decimal("100")),
        NavHistoryPoint(nav_date=date(2026, 1, 1), nav=Decimal("115")),
    ]
    analysis = MutualFundEngine().analyze_fund(mutual_fund, history)
    assert analysis.symbol == "MIF"
    assert analysis.ai_score is not None
    assert analysis.performance.since_inception_return == Decimal("15")
