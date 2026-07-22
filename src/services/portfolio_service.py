"""Portfolio application service — orchestrates repositories and engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from math import ceil
from uuid import UUID

from src.config.settings import Settings
from src.core.constants import DEFAULT_OWNER_ID, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from src.core.exceptions import (
    FundNotFoundError,
    PortfolioNotFoundError,
    PortfolioValidationError,
)
from src.core.logging import get_logger
from src.domain.entities.holding import Holding
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.portfolio_snapshot import PortfolioSnapshot
from src.domain.entities.transaction import Transaction
from src.domain.enums import PortfolioStatus, TransactionStatus, TransactionType
from src.engines.portfolio.allocation_calculator import AllocationBreakdown
from src.engines.portfolio.engine import (
    PortfolioEngine,
    PortfolioPerformance,
    PortfolioValuation,
)
from src.engines.portfolio.holding_calculator import calculate_holding_from_transactions
from src.repositories.interfaces.asset_repository import AssetRepository
from src.repositories.interfaces.portfolio_repository import PortfolioRepository

logger = get_logger("services.portfolio")


@dataclass
class PortfolioSummary:
    """Portfolio summary for API and AI modules."""

    portfolio: Portfolio
    valuation: PortfolioValuation
    performance: PortfolioPerformance
    allocation: AllocationBreakdown


@dataclass
class PaginatedTransactions:
    """Paginated transaction list."""

    items: list[Transaction]
    page: int
    page_size: int
    total_items: int
    total_pages: int


@dataclass
class RecordTransactionCommand:
    """Input for recording a new transaction."""

    asset_id: UUID
    transaction_type: TransactionType
    units: Decimal
    price: Decimal
    gross_amount: Decimal | None = None
    fees: Decimal = Decimal("0")
    taxes: Decimal = Decimal("0")
    transaction_date: date | None = None
    reference_number: str | None = None
    notes: str | None = None
    source: str = "manual"


class PortfolioService:
    """Portfolio use cases coordinating persistence and calculations."""

    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        asset_repository: AssetRepository,
        settings: Settings,
        engine: PortfolioEngine | None = None,
    ) -> None:
        self._portfolio_repository = portfolio_repository
        self._asset_repository = asset_repository
        self._settings = settings
        self._engine = engine or PortfolioEngine()
        self._default_owner_id = UUID(DEFAULT_OWNER_ID)

    def create_portfolio(self, name: str, description: str | None = None) -> Portfolio:
        """Create a new portfolio for the default MVP owner."""
        portfolio = Portfolio(
            owner_id=self._default_owner_id,
            name=name,
            description=description,
            monthly_sip=Decimal(str(self._settings.default_monthly_investment)),
        )
        saved = self._portfolio_repository.save(portfolio)
        logger.info("portfolio_created portfolio_id={} name={}", saved.id, saved.name)
        return saved

    def get_or_create_default_portfolio(self) -> Portfolio:
        """Return the active portfolio, creating a default if none exists."""
        portfolios = self._portfolio_repository.find_by_owner(self._default_owner_id)
        active = next(
            (
                portfolio
                for portfolio in portfolios
                if portfolio.status == PortfolioStatus.ACTIVE
            ),
            None,
        )
        if active is not None:
            return active
        if portfolios:
            return portfolios[0]
        return self.create_portfolio(name="Primary Portfolio")

    def get_portfolio(self, portfolio_id: UUID) -> Portfolio:
        """Load a portfolio or raise if not found."""
        portfolio = self._portfolio_repository.get_by_id(portfolio_id)
        if portfolio is None:
            raise PortfolioNotFoundError(f"Portfolio {portfolio_id} not found.")
        return portfolio

    def get_summary(self, portfolio_id: UUID | None = None) -> PortfolioSummary:
        """Build the full portfolio summary with metrics."""
        portfolio = (
            self.get_portfolio(portfolio_id)
            if portfolio_id
            else self.get_or_create_default_portfolio()
        )
        holdings = self._portfolio_repository.get_holdings(portfolio.id)
        transactions = self._portfolio_repository.get_transactions(portfolio.id)
        cash_balance = self._engine.calculate_cash_balance(transactions)
        valuation = self._engine.calculate_valuation(holdings, cash_balance)
        self._refresh_holding_allocations(holdings, valuation.total_value)
        allocation = self._engine.calculate_allocation(holdings, cash_balance)
        start_date = self._first_transaction_date(transactions)
        performance = self._engine.calculate_performance(
            transactions,
            valuation,
            start_date,
        )
        return PortfolioSummary(
            portfolio=portfolio,
            valuation=valuation,
            performance=performance,
            allocation=allocation,
        )

    def get_holdings(self, portfolio_id: UUID | None = None) -> list[Holding]:
        """Return current holdings for a portfolio."""
        portfolio = (
            self.get_portfolio(portfolio_id)
            if portfolio_id
            else self.get_or_create_default_portfolio()
        )
        return self._portfolio_repository.get_holdings(portfolio.id)

    def get_transactions(
        self,
        portfolio_id: UUID | None = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedTransactions:
        """Return paginated transactions for a portfolio."""
        portfolio = (
            self.get_portfolio(portfolio_id)
            if portfolio_id
            else self.get_or_create_default_portfolio()
        )
        page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
        page = max(page, 1)
        all_transactions = sorted(
            self._portfolio_repository.get_transactions(portfolio.id),
            key=lambda item: item.transaction_date,
            reverse=True,
        )
        total_items = len(all_transactions)
        total_pages = max(ceil(total_items / page_size), 1)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedTransactions(
            items=all_transactions[start:end],
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )

    def record_transaction(
        self,
        command: RecordTransactionCommand,
        portfolio_id: UUID | None = None,
    ) -> Transaction:
        """Record a confirmed transaction and recalculate holdings."""
        portfolio = (
            self.get_portfolio(portfolio_id)
            if portfolio_id
            else self.get_or_create_default_portfolio()
        )
        asset = self._asset_repository.get_by_id(command.asset_id)
        if asset is None:
            raise FundNotFoundError(f"Asset {command.asset_id} not found.")

        gross_amount = command.gross_amount
        if gross_amount is None:
            gross_amount = command.units * command.price

        transaction = Transaction(
            portfolio_id=portfolio.id,
            asset_id=command.asset_id,
            transaction_type=command.transaction_type,
            units=command.units,
            price=command.price,
            gross_amount=gross_amount,
            fees=command.fees,
            taxes=command.taxes,
            reference_number=command.reference_number,
            transaction_date=command.transaction_date or date.today(),
            notes=command.notes,
            source=command.source,
        )
        transaction.confirm()
        transaction.validate()

        if command.transaction_type not in {
            TransactionType.ADJUSTMENT
        } and command.units <= Decimal("0"):
            raise PortfolioValidationError("Units must be greater than zero.")

        existing_holdings = self._portfolio_repository.get_holdings(portfolio.id)
        existing = next(
            (holding for holding in existing_holdings if holding.asset_id == asset.id),
            None,
        )
        all_transactions = self._portfolio_repository.get_transactions(portfolio.id)

        if command.transaction_type == TransactionType.ADJUSTMENT:
            transaction.holding_id = existing.id if existing else None
            saved_transaction = self._portfolio_repository.save_transaction(transaction)
            cash_balance = self._engine.calculate_cash_balance(
                all_transactions + [transaction]
            )
            if cash_balance < Decimal("0"):
                raise PortfolioValidationError("Cash balance cannot be negative.")
            logger.info(
                "cash_adjustment_recorded portfolio_id={} amount={}",
                portfolio.id,
                transaction.net_amount,
            )
            return saved_transaction

        all_transactions.append(transaction)

        current_price = command.price
        provisional_value = sum(
            (holding.current_value for holding in existing_holdings),
            Decimal("0"),
        )
        result = calculate_holding_from_transactions(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            asset_type=asset.asset_type,
            transactions=all_transactions,
            current_price=current_price,
            portfolio_value=provisional_value,
            existing_holding=existing,
        )
        transaction.holding_id = result.holding.id
        saved_transaction = self._portfolio_repository.save_transaction(transaction)
        saved_holding = self._portfolio_repository.save_holding(result.holding)

        cash_balance = self._engine.calculate_cash_balance(all_transactions)
        if cash_balance < Decimal("0"):
            raise PortfolioValidationError("Cash balance cannot be negative.")

        valuation = self._engine.calculate_valuation(
            self._merge_holding(existing_holdings, saved_holding),
            cash_balance,
        )
        saved_holding.update_market_value(current_price, valuation.total_value)
        self._portfolio_repository.save_holding(saved_holding)

        logger.info(
            "transaction_recorded portfolio_id={} asset_id={} type={}",
            portfolio.id,
            asset.id,
            command.transaction_type.value,
        )
        return saved_transaction

    def get_snapshots(
        self, portfolio_id: UUID | None = None
    ) -> list[PortfolioSnapshot]:
        """Return historical snapshots for a portfolio."""
        portfolio = (
            self.get_portfolio(portfolio_id)
            if portfolio_id
            else self.get_or_create_default_portfolio()
        )
        return sorted(
            self._portfolio_repository.get_snapshots(portfolio.id),
            key=lambda item: item.snapshot_date,
            reverse=True,
        )

    def generate_snapshot(self, portfolio_id: UUID | None = None) -> PortfolioSnapshot:
        """Generate and persist a portfolio snapshot."""
        summary = self.get_summary(portfolio_id)
        snapshot = self._engine.build_snapshot(
            portfolio_id=summary.portfolio.id,
            valuation=summary.valuation,
            performance=summary.performance,
            allocation=summary.allocation,
        )
        saved = self._portfolio_repository.save_snapshot(snapshot)
        logger.info(
            "snapshot_generated portfolio_id={} date={}",
            summary.portfolio.id,
            saved.snapshot_date,
        )
        return saved

    def get_performance(self, portfolio_id: UUID | None = None) -> PortfolioPerformance:
        """Return performance metrics for a portfolio."""
        return self.get_summary(portfolio_id).performance

    def _first_transaction_date(self, transactions: list[Transaction]) -> date | None:
        confirmed = [
            transaction
            for transaction in transactions
            if transaction.status == TransactionStatus.CONFIRMED
        ]
        if not confirmed:
            return None
        return min(transaction.transaction_date for transaction in confirmed)

    def _refresh_holding_allocations(
        self,
        holdings: list[Holding],
        portfolio_value: Decimal,
    ) -> None:
        for holding in holdings:
            holding.update_market_value(holding.current_price, portfolio_value)

    @staticmethod
    def _merge_holding(holdings: list[Holding], updated: Holding) -> list[Holding]:
        merged = [
            holding for holding in holdings if holding.asset_id != updated.asset_id
        ]
        merged.append(updated)
        return merged
