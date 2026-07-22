import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Layout>
      <DashboardPage />
    </Layout>
  </StrictMode>,
);
