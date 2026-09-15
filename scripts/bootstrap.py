"""Bootstrap InvestMind AI with live market data.

Step-by-step local setup:
1. Ensure .env exists
2. Create database schema
3. Seed Shariah funds and PSX stocks
4. Collect live MUFAP NAV, PSX prices, SBP/World Bank macro, news
5. Seed a sample portfolio (cash + holdings)
6. Generate first recommendations from live data

Usage:
    python -m scripts.bootstrap
    python -m scripts.bootstrap --reset-portfolio
"""

from __future__ import annotations

import argparse
import shutil
import sys
from decimal import Decimal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import Settings, get_settings
from src.core.logging import setup_logging
from src.database.session import get_session_factory, init_database
from src.domain.enums import AssetType, TransactionType
from src.repositories.sqlalchemy.asset_repository import SqlAlchemyAssetRepository
from src.scheduler.job_context import (
    build_portfolio_service,
    build_recommendation_service,
)
from src.services.asset_service import (
    AssetService,
    CreateMutualFundCommand,
    CreateStockCommand,
)
from src.services.collector_service import CollectorService
from src.services.portfolio_service import RecordTransactionCommand


FUNDS = [
    CreateMutualFundCommand(
        symbol="MIF",
        display_name="Meezan Islamic Fund",
        asset_type=AssetType.EQUITY_FUND,
        management_company="Al Meezan",
        expense_ratio=Decimal("1.80"),
        aum=Decimal("45000000000"),
        provider="seed",
    ),
    CreateMutualFundCommand(
        symbol="MEF",
        display_name="Meezan Energy Fund",
        asset_type=AssetType.EQUITY_FUND,
        management_company="Al Meezan",
        expense_ratio=Decimal("2.00"),
        aum=Decimal("12000000000"),
        provider="seed",
    ),
    CreateMutualFundCommand(
        symbol="AMMF",
        display_name="Al Meezan Mutual Fund",
        asset_type=AssetType.EQUITY_FUND,
        management_company="Al Meezan",
        expense_ratio=Decimal("1.80"),
        aum=Decimal("25000000000"),
        provider="seed",
    ),
    CreateMutualFundCommand(
        symbol="MCF",
        display_name="Meezan Cash Fund",
        asset_type=AssetType.MONEY_MARKET_FUND,
        management_company="Al Meezan",
        expense_ratio=Decimal("0.80"),
        aum=Decimal("80000000000"),
        provider="seed",
    ),
    CreateMutualFundCommand(
        symbol="KMIF",
        display_name="KSE Meezan Index Fund",
        asset_type=AssetType.EQUITY_FUND,
        management_company="Al Meezan",
        expense_ratio=Decimal("1.00"),
        aum=Decimal("15000000000"),
        provider="seed",
    ),
    CreateMutualFundCommand(
        symbol="MBF",
        display_name="Meezan Balanced Fund",
        asset_type=AssetType.BALANCED_FUND,
        management_company="Al Meezan",
        expense_ratio=Decimal("1.50"),
        aum=Decimal("8000000000"),
        provider="seed",
    ),
]

STOCKS = [
    CreateStockCommand(
        symbol="ENGRO",
        display_name="Engro Corporation",
        company_name="Engro Corporation Limited",
        industry="Fertilizer",
        market_cap=Decimal("250000000000"),
        pe=Decimal("8.5"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="MARI",
        display_name="Mari Petroleum",
        company_name="Mari Petroleum Company Limited",
        industry="Oil & Gas",
        market_cap=Decimal("320000000000"),
        pe=Decimal("7.2"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="MEBL",
        display_name="Meezan Bank",
        company_name="Meezan Bank Limited",
        industry="Banking",
        market_cap=Decimal("280000000000"),
        pe=Decimal("6.8"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="OGDC",
        display_name="Oil & Gas Development",
        company_name="Oil and Gas Development Company Limited",
        industry="Oil & Gas",
        market_cap=Decimal("900000000000"),
        pe=Decimal("5.5"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="PPL",
        display_name="Pakistan Petroleum",
        company_name="Pakistan Petroleum Limited",
        industry="Oil & Gas",
        market_cap=Decimal("450000000000"),
        pe=Decimal("6.0"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="HUBC",
        display_name="Hub Power",
        company_name="The Hub Power Company Limited",
        industry="Power",
        market_cap=Decimal("200000000000"),
        pe=Decimal("5.8"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="SYS",
        display_name="Systems Limited",
        company_name="Systems Limited",
        industry="Technology",
        market_cap=Decimal("180000000000"),
        pe=Decimal("18.0"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="LUCK",
        display_name="Lucky Cement",
        company_name="Lucky Cement Limited",
        industry="Cement",
        market_cap=Decimal("350000000000"),
        pe=Decimal("9.0"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="FFC",
        display_name="Fauji Fertilizer",
        company_name="Fauji Fertilizer Company Limited",
        industry="Fertilizer",
        market_cap=Decimal("300000000000"),
        pe=Decimal("7.5"),
        provider="seed",
    ),
    CreateStockCommand(
        symbol="UBL",
        display_name="United Bank",
        company_name="United Bank Limited",
        industry="Banking",
        market_cap=Decimal("400000000000"),
        pe=Decimal("5.2"),
        provider="seed",
    ),
]


def _ensure_env_file(project_root: Path) -> None:
    env_path = project_root / ".env"
    example = project_root / ".env.example"
    if env_path.exists():
        print("[ok] .env already present")
        return
    if not example.exists():
        raise FileNotFoundError(".env.example is missing")
    shutil.copy(example, env_path)
    print("[ok] Created .env from .env.example")


def _ensure_directories(project_root: Path) -> None:
    for relative in (
        "data",
        "data/imports",
        "data/raw",
        "data/processed",
        "logs",
        "reports",
    ):
        (project_root / relative).mkdir(parents=True, exist_ok=True)
    print("[ok] Data directories ready")


def _seed_assets(asset_service: AssetService) -> dict[str, str]:
    created: dict[str, str] = {}
    for command in FUNDS:
        existing = asset_service.get_by_symbol(command.symbol)
        if existing is None:
            fund = asset_service.create_mutual_fund(command)
            created[fund.asset.symbol] = str(fund.asset_id)
            print(f"[ok] Seeded fund {fund.asset.symbol}")
        else:
            if existing.asset_type != command.asset_type:
                existing.asset_type = command.asset_type
                asset_service._asset_repository.save(existing)  # noqa: SLF001
                print(
                    f"[ok] Updated fund type {existing.symbol} -> {command.asset_type.value}"
                )
            created[existing.symbol] = str(existing.id)
            print(f"[skip] Fund already exists: {existing.symbol}")
    for command in STOCKS:
        existing = asset_service.get_by_symbol(command.symbol)
        if existing is None:
            stock = asset_service.create_stock(command)
            created[stock.asset.symbol] = str(stock.asset_id)
            print(f"[ok] Seeded stock {stock.asset.symbol}")
        else:
            created[existing.symbol] = str(existing.id)
            print(f"[skip] Stock already exists: {existing.symbol}")
    return created


def _seed_portfolio(
    settings: Settings,
    session,
    asset_ids: dict[str, str],
    *,
    reset_portfolio: bool,
) -> None:
    from uuid import UUID

    portfolio_service = build_portfolio_service(settings, session)
    portfolio = portfolio_service.get_or_create_default_portfolio()
    holdings = portfolio_service.get_holdings(portfolio.id)
    if holdings and not reset_portfolio:
        print("[skip] Portfolio already has holdings (use --reset-portfolio to reseed)")
        return

    mif_id = UUID(asset_ids["MIF"])
    engro_id = UUID(asset_ids["ENGRO"])

    # Cash deposit
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=mif_id,
            transaction_type=TransactionType.ADJUSTMENT,
            units=Decimal("0"),
            price=Decimal("0"),
            gross_amount=Decimal("1000000"),
            notes="Bootstrap cash deposit",
            source="bootstrap",
        ),
        portfolio_id=portfolio.id,
    )
    # Buy fund units
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=mif_id,
            transaction_type=TransactionType.BUY,
            units=Decimal("5000"),
            price=Decimal("100"),
            notes="Bootstrap MIF purchase",
            source="bootstrap",
        ),
        portfolio_id=portfolio.id,
    )
    # Buy stock
    portfolio_service.record_transaction(
        RecordTransactionCommand(
            asset_id=engro_id,
            transaction_type=TransactionType.BUY,
            units=Decimal("200"),
            price=Decimal("320"),
            notes="Bootstrap ENGRO purchase",
            source="bootstrap",
        ),
        portfolio_id=portfolio.id,
    )
    print("[ok] Seeded sample portfolio (cash + MIF + ENGRO)")


def bootstrap(*, reset_portfolio: bool = False, skip_news: bool = False) -> None:
    """Run the full local bootstrap pipeline."""
    project_root = PROJECT_ROOT
    print("=== InvestMind AI bootstrap ===")
    _ensure_env_file(project_root)
    _ensure_directories(project_root)

    get_settings.cache_clear()
    settings = Settings()
    settings.database_echo = False
    setup_logging(settings)
    init_database(settings)
    print(f"[ok] Database ready ({settings.database_url})")

    session_factory = get_session_factory(settings)
    with session_factory() as session:
        asset_service = AssetService(SqlAlchemyAssetRepository(session))
        asset_ids = _seed_assets(asset_service)
        session.commit()

        get_settings.cache_clear()
        settings = Settings()
        settings.database_echo = False
        collectors = CollectorService(settings, session)
        live_failed = False
        for label, runner in (
            ("NAV", collectors.run_nav_import),
            ("stocks", collectors.run_stock_import),
            ("macro", collectors.run_macro_import),
        ):
            result = runner()
            print(
                f"[{'ok' if result.status.value != 'failed' else 'warn'}] "
                f"{label} import: status={result.status.value} "
                f"saved={result.rows_saved} rejected={result.rows_rejected}"
            )
            if result.errors:
                print(f"     errors={result.errors}")
            if result.status.value == "failed" or result.rows_saved == 0:
                live_failed = True
        if live_failed:
            print(
                "[warn] One or more live imports saved 0 rows. "
                "Advice needs live NAV/prices/macro. Re-run after checking network."
            )

        if skip_news:
            print("[skip] News import")
        else:
            try:
                result = collectors.run_news_import()
                print(
                    f"[ok] News import: status={result.status.value} "
                    f"saved={result.rows_saved}"
                )
                if result.errors:
                    print(f"     errors={result.errors}")
            except Exception as exc:  # noqa: BLE001
                print(f"[warn] News import failed (optional): {exc}")

        _seed_portfolio(
            settings,
            session,
            asset_ids,
            reset_portfolio=reset_portfolio,
        )
        session.commit()

        recommendations = build_recommendation_service(
            settings, session
        ).run_recommendation_cycle()
        session.commit()
        print(f"[ok] Generated {len(recommendations)} recommendation(s)")
        for item in recommendations[:5]:
            print(
                f"     - {item.recommendation_type.value} "
                f"confidence={item.confidence} "
                f"symbol={item.symbol or item.to_symbol or '-'}"
            )

    print()
    print("Bootstrap complete. Next steps:")
    print("  1. Start API:     uv run python -m src.main")
    print("  2. Open docs:     http://localhost:8000/docs")
    print("  3. Start UI:      cd dashboard && npm install && npm run dev")
    print("  4. Dashboard:     http://localhost:5173")
    print("  5. Re-import:     POST /api/v1/collectors/nav|stocks|macro|news")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap InvestMind AI locally")
    parser.add_argument(
        "--reset-portfolio",
        action="store_true",
        help="Re-seed sample holdings even if portfolio already has data",
    )
    parser.add_argument(
        "--skip-news",
        action="store_true",
        help="Skip live RSS news import",
    )
    args = parser.parse_args()
    bootstrap(reset_portfolio=args.reset_portfolio, skip_news=args.skip_news)


if __name__ == "__main__":
    main()
