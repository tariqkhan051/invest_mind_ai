"""Evaluate recommendation outcomes against market data."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.entities.recommendation import Recommendation
from src.domain.enums import LearningOutcome, RecommendationType
from src.repositories.interfaces.market_data_repository import MarketDataRepository

ACCURACY_THRESHOLD = Decimal("2")
PARTIAL_THRESHOLD = Decimal("5")


def calculate_actual_return(
    recommendation: Recommendation,
    market_data_repository: MarketDataRepository,
    evaluation_date: date | None = None,
) -> Decimal | None:
    """Compute realized return for an asset-linked recommendation."""
    asset_id = _resolve_asset_id(recommendation)
    if asset_id is None:
        return None

    start_date = recommendation.generated_at.date()
    end_date = evaluation_date or date.today()
    nav_history = market_data_repository.get_nav_history(
        asset_id,
        from_date=start_date,
        to_date=end_date,
    )
    if len(nav_history) >= 2:
        start_nav = nav_history[0].nav
        end_nav = nav_history[-1].nav
        if start_nav > 0:
            return ((end_nav - start_nav) / start_nav) * Decimal("100")

    price_history = market_data_repository.get_price_history(
        asset_id,
        from_date=start_date,
        to_date=end_date,
    )
    if len(price_history) >= 2:
        start_price = price_history[0].close_price
        end_price = price_history[-1].close_price
        if start_price > 0:
            return ((end_price - start_price) / start_price) * Decimal("100")
    return None


def classify_outcome(
    expected_return: Decimal | None,
    actual_return: Decimal | None,
    recommendation_type: RecommendationType,
) -> LearningOutcome:
    """Classify how well the recommendation matched reality."""
    if recommendation_type in {
        RecommendationType.NO_ACTION,
        RecommendationType.HOLD_CASH,
        RecommendationType.WAIT,
    }:
        return LearningOutcome.NO_OUTCOME
    if actual_return is None:
        return LearningOutcome.UNKNOWN
    if expected_return is None:
        if actual_return >= Decimal("0"):
            return LearningOutcome.PARTIALLY_ACCURATE
        return LearningOutcome.INACCURATE

    error = abs(expected_return - actual_return)
    if error <= ACCURACY_THRESHOLD:
        return LearningOutcome.ACCURATE
    if error <= PARTIAL_THRESHOLD:
        return LearningOutcome.PARTIALLY_ACCURATE
    return LearningOutcome.INACCURATE


def calculate_prediction_error(
    expected_return: Decimal | None,
    actual_return: Decimal | None,
) -> Decimal | None:
    """Return absolute difference between expected and actual return."""
    if expected_return is None or actual_return is None:
        return None
    return abs(expected_return - actual_return)


def _resolve_asset_id(recommendation: Recommendation) -> UUID | None:
    if recommendation.recommendation_type == RecommendationType.SWITCH:
        return recommendation.to_asset_id
    return recommendation.asset_id
