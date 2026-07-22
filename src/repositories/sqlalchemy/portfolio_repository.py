"""SQLAlchemy portfolio repository implementation."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.exceptions import PortfolioNotFoundError
from src.database.mappers.portfolio_mapper import (
    HoldingMapper,
    InvestmentGoalMapper,
    PortfolioMapper,
    PortfolioSnapshotMapper,
    TransactionMapper,
)
from src.database.models.portfolio import (
    HoldingModel,
    InvestmentGoalModel,
    PortfolioModel,
    PortfolioSnapshotModel,
    TransactionModel,
)
from src.domain.entities.holding import Holding
from src.domain.entities.investment_goal import InvestmentGoal
from src.domain.entities.portfolio import Portfolio
from src.domain.entities.portfolio_snapshot import PortfolioSnapshot
from src.domain.entities.transaction import Transaction
from src.domain.enums import PortfolioStatus
from src.repositories.interfaces.portfolio_repository import PortfolioRepository


class SqlAlchemyPortfolioRepository(PortfolioRepository):
    """Portfolio persistence using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, portfolio_id: UUID) -> Portfolio | None:
        model = self._session.get(PortfolioModel, portfolio_id)
        if model is None or model.deleted_at is not None:
            return None
        return PortfolioMapper.to_entity(model)

    def find_by_owner(self, owner_id: UUID) -> list[Portfolio]:
        stmt = select(PortfolioModel).where(
            PortfolioModel.owner_id == owner_id,
            PortfolioModel.deleted_at.is_(None),
        )
        return [PortfolioMapper.to_entity(row) for row in self._session.scalars(stmt)]

    def find_by_status(self, status: PortfolioStatus) -> list[Portfolio]:
        stmt = select(PortfolioModel).where(
            PortfolioModel.status == status.value,
            PortfolioModel.deleted_at.is_(None),
        )
        return [PortfolioMapper.to_entity(row) for row in self._session.scalars(stmt)]

    def save(self, portfolio: Portfolio) -> Portfolio:
        portfolio.validate()
        model = self._session.get(PortfolioModel, portfolio.id)
        if model is None:
            model = PortfolioMapper.to_model(portfolio)
            self._session.add(model)
        else:
            PortfolioMapper.update_model(model, portfolio)
        self._session.flush()
        return PortfolioMapper.to_entity(model)

    def soft_delete(self, portfolio_id: UUID) -> None:
        model = self._session.get(PortfolioModel, portfolio_id)
        if model is None:
            raise PortfolioNotFoundError(f"Portfolio {portfolio_id} not found.")
        model.deleted_at = datetime.now(UTC)
        self._session.flush()

    def get_holdings(self, portfolio_id: UUID) -> list[Holding]:
        stmt = select(HoldingModel).where(HoldingModel.portfolio_id == portfolio_id)
        return [HoldingMapper.to_entity(row) for row in self._session.scalars(stmt)]

    def save_holding(self, holding: Holding) -> Holding:
        holding.validate()
        model = self._session.get(HoldingModel, holding.id)
        if model is None:
            model = HoldingMapper.to_model(holding)
            self._session.add(model)
        else:
            updated = HoldingMapper.to_model(holding)
            for column in HoldingModel.__table__.columns:
                setattr(model, column.name, getattr(updated, column.name))
        self._session.flush()
        return HoldingMapper.to_entity(model)

    def get_transactions(self, portfolio_id: UUID) -> list[Transaction]:
        stmt = select(TransactionModel).where(
            TransactionModel.portfolio_id == portfolio_id
        )
        return [TransactionMapper.to_entity(row) for row in self._session.scalars(stmt)]

    def save_transaction(self, transaction: Transaction) -> Transaction:
        transaction.validate()
        model = self._session.get(TransactionModel, transaction.id)
        if model is not None:
            return TransactionMapper.to_entity(model)
        model = TransactionMapper.to_model(transaction)
        self._session.add(model)
        self._session.flush()
        return TransactionMapper.to_entity(model)

    def get_snapshots(self, portfolio_id: UUID) -> list[PortfolioSnapshot]:
        stmt = select(PortfolioSnapshotModel).where(
            PortfolioSnapshotModel.portfolio_id == portfolio_id
        )
        return [
            PortfolioSnapshotMapper.to_entity(row)
            for row in self._session.scalars(stmt)
        ]

    def save_snapshot(self, snapshot: PortfolioSnapshot) -> PortfolioSnapshot:
        model = PortfolioSnapshotMapper.to_model(snapshot)
        self._session.add(model)
        self._session.flush()
        return PortfolioSnapshotMapper.to_entity(model)

    def get_goals(self, portfolio_id: UUID) -> list[InvestmentGoal]:
        stmt = select(InvestmentGoalModel).where(
            InvestmentGoalModel.portfolio_id == portfolio_id
        )
        return [
            InvestmentGoalMapper.to_entity(row) for row in self._session.scalars(stmt)
        ]

    def save_goal(self, goal: InvestmentGoal) -> InvestmentGoal:
        goal.validate()
        model = self._session.get(InvestmentGoalModel, goal.id)
        if model is None:
            model = InvestmentGoalMapper.to_model(goal)
            self._session.add(model)
        else:
            updated = InvestmentGoalMapper.to_model(goal)
            for column in InvestmentGoalModel.__table__.columns:
                setattr(model, column.name, getattr(updated, column.name))
        self._session.flush()
        return InvestmentGoalMapper.to_entity(model)
