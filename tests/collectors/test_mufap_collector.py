"""Unit tests for MUFAP collector."""

from datetime import date
from decimal import Decimal

import httpx
from sqlalchemy.orm import Session

from src.collectors.base.http_client import CollectorHttpClient
from src.collectors.base.models import CollectorStatus
from src.collectors.mufap.collector import MufapCollector
from src.config.settings import Settings
from src.domain.entities.asset import Asset
from src.domain.enums import AssetType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.repositories.sqlalchemy.market_data_repository import (
    SqlAlchemyMarketDataRepository,
)


def _mock_client(payload: dict[str, object]) -> CollectorHttpClient:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/nav/daily"):
            return httpx.Response(200, json=payload)
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    return CollectorHttpClient(client=httpx.Client(transport=transport))


def test_mufap_collector_saves_nav_records(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """MUFAP collector should normalize and persist NAV history."""
    asset_repo = SqlAlchemyAssetRepository(db_session)
    asset = asset_repo.save(
        Asset(
            symbol="MIF",
            display_name="Meezan Islamic Fund",
            asset_type=AssetType.MUTUAL_FUND,
        )
    )
    market_repo = SqlAlchemyMarketDataRepository(db_session)

    collector = MufapCollector(
        test_settings,
        asset_repo,
        market_repo,
        http_client=_mock_client(
            {
                "records": [
                    {
                        "symbol": "MIF",
                        "date": "2026-01-15",
                        "nav": "52.45",
                    }
                ]
            }
        ),
    )

    result = collector.run()
    assert result.status == CollectorStatus.SUCCESS
    assert result.rows_saved == 1
    assert market_repo.nav_exists(asset.id, date(2026, 1, 15))


def test_mufap_collector_rejects_invalid_nav(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Invalid NAV values should be rejected during validation."""
    asset_repo = SqlAlchemyAssetRepository(db_session)
    asset_repo.save(
        Asset(
            symbol="MIF",
            display_name="Meezan Islamic Fund",
            asset_type=AssetType.MUTUAL_FUND,
        )
    )
    market_repo = SqlAlchemyMarketDataRepository(db_session)

    collector = MufapCollector(
        test_settings,
        asset_repo,
        market_repo,
        http_client=_mock_client(
            {
                "records": [
                    {
                        "symbol": "MIF",
                        "date": "2026-01-15",
                        "nav": "-1",
                    }
                ]
            }
        ),
    )

    result = collector.run()
    assert result.rows_rejected == 1
    assert result.rows_saved == 0


def test_mufap_collector_skips_duplicates(
    db_session: Session,
    test_settings: Settings,
) -> None:
    """Duplicate NAV imports should be detected."""
    asset_repo = SqlAlchemyAssetRepository(db_session)
    asset = asset_repo.save(
        Asset(
            symbol="MIF",
            display_name="Meezan Islamic Fund",
            asset_type=AssetType.MUTUAL_FUND,
        )
    )
    market_repo = SqlAlchemyMarketDataRepository(db_session)
    from src.collectors.base.models import NavRecord

    market_repo.save_nav(
        NavRecord(
            symbol="MIF",
            nav_date=date(2026, 1, 15),
            nav=Decimal("52.45"),
            source="test",
        ),
        asset.id,
    )

    collector = MufapCollector(
        test_settings,
        asset_repo,
        market_repo,
        http_client=_mock_client(
            {
                "records": [
                    {
                        "symbol": "MIF",
                        "date": "2026-01-15",
                        "nav": "52.45",
                    }
                ]
            }
        ),
    )

    result = collector.run()
    assert result.rows_duplicates == 1
    assert result.rows_saved == 0
