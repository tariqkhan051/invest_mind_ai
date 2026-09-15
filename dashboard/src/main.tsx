import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";

import { Layout } from "./components/Layout";
import type { AppPage } from "./navigation";
import { DashboardPage } from "./pages/DashboardPage";
import { FundsPage } from "./pages/FundsPage";
import { MarketPage } from "./pages/MarketPage";
import { PortfolioPage } from "./pages/PortfolioPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { StocksPage } from "./pages/StocksPage";
import "./styles.css";

function App() {
  const [activePage, setActivePage] = useState<AppPage>("dashboard");

  let page;
  switch (activePage) {
    case "portfolio":
      page = <PortfolioPage />;
      break;
    case "funds":
      page = <FundsPage />;
      break;
    case "stocks":
      page = <StocksPage />;
      break;
    case "recommendations":
      page = <RecommendationsPage />;
      break;
    case "market":
      page = <MarketPage />;
      break;
    case "reports":
      page = <ReportsPage />;
      break;
    default:
      page = <DashboardPage />;
  }

  return (
    <Layout activePage={activePage} onNavigate={setActivePage}>
      {page}
    </Layout>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
