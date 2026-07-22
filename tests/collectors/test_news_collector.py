"""Unit tests for news collector."""


import httpx
from sqlalchemy.orm import Session

from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.models import CollectorStatus
from src.collectors.news.collector import NewsCollector
from src.config.settings import Settings
from src.repositories.sqlalchemy.news_repository import SqlAlchemyNewsRepository


def _mock_client(payload: dict[str, object]) -> CollectorHttpClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    return CollectorHttpClient(client=httpx.Client(transport=transport))


def test_news_collector_saves_articles(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """News collector should normalize and persist articles."""
    news_repo = SqlAlchemyNewsRepository(db_session)
    collector = NewsCollector(
        test_settings,
        news_repo,
        http_client=_mock_client(
            {
                "articles": [
                    {
                        "title": "PSX rallies on banking growth",
                        "url": "https://example.com/psx-rally",
                        "published": "2026-01-15T10:00:00Z",
                        "summary": "Banking sector leads market rally.",
                    }
                ]
            }
        ),
    )

    result = collector.run()
    assert result.status == CollectorStatus.SUCCESS
    assert result.rows_saved == 1
    assert news_repo.news_exists("https://example.com/psx-rally")


def test_news_collector_rejects_duplicate_urls(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Duplicate news URLs should be skipped."""
    news_repo = SqlAlchemyNewsRepository(db_session)
    collector = NewsCollector(
        test_settings,
        news_repo,
        http_client=_mock_client(
            {
                "articles": [
                    {
                        "title": "Duplicate article",
                        "url": "https://example.com/duplicate",
                        "published": "2026-01-15T10:00:00Z",
                    }
                ]
            }
        ),
    )

    first = collector.run()
    second = collector.run()
    assert first.rows_saved == 1
    assert second.rows_duplicates == 1
