import { useEffect, useState } from "react";

import { fetchDashboard } from "../api/client";
import { ActivityFeed } from "../components/ActivityFeed";
import { AllocationChart } from "../components/AllocationChart";
import { GrowthChart } from "../components/GrowthChart";
import { RecommendationCard } from "../components/RecommendationCard";
import { StatCard } from "../components/StatCard";
import type { DashboardData } from "../types/dashboard";

function formatCurrency(value: string, currency = "PKR") {
  const amount = Number(value);
  return `${currency} ${amount.toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
}

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard()
      .then((dashboard) => setData(dashboard))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="page-state">Loading dashboard...</p>;
  }

  if (error || !data) {
    return <p className="page-state error">{error ?? "Dashboard unavailable"}</p>;
  }

  const portfolio = data.portfolio_summary;
  const market = data.market_summary;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h1>{portfolio.portfolio.name}</h1>
          <p className="subtitle">
            Market regime: <strong>{market.regime.regime}</strong> · Sentiment:{" "}
            {market.sentiment.dominant_sentiment}
          </p>
        </div>
        <div className="market-score">
          <span>Market Score</span>
          <strong>{Number(market.score.overall_score).toFixed(1)}</strong>
        </div>
      </header>

      <section className="stat-grid">
        <StatCard
          label="Portfolio Value"
          value={formatCurrency(portfolio.portfolio_value)}
        />
        <StatCard
          label="Total Return"
          value={`${Number(portfolio.total_return_percentage).toFixed(2)}%`}
        />
        <StatCard
          label="Cash Balance"
          value={formatCurrency(portfolio.cash)}
          hint={`${Number(portfolio.allocation.cash_percentage).toFixed(1)}% cash`}
        />
        <StatCard
          label="XIRR"
          value={
            portfolio.xirr
              ? `${Number(portfolio.xirr).toFixed(2)}%`
              : "Not available"
          }
        />
      </section>

      <section className="chart-grid">
        <AllocationChart data={data.charts.allocation} />
        <GrowthChart data={data.charts.portfolio_growth} />
      </section>

      <section className="split-grid">
        <div className="chart-card">
          <h3>Today&apos;s Actions</h3>
          <p className="section-hint">
            What to do with cash and watchlist names based on live fund/stock data.
          </p>
          {data.latest_recommendations.length === 0 ? (
            <p className="empty-state">No recommendations yet.</p>
          ) : (
            <div className="recommendation-list">
              {data.latest_recommendations.map((item) => (
                <RecommendationCard key={item.id} recommendation={item} />
              ))}
            </div>
          )}
        </div>
        <ActivityFeed items={data.recent_activity} />
      </section>
    </div>
  );
}
