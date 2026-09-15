import { useEffect, useState } from "react";

import {
  createTransaction,
  fetchFunds,
  fetchHoldings,
  fetchLatestRecommendations,
  fetchRecommendationHistory,
  fetchStocks,
  runRecommendationCycle,
  submitRecommendationFeedback,
} from "../api/client";
import { PageState } from "../components/PageState";
import { RecommendationCard } from "../components/RecommendationCard";
import { StatCard } from "../components/StatCard";
import type { Recommendation } from "../types/api";
import { formatCurrency, formatDateTime, formatPercent } from "../utils/format";
import { buildRecommendationAction } from "../utils/recommendationAction";

function parseNumber(value: string | null | undefined) {
  if (!value) return null;
  const amount = Number(value);
  return Number.isFinite(amount) ? amount : null;
}

async function resolvePrice(assetId: string, fallback?: number | null) {
  const [holdings, funds, stocks] = await Promise.all([
    fetchHoldings(),
    fetchFunds(false),
    fetchStocks(false),
  ]);
  const holding = holdings.find((item) => item.asset_id === assetId);
  const holdingPrice = parseNumber(holding?.current_price);
  if (holdingPrice && holdingPrice > 0) return holdingPrice;

  const fund = funds.find((item) => item.asset_id === assetId);
  const fundNav = parseNumber(fund?.latest_nav);
  if (fundNav && fundNav > 0) return fundNav;

  const stock = stocks.find((item) => item.asset_id === assetId);
  const stockPrice = parseNumber(stock?.latest_price);
  if (stockPrice && stockPrice > 0) return stockPrice;

  if (fallback && fallback > 0) return fallback;
  return 1;
}

async function applyRecommendation(recommendation: Recommendation) {
  const amount =
    parseNumber(recommendation.recommended_amount) ??
    parseNumber(recommendation.supporting_evidence?.recommended_amount);
  const type = recommendation.recommendation_type;

  if (type === "hold_cash" || type === "wait" || type === "no_action") {
    await submitRecommendationFeedback(recommendation.id, "accepted");
    return "Marked as accepted. No portfolio change required.";
  }

  if (type === "switch") {
    const fromId = recommendation.from_asset_id;
    const toId = recommendation.to_asset_id;
    if (!fromId || !toId) {
      throw new Error("Switch recommendation is missing source/destination assets.");
    }
    if (!amount || amount <= 0) {
      throw new Error("Switch recommendation has no amount to move.");
    }
    const fromPrice = await resolvePrice(fromId);
    const toPrice = await resolvePrice(toId);
    const outUnits = Number((amount / fromPrice).toFixed(6));
    const inUnits = Number((amount / toPrice).toFixed(6));
    await createTransaction({
      asset_id: fromId,
      transaction_type: "switch_out",
      units: outUnits,
      price: fromPrice,
      notes: `Applied AI switch from ${recommendation.from_symbol ?? "source"}`,
      source: "ai_recommendation",
    });
    await createTransaction({
      asset_id: toId,
      transaction_type: "switch_in",
      units: inUnits,
      price: toPrice,
      notes: `Applied AI switch to ${recommendation.to_symbol ?? "destination"}`,
      source: "ai_recommendation",
    });
    await submitRecommendationFeedback(
      recommendation.id,
      "accepted",
      `Applied move of ${amount}`,
    );
    return `Moved ${formatCurrency(amount)} from ${recommendation.from_symbol} to ${recommendation.to_symbol}.`;
  }

  const assetId = recommendation.asset_id;
  if (!assetId) {
    throw new Error("Recommendation is missing target asset.");
  }
  if (!amount || amount <= 0) {
    throw new Error("Recommendation has no invest/buy amount.");
  }

  const evidencePrice =
    parseNumber(recommendation.supporting_evidence?.latest_nav) ??
    parseNumber(recommendation.supporting_evidence?.latest_price);
  const price = await resolvePrice(assetId, evidencePrice);
  const units = Number((amount / price).toFixed(6));
  const transactionType = type === "continue_sip" ? "automatic_sip" : "buy";

  await createTransaction({
    asset_id: assetId,
    transaction_type: transactionType,
    units,
    price,
    notes: `Applied AI recommendation (${type})`,
    source: "ai_recommendation",
  });
  await submitRecommendationFeedback(
    recommendation.id,
    "accepted",
    `Applied ${transactionType} of ${amount}`,
  );
  return `Applied ${formatCurrency(amount)} into ${recommendation.symbol ?? "asset"}.`;
}

export function RecommendationsPage() {
  const [latest, setLatest] = useState<Recommendation[]>([]);
  const [history, setHistory] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [latestData, historyData] = await Promise.all([
        fetchLatestRecommendations(),
        fetchRecommendationHistory(1, 25),
      ]);
      setLatest(latestData);
      setHistory(historyData.items);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleFeedback = async (
    recommendationId: string,
    action: "accepted" | "rejected" | "ignored",
  ) => {
    setBusyId(recommendationId);
    setInfo(null);
    try {
      await submitRecommendationFeedback(recommendationId, action);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Feedback failed");
    } finally {
      setBusyId(null);
    }
  };

  const handleApply = async (recommendation: Recommendation) => {
    setBusyId(recommendation.id);
    setInfo(null);
    try {
      const message = await applyRecommendation(recommendation);
      setInfo(message);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to apply recommendation");
    } finally {
      setBusyId(null);
    }
  };

  const handleRun = async () => {
    setRunning(true);
    setInfo(null);
    try {
      await runRecommendationCycle();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Recommendation run failed");
    } finally {
      setRunning(false);
    }
  };

  if (loading && latest.length === 0 && history.length === 0) {
    return <PageState loading error={null} />;
  }

  if (error && latest.length === 0 && history.length === 0) {
    return <PageState loading={false} error={error} />;
  }

  const accepted = history.filter((item) => item.feedback_action === "accepted").length;
  const rejected = history.filter((item) => item.feedback_action === "rejected").length;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Recommendations</p>
          <h1>AI Decision Engine</h1>
          <p className="subtitle">
            Actionable moves: invest, buy, or switch a specific amount between funds/stocks.
          </p>
        </div>
        <button
          type="button"
          className="primary-button"
          onClick={() => void handleRun()}
          disabled={running}
        >
          {running ? "Running..." : "Run AI Cycle"}
        </button>
      </header>

      {error ? <p className="page-state error">{error}</p> : null}
      {info ? <p className="form-success">{info}</p> : null}

      <section className="stat-grid">
        <StatCard label="Latest" value={String(latest.length)} />
        <StatCard label="History" value={String(history.length)} />
        <StatCard label="Accepted" value={String(accepted)} />
        <StatCard label="Rejected" value={String(rejected)} />
      </section>

      <section className="chart-card">
        <h3>Suggested Moves</h3>
        {latest.length === 0 ? (
          <p className="empty-state">No latest recommendations. Run an AI cycle.</p>
        ) : (
          <div className="recommendation-list">
            {latest.map((item) => {
              const action = buildRecommendationAction(item);
              return (
                <div key={item.id} className="recommendation-block">
                  <RecommendationCard recommendation={item} />
                  {item.explanation ? (
                    <p className="section-hint">{item.explanation}</p>
                  ) : null}
                  <div className="action-row">
                    <button
                      type="button"
                      className="primary-button"
                      disabled={busyId === item.id}
                      onClick={() => void handleApply(item)}
                    >
                      {busyId === item.id ? "Applying..." : "Apply move"}
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      disabled={busyId === item.id}
                      onClick={() => void handleFeedback(item.id, "accepted")}
                    >
                      Accept only
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      disabled={busyId === item.id}
                      onClick={() => void handleFeedback(item.id, "rejected")}
                    >
                      Reject
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      disabled={busyId === item.id}
                      onClick={() => void handleFeedback(item.id, "ignored")}
                    >
                      Ignore
                    </button>
                  </div>
                  {action.routeLabel ? (
                    <p className="action-meta">Route: {action.routeLabel}</p>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </section>

      <section className="chart-card">
        <h3>Recommendation History</h3>
        {history.length === 0 ? (
          <p className="empty-state">No recommendation history yet.</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Generated</th>
                  <th>Suggested move</th>
                  <th>Amount</th>
                  <th>Confidence</th>
                  <th>Status</th>
                  <th>Feedback</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => {
                  const action = buildRecommendationAction(item);
                  return (
                    <tr key={item.id}>
                      <td>{formatDateTime(item.generated_at)}</td>
                      <td>{action.headline}</td>
                      <td>
                        {item.recommended_amount
                          ? formatCurrency(item.recommended_amount)
                          : "—"}
                      </td>
                      <td>{formatPercent(item.confidence, 0)}</td>
                      <td>{item.status}</td>
                      <td>{item.feedback_action ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
