"""Abstract portfolio repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.holding import Holding
from src.domain.entities.investment_goal import InvestmentGoal
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.portfolio_snapshot import PortfolioSnapshot
from src.domain.entities.transaction import Transaction
from src.domain.enums import PortfolioStatus


class PortfolioRepository(ABC):
    """Persistence contract for portfolio aggregates."""

    @abstractmethod
    def get_by_id(self, portfolio_id: UUID) -> Portfolio | None:
        """Load a portfolio by identifier."""

    @abstractmethod
    def find_by_owner(self, owner_id: UUID) -> list[Portfolio]:
        """Find portfolios for an owner."""

    @abstractmethod
    def find_by_status(self, status: PortfolioStatus) -> list[Portfolio]:
        """Find portfolios by status."""

    @abstractmethod
    def save(self, portfolio: Portfolio) -> Portfolio:
        """Create or update a portfolio."""

    @abstractmethod
    def soft_delete(self, portfolio_id: UUID) -> None:
        """Soft delete a portfolio."""

    @abstractmethod
    def get_holdings(self, portfolio_id: UUID) -> list[Holding]:
        """Load holdings for a portfolio."""

    @abstractmethod
    def save_holding(self, holding: Holding) -> Holding:
        """Create or update a holding."""

    @abstractmethod
    def get_transactions(self, portfolio_id: UUID) -> list[Transaction]:
        """Load transactions for a portfolio."""

    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> Transaction:
        """Persist a transaction."""

    @abstractmethod
    def get_snapshots(self, portfolio_id: UUID) -> list[PortfolioSnapshot]:
        """Load snapshots for a portfolio."""

    @abstractmethod
    def save_snapshot(self, snapshot: PortfolioSnapshot) -> PortfolioSnapshot:
        """Persist a portfolio snapshot."""

    @abstractmethod
    def get_goals(self, portfolio_id: UUID) -> list[InvestmentGoal]:
        """Load goals for a portfolio."""

    @abstractmethod
    def save_goal(self, goal: InvestmentGoal) -> InvestmentGoal:
        """Create or update an investment goal."""
