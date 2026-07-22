"""Market intelligence engine orchestration."""

from __future__ import annotations

from collections import Counter
from datetime import date

from src.domain.read_models.macro_indicator import MacroIndicatorPoint
from src.domain.read_models.news_article import NewsArticle
from src.engines.market_intelligence.alert_generator import generate_alerts
from src.engines.market_intelligence.models import (
    EconomySnapshot,
    InvestmentSignal,
    MarketAlert,
    MarketScore,
    MarketSummary,
    RegimeAssessment,
)
from src.engines.market_intelligence.regime_detector import detect_regime
from src.engines.market_intelligence.scoring_engine import calculate_market_score
from src.engines.market_intelligence.sentiment_analyzer import summarize_sentiment
from src.engines.market_intelligence.signal_generator import generate_signals


class MarketIntelligenceEngine:
    """Analyze macro data and news to produce market intelligence."""

    def build_summary(
        self,
        indicators: list[MacroIndicatorPoint],
        news: list[NewsArticle],
        as_of: date | None = None,
    ) -> MarketSummary:
        """Produce a complete market intelligence summary."""
        latest_indicators = self.latest_indicators(indicators)
        sentiment = summarize_sentiment(news)
        regime = detect_regime(latest_indicators, sentiment)
        score = calculate_market_score(
            latest_indicators,
            sentiment,
            regime,
            as_of=as_of,
        )
        signals = generate_signals(regime)
        alerts = generate_alerts(latest_indicators)
        category_counts = Counter(article.category for article in news)

        return MarketSummary(
            score=score,
            regime=regime,
            sentiment=sentiment,
            signals=signals,
            alerts=alerts,
            latest_news=news[:10],
            economy=EconomySnapshot(indicators=latest_indicators),
            news_by_category=dict(category_counts),
        )

    def calculate_score(
        self,
        indicators: list[MacroIndicatorPoint],
        news: list[NewsArticle],
        as_of: date | None = None,
    ) -> MarketScore:
        """Calculate the market intelligence score only."""
        latest_indicators = self.latest_indicators(indicators)
        sentiment = summarize_sentiment(news)
        regime = detect_regime(latest_indicators, sentiment)
        return calculate_market_score(
            latest_indicators,
            sentiment,
            regime,
            as_of=as_of,
        )

    def detect_regime(
        self,
        indicators: list[MacroIndicatorPoint],
        news: list[NewsArticle],
    ) -> RegimeAssessment:
        """Detect the current market regime."""
        latest_indicators = self.latest_indicators(indicators)
        sentiment = summarize_sentiment(news)
        return detect_regime(latest_indicators, sentiment)

    def generate_signals(self, regime: RegimeAssessment) -> list[InvestmentSignal]:
        """Generate investment signals for a regime."""
        return generate_signals(regime)

    def generate_alerts(
        self,
        indicators: list[MacroIndicatorPoint],
    ) -> list[MarketAlert]:
        """Generate market alerts from macro indicators."""
        return generate_alerts(self.latest_indicators(indicators))

    @staticmethod
    def latest_indicators(
        indicators: list[MacroIndicatorPoint],
    ) -> list[MacroIndicatorPoint]:
        """Return the latest observation per indicator name."""
        latest: dict[str, MacroIndicatorPoint] = {}
        for indicator in sorted(indicators, key=lambda item: item.release_date):
            latest[indicator.indicator_name] = indicator
        return list(latest.values())

    @staticmethod
    def _latest_indicators(
        indicators: list[MacroIndicatorPoint],
    ) -> list[MacroIndicatorPoint]:
        return MarketIntelligenceEngine.latest_indicators(indicators)
