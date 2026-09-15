import { useEffect, useState } from "react";

import {
  fetchFundRankings,
  fetchFunds,
  fetchSwitchOpportunities,
} from "../api/client";
import { PageState } from "../components/PageState";
import { StatCard } from "../components/StatCard";
import type { FundAnalysis, FundRanking, SwitchOpportunity } from "../types/api";
import { formatCurrency, formatDate, formatNumber, formatPercent } from "../utils/format";

export function FundsPage() {
  const [funds, setFunds] = useState<FundAnalysis[]>([]);
  const [rankings, setRankings] = useState<FundRanking[]>([]);
  const [switches, setSwitches] = useState<SwitchOpportunity[]>([]);
  const [shariahOnly, setShariahOnly] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchFunds(shariahOnly),
      fetchFundRankings(15),
      fetchSwitchOpportunities(),
    ])
      .then(([fundsData, rankingsData, switchData]) => {
        setFunds(fundsData);
        setRankings(rankingsData);
        setSwitches(switchData);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [shariahOnly]);

  if (loading || error) {
    return <PageState loading={loading} error={error} />;
  }

  const withNav = funds.filter((fund) => fund.latest_nav).length;
  const avgScore =
    funds.length === 0
      ? null
      : funds.reduce((sum, fund) => sum + Number(fund.ai_score ?? 0), 0) / funds.length;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Funds</p>
          <h1>Mutual Fund Intelligence</h1>
          <p className="subtitle">NAV analysis, rankings, and switch opportunities.</p>
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
        <StatCard label="Funds Tracked" value={String(funds.length)} />
        <StatCard label="With Latest NAV" value={String(withNav)} />
        <StatCard
          label="Avg AI Score"
          value={avgScore === null ? "—" : formatNumber(avgScore, 1)}
        />
        <StatCard label="Switch Ideas" value={String(switches.length)} />
      </section>

      <section className="chart-card">
        <h3>Fund Rankings</h3>
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
                  <th>Volatility</th>
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
                    <td>{formatPercent(item.volatility)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="chart-card">
        <h3>All Funds</h3>
        {funds.length === 0 ? (
          <p className="empty-state">No funds found.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>NAV</th>
                  <th>As Of</th>
                  <th>1Y</th>
                  <th>Vol</th>
                  <th>AI Score</th>
                  <th>Shariah</th>
                </tr>
              </thead>
              <tbody>
                {funds.map((fund) => (
                  <tr key={fund.asset_id}>
                    <td>{fund.symbol}</td>
                    <td>{fund.display_name}</td>
                    <td>{formatCurrency(fund.latest_nav)}</td>
                    <td>{formatDate(fund.latest_nav_date)}</td>
                    <td>{formatPercent(fund.performance.yearly_return)}</td>
                    <td>{formatPercent(fund.risk.volatility)}</td>
                    <td>{formatNumber(fund.ai_score, 1)}</td>
                    <td>{fund.is_shariah ? "Yes" : "No"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="chart-card">
        <h3>Switch Opportunities</h3>
        {switches.length === 0 ? (
          <p className="empty-state">No switch opportunities right now.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>From</th>
                  <th>To</th>
                  <th>Benefit</th>
                  <th>Confidence</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {switches.map((item) => (
                  <tr key={`${item.from_asset_id}-${item.to_asset_id}`}>
                    <td>{item.from_symbol}</td>
                    <td>{item.to_symbol}</td>
                    <td>{formatPercent(item.expected_benefit_pct)}</td>
                    <td>{formatPercent(item.confidence, 0)}</td>
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
