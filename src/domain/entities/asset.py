"""Asset entity — base investable instrument."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

from src.core.exceptions import PortfolioValidationError
from src.domain.enums import AssetStatus, AssetType


@dataclass
class Asset:
    """Unified investable instrument."""

    id: UUID = field(default_factory=uuid4)
    symbol: str = ""
    display_name: str = ""
    short_name: str | None = None
    asset_type: AssetType = AssetType.MUTUAL_FUND
    currency: str = "PKR"
    country: str = "PK"
    exchange: str | None = None
    is_shariah: bool = True
    status: AssetStatus = AssetStatus.ACTIVE
    launch_date: date | None = None
    provider: str | None = None
    metadata_json: dict[str, str] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def validate(self) -> None:
        """Validate asset invariants."""
        if not self.symbol.strip():
            raise PortfolioValidationError("Asset symbol is required.")
        if not self.display_name.strip():
            raise PortfolioValidationError("Asset display name is required.")

    def is_active(self) -> bool:
        """Return True when the asset is active."""
        return self.status == AssetStatus.ACTIVE and self.deleted_at is None

    def is_shariah_compliant(self) -> bool:
        """Return True when the asset is Shariah compliant."""
        return self.is_shariah
