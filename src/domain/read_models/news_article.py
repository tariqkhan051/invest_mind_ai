"""News article read model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.domain.enums import NewsCategory, SentimentLabel


@dataclass(frozen=True, slots=True)
class NewsArticle:
    """Normalized financial news article."""

    id: UUID
    headline: str
    summary: str | None
    publisher: str | None
    publication_time: datetime
    url: str
    country: str
    category: NewsCategory
    sentiment: SentimentLabel
    sentiment_score: Decimal
    source: str | None = None
