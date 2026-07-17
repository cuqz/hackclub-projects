import { useState, useEffect } from "react";
import { AnimatePresence } from "framer-motion";
import HomePage from "./components/HomePage";
import ContentPage from "./components/ContentPage";
import AIPage from "./components/AIPage";
import CommunityPage from "./components/CommunityPage";
import AlertsPage from "./components/AlertsPage";
import LanguageSelector from "./components/LanguageSelector";

type Page = "home" | "content" | "ai" | "community" | "alerts";

import type { ReactNode } from "react";
const NAV_ICONS: Record<string, ReactNode> = {
  home: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  content: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>,
  ai: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>,
  community: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  alerts: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>,
};

const NAV_ITEMS = [
  { id: "home" as const, label: "Home" },
  { id: "content" as const, label: "Library" },
  { id: "ai" as const, label: "AI Help" },
  { id: "community" as const, label: "Community" },
  { id: "alerts" as const, label: "Alerts" },
];

function App() {
  const [page, setPage] = useState<Page>("home");
  const [language, setLanguage] = useState("en");
  const [offline, setOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const hO = () => setOffline(false);
    const hF = () => setOffline(true);
    window.addEventListener("online", hO);
    window.addEventListener("offline", hF);
    return () => { window.removeEventListener("online", hO); window.removeEventListener("offline", hF); };
  }, []);

  return (
    <div className="min-h-screen" style={{ background: "var(--color-bg)" }}>
      {/* Top Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50" style={{ background: "rgba(10,10,15,0.8)", backdropFilter: "blur(24px) saturate(1.5)", borderBottom: "1px solid var(--color-border)" }}>
        <div className="max-w-2xl mx-auto h-14 flex items-center justify-between px-4">
          <button onClick={() => setPage("home")} className="flex items-center gap-2.5 group">
            <img src="/logo.svg" alt="Bridge" className="h-7" />
          </button>
          <div className="flex items-center gap-3">
            <LanguageSelector current={language} onChange={setLanguage} />
            {offline && (
              <span className="text-[10px] font-semibold px-2.5 py-1 rounded-full" style={{ background: "var(--color-accent-orange)", color: "#000" }}>
                Offline
              </span>
            )}
            {/* Desktop nav */}
            <div className="hidden sm:flex items-center gap-1">
              {NAV_ITEMS.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setPage(item.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200"
                  style={{
                    background: page === item.id ? "rgba(255,255,255,0.06)" : "transparent",
                    color: page === item.id ? "#e8e8e8" : "#555",
                  }}
                >
                  {NAV_ICONS[item.id]}
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Main */}
      <main className="max-w-3xl mx-auto pt-20 pb-28 px-4">
        <AnimatePresence mode="wait">
          {page === "home" && <HomePage key="home" language={language} onNavigate={setPage} />}
          {page === "content" && <ContentPage key="content" language={language} />}
          {page === "ai" && <AIPage key="ai" language={language} />}
          {page === "community" && <CommunityPage key="community" language={language} />}
          {page === "alerts" && <AlertsPage key="alerts" />}
        </AnimatePresence>
      </main>

      {/* Bottom Nav (mobile) */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 sm:hidden" style={{ background: "rgba(10,10,15,0.85)", backdropFilter: "blur(24px) saturate(1.5)", borderTop: "1px solid var(--color-border)" }}>
        <div className="flex pb-safe">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              className="flex-1 flex flex-col items-center gap-0.5 py-2.5 text-[10px] transition-all duration-200"
              style={{ color: page === item.id ? "var(--color-accent)" : "var(--color-text-muted)" }}
            >
              <span className="text-lg" style={{ color: page === item.id ? "#4a9eff" : "#555" }}>{NAV_ICONS[item.id]}</span>
              {item.label}
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}

export default App;
