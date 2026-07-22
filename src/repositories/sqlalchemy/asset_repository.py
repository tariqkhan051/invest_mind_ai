"""SQLAlchemy asset repository implementation."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.core.exceptions import FundNotFoundError, StockNotFoundError
from src.database.mappers.asset_mapper import AssetMapper, MutualFundMapper, StockMapper
from src.database.models.asset import AssetModel, MutualFundModel, StockModel
from src.domain.entities.asset import Asset
from src.domain.entities.mutual_fund import MutualFund
from src.domain.entities.stock import Stock
from src.domain.enums import AssetType
from src.repositories.interfaces.asset_repository import (
    MUTUAL_FUND_TYPES,
    AssetRepository,
)


class SqlAlchemyAssetRepository(AssetRepository):
    """Asset persistence using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, asset_id: UUID) -> Asset | None:
        model = self._session.get(AssetModel, asset_id)
        if model is None or model.deleted_at is not None:
            return None
        return AssetMapper.to_entity(model)

    def get_by_symbol(self, symbol: str) -> Asset | None:
        stmt = select(AssetModel).where(
            AssetModel.symbol == symbol,
            AssetModel.deleted_at.is_(None),
        )
        model = self._session.scalar(stmt)
        return AssetMapper.to_entity(model) if model else None

    def find_by_type(self, asset_type: AssetType) -> list[Asset]:
        stmt = select(AssetModel).where(
            AssetModel.asset_type == asset_type.value,
            AssetModel.deleted_at.is_(None),
        )
        return [AssetMapper.to_entity(row) for row in self._session.scalars(stmt)]

    def save(self, asset: Asset) -> Asset:
        asset.validate()
        model = self._session.get(AssetModel, asset.id)
        if model is None:
            model = AssetMapper.to_model(asset)
            self._session.add(model)
        else:
            AssetMapper.update_model(model, asset)
        self._session.flush()
        return AssetMapper.to_entity(model)

    def get_mutual_fund(self, asset_id: UUID) -> MutualFund | None:
        stmt = (
            select(MutualFundModel)
            .options(joinedload(MutualFundModel.asset))
            .where(MutualFundModel.asset_id == asset_id)
        )
        model = self._session.scalar(stmt)
        if model is None:
            return None
        asset = AssetMapper.to_entity(model.asset)
        return MutualFundMapper.to_entity(model, asset)

    def save_mutual_fund(self, mutual_fund: MutualFund) -> MutualFund:
        mutual_fund.validate()
        self.save(mutual_fund.asset)
        model = self._session.get(MutualFundModel, mutual_fund.asset_id)
        if model is None:
            model = MutualFundMapper.to_model(mutual_fund)
            self._session.add(model)
        else:
            updated = MutualFundMapper.to_model(mutual_fund)
            for column in MutualFundModel.__table__.columns:
                setattr(model, column.name, getattr(updated, column.name))
        self._session.flush()
        saved = self.get_mutual_fund(mutual_fund.asset_id)
        if saved is None:
            raise FundNotFoundError(f"Mutual fund {mutual_fund.asset_id} not found.")
        return saved

    def get_stock(self, asset_id: UUID) -> Stock | None:
        stmt = (
            select(StockModel)
            .options(joinedload(StockModel.asset))
            .where(StockModel.asset_id == asset_id)
        )
        model = self._session.scalar(stmt)
        if model is None:
            return None
        asset = AssetMapper.to_entity(model.asset)
        return StockMapper.to_entity(model, asset)

    def save_stock(self, stock: Stock) -> Stock:
        stock.validate()
        self.save(stock.asset)
        model = self._session.get(StockModel, stock.asset_id)
        if model is None:
            model = StockMapper.to_model(stock)
            self._session.add(model)
        else:
            updated = StockMapper.to_model(stock)
            for column in StockModel.__table__.columns:
                setattr(model, column.name, getattr(updated, column.name))
        self._session.flush()
        saved = self.get_stock(stock.asset_id)
        if saved is None:
            raise StockNotFoundError(f"Stock {stock.asset_id} not found.")
        return saved

    def list_mutual_funds(
        self,
        shariah_only: bool = False,
        asset_type: AssetType | None = None,
    ) -> list[MutualFund]:
        fund_types = {asset_type} if asset_type else MUTUAL_FUND_TYPES
        stmt = (
            select(MutualFundModel)
            .options(joinedload(MutualFundModel.asset))
            .join(AssetModel, MutualFundModel.asset_id == AssetModel.id)
            .where(
                AssetModel.asset_type.in_([item.value for item in fund_types]),
                AssetModel.deleted_at.is_(None),
            )
        )
        if shariah_only:
            stmt = stmt.where(AssetModel.is_shariah.is_(True))

        models = self._session.scalars(stmt).unique().all()
        results: list[MutualFund] = []
        for model in models:
            asset = AssetMapper.to_entity(model.asset)
            results.append(MutualFundMapper.to_entity(model, asset))
        return results

    def list_stocks(
        self,
        shariah_only: bool = False,
        sector: str | None = None,
    ) -> list[Stock]:
        stmt = (
            select(StockModel)
            .options(joinedload(StockModel.asset))
            .join(AssetModel, StockModel.asset_id == AssetModel.id)
            .where(
                AssetModel.asset_type == AssetType.STOCK.value,
                AssetModel.deleted_at.is_(None),
            )
        )
        if shariah_only:
            stmt = stmt.where(AssetModel.is_shariah.is_(True))
        if sector:
            stmt = stmt.where(StockModel.industry == sector)

        models = self._session.scalars(stmt).unique().all()
        results: list[Stock] = []
        for model in models:
            asset = AssetMapper.to_entity(model.asset)
            results.append(StockMapper.to_entity(model, asset))
        return results

    def get_stock_by_symbol(self, symbol: str) -> Stock | None:
        asset = self.get_by_symbol(symbol)
        if asset is None or asset.asset_type != AssetType.STOCK:
            return None
        return self.get_stock(asset.id)
