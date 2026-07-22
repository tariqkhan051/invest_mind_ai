"""Rule-based news sentiment and classification."""

from __future__ import annotations

from decimal import Decimal

from src.collectors.base.models import NewsRecord
from src.domain.enums import NewsCategory, SentimentLabel
from src.domain.read_models.news_article import NewsArticle
from src.engines.market_intelligence.models import SentimentSummary

POSITIVE_KEYWORDS = (
    "growth",
    "surge",
    "rally",
    "gain",
    "profit",
    "upgrade",
    "bullish",
    "recovery",
    "expansion",
)
NEGATIVE_KEYWORDS = (
    "decline",
    "crash",
    "loss",
    "downgrade",
    "bearish",
    "crisis",
    "inflation",
    "debt",
    "default",
    "recession",
)
CATEGORY_KEYWORDS: dict[NewsCategory, tuple[str, ...]] = {
    NewsCategory.BANKING: ("bank", "banking", "sbp", "interest rate"),
    NewsCategory.ENERGY: ("oil", "energy", "gas", "petroleum"),
    NewsCategory.TECHNOLOGY: ("tech", "software", "digital"),
    NewsCategory.MUTUAL_FUNDS: ("mutual fund", "nav", "asset management"),
    NewsCategory.CORPORATE_EARNINGS: ("earnings", "profit", "dividend"),
    NewsCategory.POLITICS: ("government", "policy", "election", "imf"),
    NewsCategory.GLOBAL_MARKETS: ("global", "fed", "china", "us market"),
    NewsCategory.REGULATIONS: ("regulation", "secp", "compliance"),
    NewsCategory.ECONOMY: ("gdp", "inflation", "economy", "fiscal"),
}


def classify_news(record: NewsRecord) -> NewsCategory:
    """Classify a news article into a category."""
    text = f"{record.headline} {record.summary or ''}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return NewsCategory.GENERAL


def analyze_sentiment(record: NewsRecord) -> tuple[SentimentLabel, Decimal]:
    """Assign sentiment label and score to a news article."""
    text = f"{record.headline} {record.summary or ''}".lower()
    positive_hits = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text)
    negative_hits = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text)

    if positive_hits > negative_hits:
        score = Decimal(str(min(100, 50 + positive_hits * 10)))
        return SentimentLabel.POSITIVE, score
    if negative_hits > positive_hits:
        score = Decimal(str(max(-100, -50 - negative_hits * 10)))
        return SentimentLabel.NEGATIVE, score
    return SentimentLabel.NEUTRAL, Decimal("0")


def summarize_sentiment(articles: list[NewsArticle]) -> SentimentSummary:
    """Aggregate sentiment across news articles."""
    if not articles:
        return SentimentSummary(
            average_score=Decimal("0"),
            positive_count=0,
            neutral_count=0,
            negative_count=0,
            dominant_sentiment=SentimentLabel.NEUTRAL,
        )

    positive = sum(1 for item in articles if item.sentiment == SentimentLabel.POSITIVE)
    neutral = sum(1 for item in articles if item.sentiment == SentimentLabel.NEUTRAL)
    negative = sum(1 for item in articles if item.sentiment == SentimentLabel.NEGATIVE)
    average = sum(
        (item.sentiment_score for item in articles),
        Decimal("0"),
    ) / Decimal(len(articles))

    counts = {
        SentimentLabel.POSITIVE: positive,
        SentimentLabel.NEUTRAL: neutral,
        SentimentLabel.NEGATIVE: negative,
    }
    dominant = max(counts, key=lambda label: counts[label])

    return SentimentSummary(
        average_score=average,
        positive_count=positive,
        neutral_count=neutral,
        negative_count=negative,
        dominant_sentiment=dominant,
    )
