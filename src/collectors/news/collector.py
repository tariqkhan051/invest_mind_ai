"""RSS and JSON news collector."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from xml.etree import ElementTree

from src.collectors.base.collector import BaseCollector
from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.models import NewsRecord, ProviderHealth
from src.collectors.base.validator import validate_news_record
from src.config.settings import Settings
from src.engines.market_intelligence.sentiment_analyzer import (
    analyze_sentiment,
    classify_news,
)
from src.repositories.interfaces.news_repository import NewsRepository


class NewsCollector(BaseCollector):
    """Collect financial news from configured RSS or JSON feeds."""

    provider_name = "news"

    def __init__(
        self,
        settings: Settings,
        news_repository: NewsRepository,
        http_client: CollectorHttpClient | None = None,
    ) -> None:
        super().__init__(settings)
        self._news_repository = news_repository
        timeout = int(self._provider_config.get("timeout_seconds", 15))
        retries = int(self._provider_config.get("retry_attempts", 2))
        self._http_client = http_client or CollectorHttpClient(timeout, retries)

    def collect(self) -> Any:
        """Download news from configured feed endpoints."""
        feeds = self._provider_config.get("feeds", [])
        if isinstance(feeds, list) and feeds:
            collected: list[dict[str, Any]] = []
            for feed in feeds:
                if not isinstance(feed, dict):
                    continue
                feed_url = str(feed.get("url", "")).strip()
                if not feed_url:
                    continue
                response = self._http_client.get_text(feed_url)
                if response.strip().startswith("{"):
                    payload = self._http_client.get_json(feed_url)
                    if isinstance(payload, dict):
                        rows = payload.get("articles", payload.get("records", []))
                        if isinstance(rows, list):
                            collected.extend(
                                row for row in rows if isinstance(row, dict)
                            )
                else:
                    collected.extend(self._parse_rss(response))
            return collected

        feed_url = str(self._provider_config.get("feed_url", "")).strip()
        if not feed_url:
            return {"articles": []}
        response = self._http_client.get_text(feed_url)
        if response.strip().startswith("{"):
            return self._http_client.get_json(feed_url)
        return self._parse_rss(response)

    def normalize(self, raw_data: Any) -> list[NewsRecord]:
        """Normalize provider payload into news records."""
        rows = raw_data
        if isinstance(raw_data, dict):
            rows = raw_data.get("articles", raw_data.get("records", []))
        if not isinstance(rows, list):
            return []

        records: list[NewsRecord] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            headline = str(row.get("headline") or row.get("title") or "").strip()
            url = str(row.get("url") or row.get("link") or "").strip()
            published = self._parse_datetime(
                row.get("publication_time")
                or row.get("published")
                or row.get("pubDate")
            )
            if not headline or not url or published is None:
                continue
            records.append(
                NewsRecord(
                    headline=headline,
                    url=url,
                    publication_time=published,
                    source=self.provider_name,
                    summary=row.get("summary") or row.get("description"),
                    publisher=row.get("publisher") or row.get("source"),
                    country=str(row.get("country", "PK")),
                    language=str(row.get("language", "en")),
                )
            )
        return records

    def save(self, records: list[NewsRecord]) -> tuple[int, int]:
        """Persist validated news records with sentiment metadata."""
        saved = 0
        duplicates = 0
        for record in records:
            category = classify_news(record)
            sentiment, score = analyze_sentiment(record)
            if self._news_repository.save_news(record, category, sentiment, score):
                saved += 1
            else:
                duplicates += 1
        return saved, duplicates

    def _validate_record(self, record: NewsRecord) -> list[str]:
        return validate_news_record(record)

    def health_check(self) -> ProviderHealth:
        feed_url = str(self._provider_config.get("feed_url", "")).strip()
        feeds = self._provider_config.get("feeds", [])
        if isinstance(feeds, list) and feeds:
            first = feeds[0]
            if isinstance(first, dict):
                feed_url = str(first.get("url", feed_url)).strip()
        healthy = bool(feed_url) and self._http_client.health_check(feed_url)
        return ProviderHealth(
            provider=self.provider_name,
            healthy=healthy,
            message="News feed reachable." if healthy else "News feed unreachable.",
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
        text = str(value).strip()
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
        ):
            try:
                parsed = datetime.strptime(text[:35], fmt)
                if parsed.tzinfo:
                    return parsed.astimezone(UTC)
                return parsed.replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_rss(xml_text: str) -> list[dict[str, str]]:
        root = ElementTree.fromstring(xml_text)
        items: list[dict[str, str]] = []
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            if title and link:
                items.append(
                    {
                        "title": title,
                        "link": link,
                        "description": description,
                        "pubDate": pub_date,
                    }
                )
        return items
