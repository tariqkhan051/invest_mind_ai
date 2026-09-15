import { useEffect, useState } from "react";

import { fetchMarketSummary } from "../api/client";
import { PageState } from "../components/PageState";
import { StatCard } from "../components/StatCard";
import type { FullMarketSummary } from "../types/api";
import {
  formatDate,
  formatDateTime,
  formatNumber,
  formatPercent,
} from "../utils/format";

export function MarketPage() {
  const [data, setData] = useState<FullMarketSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarketSummary()
      .then((summary) => setData(summary))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading || error || !data) {
    return (
      <PageState
        loading={loading}
        error={error ?? (!data ? "Market summary unavailable" : null)}
      />
    );
  }

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Market</p>
          <h1>Market Intelligence</h1>
          <p className="subtitle">{data.regime.explanation}</p>
        </div>
        <div className="market-score">
          <span>Market Score</span>
          <strong>{Number(data.score.overall_score).toFixed(1)}</strong>
        </div>
      </header>

      <section className="stat-grid">
        <StatCard label="Regime" value={data.regime.regime} />
        <StatCard
          label="Regime Confidence"
          value={formatPercent(data.regime.confidence, 0)}
        />
        <StatCard label="Sentiment" value={data.sentiment.dominant_sentiment} />
        <StatCard
          label="News Mix"
          value={`${data.sentiment.positive_count}/${data.sentiment.neutral_count}/${data.sentiment.negative_count}`}
          hint="Positive / Neutral / Negative"
        />
      </section>

      <section className="stat-grid">
        <StatCard label="Macro Score" value={formatNumber(data.score.macro_score, 1)} />
        <StatCard
          label="Sentiment Score"
          value={formatNumber(data.score.sentiment_score, 1)}
        />
        <StatCard label="Regime Score" value={formatNumber(data.score.regime_score, 1)} />
        <StatCard label="Score Date" value={formatDate(data.score.calculation_date)} />
      </section>

      <section className="split-grid">
        <div className="chart-card">
          <h3>Economic Indicators</h3>
          {data.economy.indicators.length === 0 ? (
            <p className="empty-state">No economic indicators available.</p>
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Indicator</th>
                    <th>Value</th>
                    <th>Unit</th>
                    <th>Trend</th>
                    <th>As Of</th>
                  </tr>
                </thead>
                <tbody>
                  {data.economy.indicators.map((item) => (
                    <tr key={`${item.indicator_name}-${item.release_date}`}>
                      <td>{item.indicator_name}</td>
                      <td>{formatNumber(item.actual_value, 2)}</td>
                      <td>{item.unit ?? "—"}</td>
                      <td>{item.trend ?? "—"}</td>
                      <td>{formatDate(item.release_date)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="chart-card">
          <h3>Signals & Alerts</h3>
          {data.signals.length === 0 && data.alerts.length === 0 ? (
            <p className="empty-state">No active signals or alerts.</p>
          ) : (
            <ul className="activity-list">
              {data.signals.map((signal) => (
                <li key={`${signal.signal_type}-${signal.message}`}>
                  <div>
                    <strong>{signal.signal_type}</strong>
                    <p>{signal.message}</p>
                  </div>
                  <span>{formatPercent(signal.confidence, 0)}</span>
                </li>
              ))}
              {data.alerts.map((alert) => (
                <li key={`${alert.alert_type}-${alert.detected_at}`}>
                  <div>
                    <strong>
                      {alert.severity}: {alert.alert_type}
                    </strong>
                    <p>{alert.message}</p>
                  </div>
                  <span>{formatDateTime(alert.detected_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="chart-card">
        <h3>Latest News</h3>
        {data.latest_news.length === 0 ? (
          <p className="empty-state">No news articles available.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Headline</th>
                  <th>Category</th>
                  <th>Sentiment</th>
                  <th>Publisher</th>
                  <th>Published</th>
                </tr>
              </thead>
              <tbody>
                {data.latest_news.map((article) => (
                  <tr key={article.id}>
                    <td>
                      {article.url ? (
                        <a href={article.url} target="_blank" rel="noreferrer">
                          {article.headline}
                        </a>
                      ) : (
                        article.headline
                      )}
                    </td>
                    <td>{article.category}</td>
                    <td>{article.sentiment}</td>
                    <td>{article.publisher ?? "—"}</td>
                    <td>{formatDateTime(article.publication_time)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
