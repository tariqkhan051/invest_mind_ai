"""Unit tests for market intelligence engine."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from src.collectors.base.models import NewsRecord
from src.domain.enums import MarketRegime, NewsCategory, SentimentLabel
from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.domain.read_models.news_article import NewsArticle
from src.engines.market_intelligence.alert_generator import generate_alerts
from src.engines.market_intelligence.engine import MarketIntelligenceEngine
from src.engines.market_intelligence.regime_detector import detect_regime
from src.engines.market_intelligence.scoring_engine import calculate_market_score
from src.engines.market_intelligence.sentiment_analyzer import (
    analyze_sentiment,
    classify_news,
    summarize_sentiment,
)


def _article(sentiment: SentimentLabel, score: Decimal) -> NewsArticle:
    return NewsArticle(
        id=uuid4(),
        headline="Test headline",
        summary="Test summary",
        publisher="Test",
        publication_time=datetime(2026, 1, 1, tzinfo=UTC),
        url=f"https://example.com/{uuid4()}",
        country="PK",
        category=NewsCategory.ECONOMY,
        sentiment=sentiment,
        sentiment_score=score,
    )


def test_analyze_sentiment_positive() -> None:
    """Positive keywords should produce positive sentiment."""
    record = NewsRecord(
        headline="Pakistan economy shows strong growth rally",
        url="https://example.com/growth",
        publication_time=datetime(2026, 1, 1, tzinfo=UTC),
        source="test",
    )
    sentiment, score = analyze_sentiment(record)
    assert sentiment == SentimentLabel.POSITIVE
    assert score > Decimal("0")


def test_classify_news_banking() -> None:
    """Banking keywords should classify as banking news."""
    record = NewsRecord(
        headline="SBP keeps banking sector rates unchanged",
        url="https://example.com/banking",
        publication_time=datetime(2026, 1, 1, tzinfo=UTC),
        source="test",
    )
    assert classify_news(record) == NewsCategory.BANKING


def test_detect_high_inflation_regime() -> None:
    """High inflation macro data should trigger inflation regime."""
    indicators = [
        MacroIndicatorPoint(
            indicator_name="Inflation",
            release_date=date(2026, 1, 1),
            actual_value=Decimal("22"),
            trend="rising",
        )
    ]
    sentiment = summarize_sentiment([])
    regime = detect_regime(indicators, sentiment)
    assert regime.regime == MarketRegime.HIGH_INFLATION


def test_calculate_market_score_within_bounds() -> None:
    """Market score should stay between 0 and 100."""
    indicators = [
        MacroIndicatorPoint(
            indicator_name="Policy Rate",
            release_date=date(2026, 1, 1),
            actual_value=Decimal("12"),
            trend="stable",
        )
    ]
    sentiment = summarize_sentiment([_article(SentimentLabel.POSITIVE, Decimal("20"))])
    from src.engines.market_intelligence.models import RegimeAssessment

    regime = RegimeAssessment(
        regime=MarketRegime.BULL,
        confidence=Decimal("0.7"),
        explanation="test",
    )
    score = calculate_market_score(indicators, sentiment, regime)
    assert Decimal("0") <= score.overall_score <= Decimal("100")


def test_generate_alerts_for_rate_change() -> None:
    """Significant rate changes should generate alerts."""
    indicators = [
        MacroIndicatorPoint(
            indicator_name="Policy Rate",
            release_date=date(2026, 1, 1),
            actual_value=Decimal("16"),
            previous_value=Decimal("14"),
        )
    ]
    alerts = generate_alerts(indicators)
    assert any(alert.alert_type == "interest_rate_change" for alert in alerts)


def test_build_summary() -> None:
    """Engine should produce a complete market summary."""
    indicators = [
        MacroIndicatorPoint(
            indicator_name="Inflation",
            release_date=date(2026, 1, 1),
            actual_value=Decimal("10"),
            trend="falling",
        )
    ]
    news = [_article(SentimentLabel.POSITIVE, Decimal("30"))]
    summary = MarketIntelligenceEngine().build_summary(indicators, news)
    assert summary.score.overall_score is not None
    assert summary.regime.regime is not None
    assert len(summary.latest_news) == 1
