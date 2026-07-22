"""Generated investment report entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

from src.domain.enums import ReportType


@dataclass
class Report:
    """Persisted investment report."""

    report_type: ReportType
    title: str
    markdown_content: str
    html_content: str
    id: UUID = field(default_factory=uuid4)
    portfolio_id: UUID | None = None
    period_start: date | None = None
    period_end: date | None = None
    generated_at: datetime = field(default_factory=datetime.utcnow)
