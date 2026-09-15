import { useCallback, useEffect, useMemo, useState } from "react";

import {
  fetchAssets,
  fetchHoldings,
  fetchPerformance,
  fetchPortfolioSummary,
  fetchSnapshots,
  fetchTransactions,
} from "../api/client";
import { AllocationChart } from "../components/AllocationChart";
import { GrowthChart } from "../components/GrowthChart";
import { PageState } from "../components/PageState";
import { StatCard } from "../components/StatCard";
import {
  TransactionForm,
  type InputMode,
} from "../components/TransactionForm";
import type {
  Asset,
  Holding,
  PortfolioPerformance,
  PortfolioSnapshot,
  PortfolioSummary,
  Transaction,
} from "../types/api";
import {
  formatCurrency,
  formatDate,
  formatDateTime,
  formatNumber,
  formatPercent,
} from "../utils/format";

function assetLabel(assetsById: Map<string, Asset>, assetId: string | null) {
  if (!assetId) return "—";
  const asset = assetsById.get(assetId);
  return asset ? `${asset.symbol}` : `${assetId.slice(0, 8)}…`;
}

export function PortfolioPage() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [snapshots, setSnapshots] = useState<PortfolioSnapshot[]>([]);
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [formPrefill, setFormPrefill] = useState<
    | {
        mode: InputMode;
        assetId?: string;
        fromAssetId?: string;
        toAssetId?: string;
        amount?: string;
        price?: string;
        notes?: string;
      }
    | undefined
  >(undefined);

  const load = useCallback(async () => {
    const [
      summaryData,
      holdingsData,
      txData,
      snapshotData,
      performanceData,
      assetsData,
    ] = await Promise.all([
      fetchPortfolioSummary(),
      fetchHoldings(),
      fetchTransactions(1, 100),
      fetchSnapshots(),
      fetchPerformance(),
      fetchAssets(),
    ]);
    setSummary(summaryData);
    setHoldings(holdingsData);
    setTransactions(txData.items);
    setSnapshots(snapshotData);
    setPerformance(performanceData);
    setAssets(assetsData);
  }, []);

  useEffect(() => {
    load()
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [load]);

  const assetsById = useMemo(
    () => new Map(assets.map((asset) => [asset.id, asset])),
    [assets],
  );

  const holdingsByAssetId = useMemo(
    () => new Map(holdings.map((holding) => [holding.asset_id, holding])),
    [holdings],
  );

  if (loading || error || !summary) {
    return (
      <PageState
        loading={loading}
        error={error ?? (!summary ? "Portfolio unavailable" : null)}
      />
    );
  }

  const allocation = Object.entries(summary.allocation.by_asset_type).map(
    ([label, value]) => ({ label, value }),
  );
  const growth = snapshots
    .slice()
    .reverse()
    .map((snapshot) => ({
      label: snapshot.snapshot_date,
      value: snapshot.total_value,
    }));

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Portfolio</p>
          <h1>{summary.portfolio.name}</h1>
          <p className="subtitle">
            Risk profile: <strong>{summary.portfolio.risk_profile}</strong> · Currency:{" "}
            {summary.portfolio.base_currency}
          </p>
        </div>
      </header>

      <section className="stat-grid">
        <StatCard label="Portfolio Value" value={formatCurrency(summary.portfolio_value)} />
        <StatCard label="Investment Value" value={formatCurrency(summary.investment_value)} />
        <StatCard label="Cash" value={formatCurrency(summary.cash)} />
        <StatCard
          label="Total Return"
          value={formatPercent(summary.total_return_percentage)}
          hint={
            performance?.xirr
              ? `XIRR ${formatPercent(performance.xirr)}`
              : summary.xirr
                ? `XIRR ${formatPercent(summary.xirr)}`
                : undefined
          }
        />
      </section>

      <section className="chart-card">
        <h3>Record Input</h3>
        <p className="section-hint">
          Enter cash deposits, buys, sells, SIP, or switches. Holdings are recalculated from
          transaction history — never edited directly.
        </p>
        <TransactionForm
          assets={assets}
          prefills={formPrefill}
          onCreated={async () => {
            setFormPrefill(undefined);
            await load();
          }}
        />
      </section>

      <section className="chart-grid">
        <AllocationChart data={allocation} />
        <GrowthChart data={growth} />
      </section>

      <section className="chart-card">
        <h3>Current Holdings</h3>
        {holdings.length === 0 ? (
          <p className="empty-state">No holdings yet. Record a buy or SIP above.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>Qty</th>
                  <th>Avg Cost</th>
                  <th>Live Price</th>
                  <th>Current Value</th>
                  <th>Unrealized</th>
                  <th>Alloc %</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => (
                  <tr key={holding.id}>
                    <td>{assetLabel(assetsById, holding.asset_id)}</td>
                    <td>{holding.asset_type}</td>
                    <td>{formatNumber(holding.quantity, 4)}</td>
                    <td>{formatCurrency(holding.average_cost)}</td>
                    <td>{formatCurrency(holding.current_price)}</td>
                    <td>{formatCurrency(holding.current_value)}</td>
                    <td>{formatCurrency(holding.unrealized_gain)}</td>
                    <td>{formatPercent(holding.allocation_percentage, 1)}</td>
                    <td>
                      <button
                        type="button"
                        className="link-button"
                        onClick={() =>
                          setFormPrefill({
                            mode: "sell",
                            assetId: holding.asset_id,
                            price: holding.current_price,
                            notes: `Sell from ${assetLabel(assetsById, holding.asset_id)}`,
                          })
                        }
                      >
                        Sell
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="chart-card">
        <h3>Input History</h3>
        <p className="section-hint">
          Every amount you entered into the system, with what it was worth then and what that
          holding is worth now.
        </p>
        {transactions.length === 0 ? (
          <p className="empty-state">No transactions yet.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>When</th>
                  <th>Input</th>
                  <th>Asset</th>
                  <th>Units @ Price</th>
                  <th>Amount Then</th>
                  <th>Holding Now</th>
                  <th>Source</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((tx) => {
                  const holding = tx.asset_id
                    ? holdingsByAssetId.get(tx.asset_id)
                    : undefined;
                  return (
                    <tr key={tx.id}>
                      <td>
                        <div>{formatDate(tx.transaction_date)}</div>
                        <div className="muted">{formatDateTime(tx.created_at)}</div>
                      </td>
                      <td>
                        <span className="pill">{tx.transaction_type}</span>
                      </td>
                      <td>{assetLabel(assetsById, tx.asset_id)}</td>
                      <td>
                        {tx.transaction_type === "adjustment"
                          ? "—"
                          : `${formatNumber(tx.units, 4)} @ ${formatCurrency(tx.price)}`}
                      </td>
                      <td>{formatCurrency(tx.net_amount)}</td>
                      <td>
                        {holding
                          ? formatCurrency(holding.current_value)
                          : "—"}
                      </td>
                      <td>{tx.source}</td>
                      <td>{tx.notes ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="chart-card">
        <h3>Snapshots</h3>
        {snapshots.length === 0 ? (
          <p className="empty-state">No snapshots yet.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Total Value</th>
                  <th>Investment</th>
                  <th>Cash</th>
                  <th>XIRR</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {snapshots.slice(0, 15).map((snapshot) => (
                  <tr key={snapshot.id}>
                    <td>{formatDate(snapshot.snapshot_date)}</td>
                    <td>{formatCurrency(snapshot.total_value)}</td>
                    <td>{formatCurrency(snapshot.investment_value)}</td>
                    <td>{formatCurrency(snapshot.cash_value)}</td>
                    <td>{formatPercent(snapshot.xirr)}</td>
                    <td>{formatDateTime(snapshot.created_at)}</td>
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
