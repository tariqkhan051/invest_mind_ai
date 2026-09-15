export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ChartPoint {
  label: string;
  value: string;
}

export interface DashboardCharts {
  allocation: ChartPoint[];
  portfolio_growth: ChartPoint[];
}

export interface ActivityItem {
  activity_type: string;
  title: string;
  description: string;
  occurred_at: string;
}

export interface PortfolioSummary {
  portfolio: {
    id: string;
    name: string;
    base_currency: string;
    risk_profile: string;
    description?: string | null;
    investment_preference?: string;
    monthly_sip?: string | null;
    status?: string;
  };
  portfolio_value: string;
  cash: string;
  investment_value: string;
  total_invested?: string;
  total_return?: string;
  total_return_percentage: string;
  unrealized_gain?: string;
  realized_gain?: string;
  xirr: string | null;
  cagr?: string | null;
  allocation: {
    by_asset_type: Record<string, string>;
    by_holding?: Record<string, string>;
    cash_percentage: string;
  };
}

export interface MarketSummary {
  score: { overall_score: string };
  regime: { regime: string; explanation: string };
  sentiment: { dominant_sentiment: string };
  latest_news: Array<{ headline: string; sentiment: string }>;
}

export interface Recommendation {
  id: string;
  portfolio_id?: string;
  recommendation_type: string;
  priority?: number;
  asset_id?: string | null;
  from_asset_id?: string | null;
  to_asset_id?: string | null;
  symbol: string | null;
  from_symbol?: string | null;
  to_symbol?: string | null;
  confidence: string;
  reason: string;
  explanation?: string;
  expected_return?: string | null;
  expected_risk?: string;
  recommended_amount?: string | null;
  supporting_evidence?: Record<string, string>;
  status: string;
  feedback_action?: string | null;
  generated_at: string;
  expires_at?: string | null;
}

export interface DashboardData {
  portfolio_summary: PortfolioSummary;
  market_summary: MarketSummary;
  latest_recommendations: Recommendation[];
  charts: DashboardCharts;
  recent_activity: ActivityItem[];
}
