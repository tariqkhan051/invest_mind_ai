export type AppPage =
  | "dashboard"
  | "portfolio"
  | "funds"
  | "stocks"
  | "recommendations"
  | "market"
  | "reports";

export interface NavItem {
  id: AppPage;
  label: string;
}

export const NAV_ITEMS: NavItem[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "portfolio", label: "Portfolio" },
  { id: "funds", label: "Funds" },
  { id: "stocks", label: "Stocks" },
  { id: "recommendations", label: "Recommendations" },
  { id: "market", label: "Market" },
  { id: "reports", label: "Reports" },
];
