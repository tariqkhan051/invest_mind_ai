import type {
  ApiResponse,
  Asset,
  BuyOpportunity,
  CreateTransactionPayload,
  DashboardData,
  FullMarketSummary,
  FundAnalysis,
  FundRanking,
  Holding,
  PortfolioPerformance,
  PortfolioSnapshot,
  PortfolioSummary,
  Recommendation,
  RecommendationHistory,
  ReportDetail,
  ReportHistory,
  StockAnalysis,
  StockRanking,
  SwitchOpportunity,
  Transaction,
  TransactionList,
} from "../types/api";

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status}) for ${path}`;
    try {
      const body = (await response.json()) as { message?: string; detail?: string };
      detail = body.message || body.detail || detail;
    } catch {
      // keep default detail
    }
    throw new Error(detail);
  }

  const body = (await response.json()) as ApiResponse<T>;
  if (!body.success || body.data === undefined || body.data === null) {
    throw new Error(body.message || `Request failed for ${path}`);
  }
  return body.data;
}

export function fetchDashboard(): Promise<DashboardData> {
  return fetchApi<DashboardData>("/api/v1/dashboard");
}

export function fetchAssets(): Promise<Asset[]> {
  return fetchApi<Asset[]>("/api/v1/assets");
}

export function fetchPortfolioSummary(): Promise<PortfolioSummary> {
  return fetchApi<PortfolioSummary>("/api/v1/portfolio/summary");
}

export function fetchHoldings(): Promise<Holding[]> {
  return fetchApi<Holding[]>("/api/v1/portfolio/holdings");
}

export function fetchTransactions(page = 1, pageSize = 20): Promise<TransactionList> {
  return fetchApi<TransactionList>(
    `/api/v1/portfolio/transactions?page=${page}&page_size=${pageSize}`,
  );
}

export function createTransaction(
  payload: CreateTransactionPayload,
): Promise<Transaction> {
  return fetchApi<Transaction>("/api/v1/portfolio/transactions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchSnapshots(): Promise<PortfolioSnapshot[]> {
  return fetchApi<PortfolioSnapshot[]>("/api/v1/portfolio/snapshots");
}

export function fetchPerformance(): Promise<PortfolioPerformance> {
  return fetchApi<PortfolioPerformance>("/api/v1/portfolio/performance");
}

export function fetchFunds(shariahOnly = false): Promise<FundAnalysis[]> {
  return fetchApi<FundAnalysis[]>(
    `/api/v1/funds?shariah_only=${shariahOnly ? "true" : "false"}`,
  );
}

export function fetchFundRankings(limit = 20): Promise<FundRanking[]> {
  return fetchApi<FundRanking[]>(`/api/v1/funds/rankings?limit=${limit}`);
}

export function fetchSwitchOpportunities(): Promise<SwitchOpportunity[]> {
  return fetchApi<SwitchOpportunity[]>("/api/v1/funds/switch-opportunities");
}

export function fetchStocks(shariahOnly = false): Promise<StockAnalysis[]> {
  return fetchApi<StockAnalysis[]>(
    `/api/v1/stocks?shariah_only=${shariahOnly ? "true" : "false"}`,
  );
}

export function fetchStockRankings(limit = 20): Promise<StockRanking[]> {
  return fetchApi<StockRanking[]>(`/api/v1/stocks/rankings?limit=${limit}`);
}

export function fetchBuyOpportunities(): Promise<BuyOpportunity[]> {
  return fetchApi<BuyOpportunity[]>("/api/v1/stocks/opportunities");
}

export function fetchLatestRecommendations(): Promise<Recommendation[]> {
  return fetchApi<Recommendation[]>("/api/v1/recommendations/latest");
}

export function fetchRecommendationHistory(
  page = 1,
  pageSize = 20,
): Promise<RecommendationHistory> {
  return fetchApi<RecommendationHistory>(
    `/api/v1/recommendations?page=${page}&page_size=${pageSize}`,
  );
}

export function runRecommendationCycle(): Promise<Recommendation[]> {
  return fetchApi<Recommendation[]>("/api/v1/recommendations/run", {
    method: "POST",
  });
}

export function submitRecommendationFeedback(
  recommendationId: string,
  action: "accepted" | "rejected" | "modified" | "ignored",
  notes?: string,
): Promise<Recommendation> {
  return fetchApi<Recommendation>(
    `/api/v1/recommendations/${recommendationId}/feedback`,
    {
      method: "POST",
      body: JSON.stringify({ action, notes: notes ?? null }),
    },
  );
}

export function fetchMarketSummary(): Promise<FullMarketSummary> {
  return fetchApi<FullMarketSummary>("/api/v1/market/summary");
}

export function fetchReports(page = 1, pageSize = 20): Promise<ReportHistory> {
  return fetchApi<ReportHistory>(
    `/api/v1/reports?page=${page}&page_size=${pageSize}`,
  );
}

export function fetchReport(reportId: string): Promise<ReportDetail> {
  return fetchApi<ReportDetail>(`/api/v1/reports/${reportId}`);
}

export function generateReport(
  reportType: "daily" | "weekly" | "monthly" | "yearly",
): Promise<ReportDetail> {
  return fetchApi<ReportDetail>("/api/v1/reports/generate", {
    method: "POST",
    body: JSON.stringify({ report_type: reportType }),
  });
}
