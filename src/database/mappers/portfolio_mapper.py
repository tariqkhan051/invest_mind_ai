"""Portfolio domain ↔ ORM mappers."""

from __future__ import annotations

from decimal import Decimal

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
from src.domain.enums import (
    AssetType,
    GoalStatus,
    HoldingStatus,
    InvestmentHorizon,
    InvestmentObjective,
    InvestmentPreference,
    PortfolioStatus,
    RiskProfile,
    TransactionStatus,
    TransactionType,
)


class PortfolioMapper:
    """Convert Portfolio entities and ORM models."""

    @staticmethod
    def to_entity(model: PortfolioModel) -> Portfolio:
        """Map ORM model to domain entity."""
        return Portfolio(
            id=model.id,
            owner_id=model.owner_id,
            name=model.name,
            description=model.description,
            base_currency=model.base_currency,
            risk_profile=RiskProfile(model.risk_profile),
            investment_preference=InvestmentPreference(model.investment_preference),
            investment_objective=InvestmentObjective(model.investment_objective),
            investment_horizon=InvestmentHorizon(model.investment_horizon),
            monthly_sip=model.monthly_sip,
            status=PortfolioStatus(model.status),
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(entity: Portfolio) -> PortfolioModel:
        """Map domain entity to ORM model."""
        return PortfolioModel(
            id=entity.id,
            owner_id=entity.owner_id,
            name=entity.name,
            description=entity.description,
            base_currency=entity.base_currency,
            risk_profile=entity.risk_profile.value,
            investment_preference=entity.investment_preference.value,
            investment_objective=entity.investment_objective.value,
            investment_horizon=entity.investment_horizon.value,
            monthly_sip=entity.monthly_sip,
            status=entity.status.value,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    @staticmethod
    def update_model(model: PortfolioModel, entity: Portfolio) -> PortfolioModel:
        """Update an existing ORM model from a domain entity."""
        model.owner_id = entity.owner_id
        model.name = entity.name
        model.description = entity.description
        model.base_currency = entity.base_currency
        model.risk_profile = entity.risk_profile.value
        model.investment_preference = entity.investment_preference.value
        model.investment_objective = entity.investment_objective.value
        model.investment_horizon = entity.investment_horizon.value
        model.monthly_sip = entity.monthly_sip
        model.status = entity.status.value
        model.version = entity.version
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model


class HoldingMapper:
    """Convert Holding entities and ORM models."""

    @staticmethod
    def to_entity(model: HoldingModel) -> Holding:
        """Map ORM model to domain entity."""
        return Holding(
            id=model.id,
            portfolio_id=model.portfolio_id,
            asset_id=model.asset_id,
            asset_type=AssetType(model.asset_type),
            quantity=model.quantity,
            average_cost=model.average_cost,
            current_price=model.current_price,
            current_value=model.current_value,
            cost_basis=model.cost_basis,
            unrealized_gain=model.unrealized_gain,
            realized_gain=model.realized_gain,
            allocation_percentage=model.allocation_percentage,
            currency=model.currency,
            status=HoldingStatus(model.status),
            last_price_update=model.last_price_update,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Holding) -> HoldingModel:
        """Map domain entity to ORM model."""
        return HoldingModel(
            id=entity.id,
            portfolio_id=entity.portfolio_id,
            asset_id=entity.asset_id,
            asset_type=entity.asset_type.value,
            quantity=entity.quantity,
            average_cost=entity.average_cost,
            current_price=entity.current_price,
            current_value=entity.current_value,
            cost_basis=entity.cost_basis,
            unrealized_gain=entity.unrealized_gain,
            realized_gain=entity.realized_gain,
            allocation_percentage=entity.allocation_percentage,
            currency=entity.currency,
            status=entity.status.value,
            last_price_update=entity.last_price_update,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class TransactionMapper:
    """Convert Transaction entities and ORM models."""

    @staticmethod
    def to_entity(model: TransactionModel) -> Transaction:
        """Map ORM model to domain entity."""
        return Transaction(
            id=model.id,
            portfolio_id=model.portfolio_id,
            holding_id=model.holding_id,
            asset_id=model.asset_id,
            transaction_type=TransactionType(model.transaction_type),
            units=model.units,
            price=model.price,
            gross_amount=model.gross_amount,
            fees=model.fees,
            taxes=model.taxes,
            net_amount=model.net_amount,
            reference_number=model.reference_number,
            transaction_date=model.transaction_date,
            settlement_date=model.settlement_date,
            notes=model.notes,
            source=model.source,
            status=TransactionStatus(model.status),
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: Transaction) -> TransactionModel:
        """Map domain entity to ORM model."""
        return TransactionModel(
            id=entity.id,
            portfolio_id=entity.portfolio_id,
            holding_id=entity.holding_id,
            asset_id=entity.asset_id,
            transaction_type=entity.transaction_type.value,
            units=entity.units,
            price=entity.price,
            gross_amount=entity.gross_amount,
            fees=entity.fees,
            taxes=entity.taxes,
            net_amount=entity.net_amount,
            reference_number=entity.reference_number,
            transaction_date=entity.transaction_date,
            settlement_date=entity.settlement_date,
            notes=entity.notes,
            source=entity.source,
            status=entity.status.value,
            created_at=entity.created_at,
        )


class PortfolioSnapshotMapper:
    """Convert PortfolioSnapshot entities and ORM models."""

    @staticmethod
    def to_entity(model: PortfolioSnapshotModel) -> PortfolioSnapshot:
        """Map ORM model to domain entity."""
        allocation = (
            {key: Decimal(str(value)) for key, value in model.allocation_json.items()}
            if model.allocation_json
            else None
        )
        sector_allocation = (
            {
                key: Decimal(str(value))
                for key, value in model.sector_allocation_json.items()
            }
            if model.sector_allocation_json
            else None
        )
        return PortfolioSnapshot(
            id=model.id,
            portfolio_id=model.portfolio_id,
            snapshot_date=model.snapshot_date,
            total_value=model.total_value,
            investment_value=model.investment_value,
            cash_value=model.cash_value,
            daily_return=model.daily_return,
            monthly_return=model.monthly_return,
            yearly_return=model.yearly_return,
            xirr=model.xirr,
            cagr=model.cagr,
            volatility=model.volatility,
            drawdown=model.drawdown,
            sharpe_ratio=model.sharpe_ratio,
            sortino_ratio=model.sortino_ratio,
            allocation_json=allocation,
            sector_allocation_json=sector_allocation,
            notes=model.notes,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: PortfolioSnapshot) -> PortfolioSnapshotModel:
        """Map domain entity to ORM model."""
        allocation = (
            {key: float(value) for key, value in entity.allocation_json.items()}
            if entity.allocation_json
            else None
        )
        sector_allocation = (
            {key: float(value) for key, value in entity.sector_allocation_json.items()}
            if entity.sector_allocation_json
            else None
        )
        return PortfolioSnapshotModel(
            id=entity.id,
            portfolio_id=entity.portfolio_id,
            snapshot_date=entity.snapshot_date,
            total_value=entity.total_value,
            investment_value=entity.investment_value,
            cash_value=entity.cash_value,
            daily_return=entity.daily_return,
            monthly_return=entity.monthly_return,
            yearly_return=entity.yearly_return,
            xirr=entity.xirr,
            cagr=entity.cagr,
            volatility=entity.volatility,
            drawdown=entity.drawdown,
            sharpe_ratio=entity.sharpe_ratio,
            sortino_ratio=entity.sortino_ratio,
            allocation_json=allocation,
            sector_allocation_json=sector_allocation,
            notes=entity.notes,
            created_at=entity.created_at,
        )


class InvestmentGoalMapper:
    """Convert InvestmentGoal entities and ORM models."""

    @staticmethod
    def to_entity(model: InvestmentGoalModel) -> InvestmentGoal:
        """Map ORM model to domain entity."""
        return InvestmentGoal(
            id=model.id,
            portfolio_id=model.portfolio_id,
            name=model.name,
            target_amount=model.target_amount,
            current_amount=model.current_amount,
            target_date=model.target_date,
            monthly_contribution=model.monthly_contribution,
            priority=model.priority,
            risk_preference=RiskProfile(model.risk_preference),
            status=GoalStatus(model.status),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: InvestmentGoal) -> InvestmentGoalModel:
        """Map domain entity to ORM model."""
        return InvestmentGoalModel(
            id=entity.id,
            portfolio_id=entity.portfolio_id,
            name=entity.name,
            target_amount=entity.target_amount,
            current_amount=entity.current_amount,
            target_date=entity.target_date,
            monthly_contribution=entity.monthly_contribution,
            priority=entity.priority,
            risk_preference=entity.risk_preference.value,
            status=entity.status.value,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
