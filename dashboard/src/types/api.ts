export interface Asset {
  id: string;
  symbol: string;
  display_name: string;
  asset_type: string;
  is_shariah: boolean;
  exchange: string | null;
  provider: string | null;
  status: string;
}

export type TransactionType =
  | "buy"
  | "sell"
  | "switch_in"
  | "switch_out"
  | "dividend"
  | "bonus"
  | "adjustment"
  | "fee"
  | "automatic_sip"
  | "manual_investment"
  | "redemption";

export interface CreateTransactionPayload {
  asset_id: string;
  transaction_type: TransactionType;
  units: number;
  price: number;
  gross_amount?: number | null;
  fees?: number;
  taxes?: number;
  transaction_date?: string | null;
  reference_number?: string | null;
  notes?: string | null;
  source?: string;
}

export type {
  ActivityItem,
  ApiResponse,
  ChartPoint,
  DashboardCharts,
  DashboardData,
  MarketSummary,
  PortfolioSummary,
  Recommendation,
} from "./dashboard";

export interface Holding {
  id: string;
  asset_id: string;
  asset_type: string;
  quantity: string;
  average_cost: string;
  current_price: string;
  current_value: string;
  cost_basis: string;
  unrealized_gain: string;
  realized_gain: string;
  allocation_percentage: string;
  currency: string;
  status: string;
}

export interface Transaction {
  id: string;
  portfolio_id: string;
  holding_id: string | null;
  asset_id: string | null;
  transaction_type: string;
  units: string | null;
  price: string | null;
  gross_amount: string;
  fees: string;
  taxes: string;
  net_amount: string;
  reference_number: string | null;
  transaction_date: string;
  settlement_date: string | null;
  notes: string | null;
  source: string;
  status: string;
  created_at: string;
}

export interface TransactionList {
  items: Transaction[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface PortfolioSnapshot {
  id: string;
  portfolio_id: string;
  snapshot_date: string;
  total_value: string;
  investment_value: string;
  cash_value: string;
  xirr: string | null;
  cagr: string | null;
  allocation: Record<string, string>;
  created_at: string;
}

export interface PortfolioPerformance {
  absolute_return: string;
  percentage_return: string;
  xirr: string | null;
  cagr: string | null;
}

export interface FundPerformance {
  daily_return: string | null;
  weekly_return: string | null;
  monthly_return: string | null;
  quarterly_return: string | null;
  yearly_return: string | null;
  cagr_3y: string | null;
  cagr_5y: string | null;
  since_inception_return: string | null;
}

export interface FundRisk {
  volatility: string | null;
  standard_deviation: string | null;
  max_drawdown: string | null;
  downside_risk: string | null;
}

export interface FundAnalysis {
  asset_id: string;
  symbol: string;
  display_name: string;
  asset_type: string;
  is_shariah: boolean;
  management_company: string | null;
  expense_ratio: string | null;
  aum: string | null;
  latest_nav: string | null;
  latest_nav_date: string | null;
  performance: FundPerformance;
  risk: FundRisk;
  ai_score: string | null;
}

export interface FundRanking {
  rank: number;
  asset_id: string;
  symbol: string;
  display_name: string;
  ai_score: string | null;
  yearly_return: string | null;
  volatility: string | null;
}

export interface SwitchOpportunity {
  from_asset_id: string;
  from_symbol: string;
  to_asset_id: string;
  to_symbol: string;
  expected_benefit_pct: string;
  reason: string;
  confidence: string;
}

export interface StockPerformance {
  daily_return: string | null;
  weekly_return: string | null;
  monthly_return: string | null;
  quarterly_return: string | null;
  yearly_return: string | null;
  cagr_3y: string | null;
  volatility: string | null;
  max_drawdown: string | null;
}

export interface TechnicalIndicators {
  sma_20: string | null;
  sma_50: string | null;
  ema_12: string | null;
  rsi_14: string | null;
  momentum: string | null;
  volume_trend: string | null;
}

export interface FundamentalMetrics {
  eps: string | null;
  pe: string | null;
  pbv: string | null;
  roe: string | null;
  roa: string | null;
  debt_ratio: string | null;
  dividend_yield: string | null;
  market_cap: string | null;
}

export interface StockAnalysis {
  asset_id: string;
  symbol: string;
  display_name: string;
  company_name: string | null;
  sector: string | null;
  industry: string | null;
  is_shariah: boolean;
  latest_price: string | null;
  latest_price_date: string | null;
  performance: StockPerformance;
  technicals: TechnicalIndicators;
  fundamentals: FundamentalMetrics;
  ai_score: string | null;
}

export interface StockRanking {
  rank: number;
  asset_id: string;
  symbol: string;
  display_name: string;
  ai_score: string | null;
  yearly_return: string | null;
  rsi_14: string | null;
}

export interface BuyOpportunity {
  asset_id: string;
  symbol: string;
  opportunity_type: string;
  reason: string;
  confidence: string;
  expected_return_pct: string | null;
  risk_level: string | null;
}

export interface RecommendationHistory {
  items: import("./dashboard").Recommendation[];
  meta: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
}

export interface MacroIndicator {
  indicator_name: string;
  release_date: string;
  actual_value: string;
  country: string;
  forecast_value: string | null;
  previous_value: string | null;
  unit: string | null;
  trend: string | null;
  source: string | null;
}

export interface NewsArticle {
  id: string;
  headline: string;
  summary: string | null;
  publisher: string | null;
  publication_time: string;
  url: string | null;
  country: string;
  category: string;
  sentiment: string;
  sentiment_score: string | null;
  source: string;
}

export interface InvestmentSignal {
  signal_type: string;
  message: string;
  confidence: string;
}

export interface MarketAlert {
  alert_type: string;
  severity: string;
  message: string;
  detected_at: string;
}

export interface FullMarketSummary {
  score: {
    overall_score: string;
    macro_score: string;
    sentiment_score: string;
    regime_score: string;
    calculation_date: string;
  };
  regime: {
    regime: string;
    confidence: string;
    explanation: string;
  };
  sentiment: {
    average_score: string;
    positive_count: number;
    neutral_count: number;
    negative_count: number;
    dominant_sentiment: string;
  };
  signals: InvestmentSignal[];
  alerts: MarketAlert[];
  latest_news: NewsArticle[];
  economy: {
    indicators: MacroIndicator[];
  };
  news_by_category: Record<string, number>;
}

export interface ReportSummary {
  id: string;
  portfolio_id: string;
  report_type: string;
  title: string;
  period_start: string;
  period_end: string;
  generated_at: string;
}

export interface ReportDetail extends ReportSummary {
  markdown_content: string;
  html_content: string | null;
}

export interface ReportHistory {
  items: ReportSummary[];
  meta: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
}
