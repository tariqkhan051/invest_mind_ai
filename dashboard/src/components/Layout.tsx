import type { ReactNode } from "react";

import type { AppPage, NavItem } from "../navigation";
import { NAV_ITEMS } from "../navigation";

interface LayoutProps {
  activePage: AppPage;
  onNavigate: (page: AppPage) => void;
  children: ReactNode;
}

export function Layout({ activePage, onNavigate, children }: LayoutProps) {
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
          {NAV_ITEMS.map((item: NavItem) => (
            <button
              key={item.id}
              type="button"
              className={item.id === activePage ? "nav-link active" : "nav-link"}
              onClick={() => onNavigate(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
