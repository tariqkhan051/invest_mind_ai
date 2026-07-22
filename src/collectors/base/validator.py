"""Validation helpers for collector data."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from src.collectors.base.models import (
    MacroIndicatorRecord,
    NavRecord,
    NewsRecord,
    PriceRecord,
)


def validate_nav_record(record: NavRecord) -> list[str]:
    """Validate a normalized NAV record."""
    errors: list[str] = []
    if not record.symbol.strip():
        errors.append("Symbol is required.")
    if record.nav <= Decimal("0"):
        errors.append("NAV must be greater than zero.")
    if record.nav_date > date.today():
        errors.append("NAV date cannot be in the future.")
    return errors


def validate_price_record(record: PriceRecord) -> list[str]:
    """Validate a normalized price record."""
    errors: list[str] = []
    if not record.symbol.strip():
        errors.append("Symbol is required.")
    if record.close_price <= Decimal("0"):
        errors.append("Close price must be greater than zero.")
    if record.price_date > date.today():
        errors.append("Price date cannot be in the future.")
    return errors


def validate_macro_record(record: MacroIndicatorRecord) -> list[str]:
    """Validate a normalized macro indicator record."""
    errors: list[str] = []
    if not record.indicator_name.strip():
        errors.append("Indicator name is required.")
    if record.release_date > date.today():
        errors.append("Release date cannot be in the future.")
    return errors


def validate_news_record(record: NewsRecord) -> list[str]:
    """Validate a normalized news record."""
    errors: list[str] = []
    if not record.headline.strip():
        errors.append("Headline is required.")
    if not record.url.strip():
        errors.append("URL is required.")
    if record.publication_time > datetime.now(UTC):
        errors.append("Publication time cannot be in the future.")
    return errors
