"""Asset domain ↔ ORM mappers."""

from __future__ import annotations

from src.database.models.asset import AssetModel, MutualFundModel, StockModel
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.stock import Stock
from src.domain.enums import AssetStatus, AssetType


class AssetMapper:
    """Convert Asset entities and ORM models."""

    @staticmethod
    def to_entity(model: AssetModel) -> Asset:
        """Map ORM model to domain entity."""
        return Asset(
            id=model.id,
            symbol=model.symbol,
            display_name=model.display_name,
            short_name=model.short_name,
            asset_type=AssetType(model.asset_type),
            currency=model.currency,
            country=model.country,
            exchange=model.exchange,
            is_shariah=model.is_shariah,
            status=AssetStatus(model.status),
            launch_date=model.launch_date,
            provider=model.provider,
            metadata_json=model.metadata_json,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(entity: Asset) -> AssetModel:
        """Map domain entity to ORM model."""
        return AssetModel(
            id=entity.id,
            symbol=entity.symbol,
            display_name=entity.display_name,
            short_name=entity.short_name,
            asset_type=entity.asset_type.value,
            currency=entity.currency,
            country=entity.country,
            exchange=entity.exchange,
            is_shariah=entity.is_shariah,
            status=entity.status.value,
            launch_date=entity.launch_date,
            provider=entity.provider,
            metadata_json=entity.metadata_json,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    @staticmethod
    def update_model(model: AssetModel, entity: Asset) -> AssetModel:
        """Update an existing ORM model from a domain entity."""
        model.symbol = entity.symbol
        model.display_name = entity.display_name
        model.short_name = entity.short_name
        model.asset_type = entity.asset_type.value
        model.currency = entity.currency
        model.country = entity.country
        model.exchange = entity.exchange
        model.is_shariah = entity.is_shariah
        model.status = entity.status.value
        model.launch_date = entity.launch_date
        model.provider = entity.provider
        model.metadata_json = entity.metadata_json
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model


class MutualFundMapper:
    """Convert MutualFund entities and ORM models."""

    @staticmethod
    def to_entity(model: MutualFundModel, asset: Asset) -> MutualFund:
        """Map ORM model to domain entity."""
        return MutualFund(
            asset_id=model.asset_id,
            asset=asset,
            management_company=model.management_company,
            fund_category_id=model.fund_category_id,
            benchmark_id=model.benchmark_id,
            expense_ratio=model.expense_ratio,
            front_load=model.front_load,
            back_load=model.back_load,
            management_fee=model.management_fee,
            minimum_investment=model.minimum_investment,
            minimum_sip=model.minimum_sip,
            aum=model.aum,
            cash_percentage=model.cash_percentage,
            equity_percentage=model.equity_percentage,
            debt_percentage=model.debt_percentage,
            dividend_policy=model.dividend_policy,
            dividend_frequency=model.dividend_frequency,
            website=model.website,
            factsheet_url=model.factsheet_url,
            prospectus_url=model.prospectus_url,
            last_nav_update=model.last_nav_update,
        )

    @staticmethod
    def to_model(entity: MutualFund) -> MutualFundModel:
        """Map domain entity to ORM model."""
        return MutualFundModel(
            asset_id=entity.asset_id,
            management_company=entity.management_company,
            fund_category_id=entity.fund_category_id,
            benchmark_id=entity.benchmark_id,
            expense_ratio=entity.expense_ratio,
            front_load=entity.front_load,
            back_load=entity.back_load,
            management_fee=entity.management_fee,
            minimum_investment=entity.minimum_investment,
            minimum_sip=entity.minimum_sip,
            aum=entity.aum,
            cash_percentage=entity.cash_percentage,
            equity_percentage=entity.equity_percentage,
            debt_percentage=entity.debt_percentage,
            dividend_policy=entity.dividend_policy,
            dividend_frequency=entity.dividend_frequency,
            website=entity.website,
            factsheet_url=entity.factsheet_url,
            prospectus_url=entity.prospectus_url,
            last_nav_update=entity.last_nav_update,
        )


class StockMapper:
    """Convert Stock entities and ORM models."""

    @staticmethod
    def to_entity(model: StockModel, asset: Asset) -> Stock:
        """Map ORM model to domain entity."""
        return Stock(
            asset_id=model.asset_id,
            asset=asset,
            isin=model.isin,
            company_name=model.company_name,
            sector_id=model.sector_id,
            industry=model.industry,
            market_cap=model.market_cap,
            free_float=model.free_float,
            shares_outstanding=model.shares_outstanding,
            eps=model.eps,
            pe=model.pe,
            pbv=model.pbv,
            roe=model.roe,
            roa=model.roa,
            debt_ratio=model.debt_ratio,
            dividend_yield=model.dividend_yield,
            last_financial_update=model.last_financial_update,
        )

    @staticmethod
    def to_model(entity: Stock) -> StockModel:
        """Map domain entity to ORM model."""
        return StockModel(
            asset_id=entity.asset_id,
            isin=entity.isin,
            company_name=entity.company_name,
            sector_id=entity.sector_id,
            industry=entity.industry,
            market_cap=entity.market_cap,
            free_float=entity.free_float,
            shares_outstanding=entity.shares_outstanding,
            eps=entity.eps,
            pe=entity.pe,
            pbv=entity.pbv,
            roe=entity.roe,
            roa=entity.roa,
            debt_ratio=entity.debt_ratio,
            dividend_yield=entity.dividend_yield,
            last_financial_update=entity.last_financial_update,
        )
