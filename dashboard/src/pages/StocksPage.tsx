import { useEffect, useState } from "react";

import {
  fetchBuyOpportunities,
  fetchStockRankings,
  fetchStocks,
} from "../api/client";
import { PageState } from "../components/PageState";
import { StatCard } from "../components/StatCard";
import type { BuyOpportunity, StockAnalysis, StockRanking } from "../types/api";
import { formatCurrency, formatDate, formatNumber, formatPercent } from "../utils/format";

export function StocksPage() {
  const [stocks, setStocks] = useState<StockAnalysis[]>([]);
  const [rankings, setRankings] = useState<StockRanking[]>([]);
  const [opportunities, setOpportunities] = useState<BuyOpportunity[]>([]);
  const [shariahOnly, setShariahOnly] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchStocks(shariahOnly),
      fetchStockRankings(15),
      fetchBuyOpportunities(),
    ])
      .then(([stocksData, rankingsData, opportunityData]) => {
        setStocks(stocksData);
        setRankings(rankingsData);
        setOpportunities(opportunityData);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [shariahOnly]);

  if (loading || error) {
    return <PageState loading={loading} error={error} />;
  }

  const sectors = new Set(stocks.map((stock) => stock.sector).filter(Boolean)).size;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Stocks</p>
          <h1>PSX Stock Intelligence</h1>
          <p className="subtitle">Prices, rankings, technicals, and buy opportunities.</p>
        </div>
        <label className="filter-toggle">
          <input
            type="checkbox"
            checked={shariahOnly}
            onChange={(event) => setShariahOnly(event.target.checked)}
          />
          Shariah only
        </label>
      </header>

      <section className="stat-grid">
        <StatCard label="Stocks Tracked" value={String(stocks.length)} />
        <StatCard label="Sectors" value={String(sectors)} />
        <StatCard label="Buy Ideas" value={String(opportunities.length)} />
        <StatCard
          label="Top Score"
          value={
            rankings[0]?.ai_score ? formatNumber(rankings[0].ai_score, 1) : "—"
          }
        />
      </section>

      <section className="chart-card">
        <h3>Stock Rankings</h3>
        {rankings.length === 0 ? (
          <p className="empty-state">No rankings available.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>AI Score</th>
                  <th>Yearly Return</th>
                  <th>RSI</th>
                </tr>
              </thead>
              <tbody>
                {rankings.map((item) => (
                  <tr key={item.asset_id}>
                    <td>{item.rank}</td>
                    <td>{item.symbol}</td>
                    <td>{item.display_name}</td>
                    <td>{formatNumber(item.ai_score, 1)}</td>
                    <td>{formatPercent(item.yearly_return)}</td>
                    <td>{formatNumber(item.rsi_14, 1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="chart-card">
        <h3>All Stocks</h3>
        {stocks.length === 0 ? (
          <p className="empty-state">No stocks found.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>Sector</th>
                  <th>Price</th>
                  <th>As Of</th>
                  <th>1Y</th>
                  <th>RSI</th>
                  <th>AI Score</th>
                </tr>
              </thead>
              <tbody>
                {stocks.map((stock) => (
                  <tr key={stock.asset_id}>
                    <td>{stock.symbol}</td>
                    <td>{stock.display_name}</td>
                    <td>{stock.sector ?? "—"}</td>
                    <td>{formatCurrency(stock.latest_price)}</td>
                    <td>{formatDate(stock.latest_price_date)}</td>
                    <td>{formatPercent(stock.performance.yearly_return)}</td>
                    <td>{formatNumber(stock.technicals.rsi_14, 1)}</td>
                    <td>{formatNumber(stock.ai_score, 1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="chart-card">
        <h3>Buy Opportunities</h3>
        {opportunities.length === 0 ? (
          <p className="empty-state">No buy opportunities right now.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>Expected Return</th>
                  <th>Confidence</th>
                  <th>Risk</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {opportunities.map((item) => (
                  <tr key={`${item.asset_id}-${item.opportunity_type}`}>
                    <td>{item.symbol}</td>
                    <td>{item.opportunity_type}</td>
                    <td>{formatPercent(item.expected_return_pct)}</td>
                    <td>{formatPercent(item.confidence, 0)}</td>
                    <td>{item.risk_level ?? "—"}</td>
                    <td>{item.reason}</td>
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
