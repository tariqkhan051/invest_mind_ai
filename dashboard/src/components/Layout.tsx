import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

const NAV_ITEMS = [
  "Dashboard",
  "Portfolio",
  "Funds",
  "Stocks",
  "Recommendations",
  "Market",
  "Reports",
];

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">IM</span>
          <div>
            <strong>InvestMind AI</strong>
            <p>Shariah-compliant advisor</p>
          </div>
        </div>
        <nav>
          {NAV_ITEMS.map((item, index) => (
            <a
              key={item}
              href="#"
              className={index === 0 ? "nav-link active" : "nav-link"}
            >
              {item}
            </a>
          ))}
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
