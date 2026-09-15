import { useEffect, useState } from "react";

import { fetchReport, fetchReports, generateReport } from "../api/client";
import { PageState } from "../components/PageState";
import { StatCard } from "../components/StatCard";
import type { ReportDetail, ReportSummary } from "../types/api";
import { formatDate, formatDateTime } from "../utils/format";

type ReportType = "daily" | "weekly" | "monthly" | "yearly";

export function ReportsPage() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [selected, setSelected] = useState<ReportDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState<ReportType | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const history = await fetchReports(1, 30);
      setReports(history.items);
      setError(null);
      if (history.items[0] && !selected) {
        const detail = await fetchReport(history.items[0].id);
        setSelected(detail);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openReport = async (reportId: string) => {
    try {
      const detail = await fetchReport(reportId);
      setSelected(detail);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to open report");
    }
  };

  const handleGenerate = async (reportType: ReportType) => {
    setGenerating(reportType);
    try {
      const report = await generateReport(reportType);
      setSelected(report);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Report generation failed");
    } finally {
      setGenerating(null);
    }
  };

  if (loading && reports.length === 0) {
    return <PageState loading error={null} />;
  }

  if (error && reports.length === 0 && !selected) {
    return <PageState loading={false} error={error} />;
  }

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Reports</p>
          <h1>Investment Reports</h1>
          <p className="subtitle">Generate and review daily, weekly, and monthly reports.</p>
        </div>
      </header>

      {error ? <p className="page-state error">{error}</p> : null}

      <section className="stat-grid">
        <StatCard label="Stored Reports" value={String(reports.length)} />
        <StatCard
          label="Selected"
          value={selected ? selected.report_type : "None"}
        />
        <StatCard
          label="Period"
          value={
            selected
              ? `${formatDate(selected.period_start)} → ${formatDate(selected.period_end)}`
              : "—"
          }
        />
        <StatCard
          label="Generated"
          value={selected ? formatDateTime(selected.generated_at) : "—"}
        />
      </section>

      <section className="action-row wrap">
        {(["daily", "weekly", "monthly", "yearly"] as ReportType[]).map((type) => (
          <button
            key={type}
            type="button"
            className="primary-button"
            disabled={generating !== null}
            onClick={() => void handleGenerate(type)}
          >
            {generating === type ? `Generating ${type}...` : `Generate ${type}`}
          </button>
        ))}
      </section>

      <section className="split-grid">
        <div className="chart-card">
          <h3>Report History</h3>
          {reports.length === 0 ? (
            <p className="empty-state">No reports yet. Generate one to get started.</p>
          ) : (
            <ul className="activity-list">
              {reports.map((report) => (
                <li key={report.id}>
                  <div>
                    <button
                      type="button"
                      className="link-button"
                      onClick={() => void openReport(report.id)}
                    >
                      <strong>{report.title}</strong>
                    </button>
                    <p>
                      {report.report_type} · {formatDate(report.period_start)} to{" "}
                      {formatDate(report.period_end)}
                    </p>
                  </div>
                  <span>{formatDateTime(report.generated_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="chart-card">
          <h3>Report Content</h3>
          {!selected ? (
            <p className="empty-state">Select a report to view its content.</p>
          ) : selected.html_content ? (
            <div
              className="report-content"
              dangerouslySetInnerHTML={{ __html: selected.html_content }}
            />
          ) : (
            <pre className="report-markdown">{selected.markdown_content}</pre>
          )}
        </div>
      </section>
    </div>
  );
}
