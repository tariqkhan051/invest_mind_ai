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
  };
  portfolio_value: string;
  cash: string;
  investment_value: string;
  total_return_percentage: string;
  xirr: string | null;
  allocation: {
    by_asset_type: Record<string, string>;
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
  recommendation_type: string;
  symbol: string | null;
  confidence: string;
  reason: string;
  status: string;
  generated_at: string;
}

export interface DashboardData {
  portfolio_summary: PortfolioSummary;
  market_summary: MarketSummary;
  latest_recommendations: Recommendation[];
  charts: DashboardCharts;
  recent_activity: ActivityItem[];
}
