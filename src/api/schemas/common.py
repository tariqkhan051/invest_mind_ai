"""Common API response schemas.

See docs/18_API.md §4.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured validation or business error detail."""

    field: str | None = None
    message: str


class ApiResponse[T](BaseModel):
    """Standard success response envelope."""

    success: bool = True
    message: str = "Operation completed"
    data: T | None = None


class ApiErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = False
    message: str
    errors: list[ErrorDetail] = Field(default_factory=list)


class HealthData(BaseModel):
    """Health check payload."""

    status: str
    environment: str
    app_name: str


class ReadinessData(BaseModel):
    """Readiness check payload."""

    status: str
    database: str
    scheduler: str


class VersionData(BaseModel):
    """Application version payload."""

    name: str
    version: str
    api_version: str
    environment: str


class PaginationMeta(BaseModel):
    """Pagination metadata for list endpoints."""

    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedResponse[T](BaseModel):
    """Paginated list response."""

    success: bool = True
    message: str = "Operation completed"
    data: list[Any] = Field(default_factory=list)
    meta: PaginationMeta
