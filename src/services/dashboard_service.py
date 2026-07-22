"""Dashboard application service."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from src.core.logging import get_logger
from src.domain.entities.portfolio_snapshot import PortfolioSnapshot
from src.domain.entities.recommendation import Recommendation
from src.engines.dashboard.models import (
    ActivityItem,
    ChartPoint,
    DashboardCharts,
    DashboardData,
)
from src.repositories.interfaces.notification_repository import NotificationRepository
from src.repositories.interfaces.scheduler_job_run_repository import (
    SchedulerJobRunRepository,
)
from src.services.market_intelligence_service import MarketIntelligenceService
from src.services.portfolio_service import PortfolioService
from src.services.recommendation_service import RecommendationService

logger = get_logger("services.dashboard")


class DashboardService:
    """Aggregate portfolio, market, and AI data for the dashboard."""

    def __init__(
        self,
        portfolio_service: PortfolioService,
        market_intelligence_service: MarketIntelligenceService,
        recommendation_service: RecommendationService,
        notification_repository: NotificationRepository | None = None,
        scheduler_job_run_repository: SchedulerJobRunRepository | None = None,
    ) -> None:
        self._portfolio_service = portfolio_service
        self._market_intelligence_service = market_intelligence_service
        self._recommendation_service = recommendation_service
        self._notification_repository = notification_repository
        self._scheduler_job_run_repository = scheduler_job_run_repository

    def get_dashboard(self, portfolio_id: UUID | None = None) -> DashboardData:
        """Build the unified dashboard payload."""
        portfolio_summary = self._portfolio_service.get_summary(portfolio_id)
        market_summary = self._market_intelligence_service.get_summary()
        latest_recommendations = self._recommendation_service.get_latest(portfolio_id)
        snapshots = self._portfolio_service.get_snapshots(portfolio_id)

        charts = DashboardCharts(
            allocation=_allocation_chart(portfolio_summary.allocation.by_asset_type),
            portfolio_growth=_growth_chart(snapshots),
        )
        activity = self._recent_activity(latest_recommendations)

        logger.info(
            "dashboard_loaded portfolio_id={} recommendations={}",
            portfolio_summary.portfolio.id,
            len(latest_recommendations),
        )
        return DashboardData(
            portfolio_summary=portfolio_summary,
            market_summary=market_summary,
            latest_recommendations=latest_recommendations,
            charts=charts,
            recent_activity=activity,
        )

    def _recent_activity(
        self,
        recommendations: list[Recommendation],
    ) -> list[ActivityItem]:
        activity: list[ActivityItem] = []
        for recommendation in recommendations[:3]:
            activity.append(
                ActivityItem(
                    activity_type="recommendation",
                    title=recommendation.reason,
                    description=recommendation.recommendation_type.value,
                    occurred_at=recommendation.generated_at,
                )
            )

        if self._notification_repository is not None:
            for notification in self._notification_repository.list_recent(limit=3):
                activity.append(
                    ActivityItem(
                        activity_type="notification",
                        title=notification.title,
                        description=notification.body,
                        occurred_at=notification.created_at,
                    )
                )

        if self._scheduler_job_run_repository is not None:
            for job_run in self._scheduler_job_run_repository.list_recent(limit=3):
                activity.append(
                    ActivityItem(
                        activity_type="scheduler",
                        title=job_run.job_name,
                        description=job_run.message,
                        occurred_at=job_run.started_at,
                    )
                )

        activity.sort(key=lambda item: item.occurred_at, reverse=True)
        return activity[:8]


def _allocation_chart(allocation: dict[str, Decimal]) -> list[ChartPoint]:
    if not allocation:
        return [ChartPoint(label="cash", value=Decimal("100"))]
    return [
        ChartPoint(label=label, value=value)
        for label, value in sorted(
            allocation.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]


def _growth_chart(snapshots: list[PortfolioSnapshot]) -> list[ChartPoint]:
    ordered = sorted(snapshots, key=lambda item: item.snapshot_date)
    return [
        ChartPoint(
            label=snapshot.snapshot_date.isoformat(),
            value=snapshot.total_value,
        )
        for snapshot in ordered
    ]
