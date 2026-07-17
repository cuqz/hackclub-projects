import { useLocation, Link, Outlet } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Home" },
  { to: "/pricing", label: "Pricing" },
];

export function Layout() {
  const { pathname } = useLocation();
  const isLanding = pathname === "/";

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "hsl(var(--bg))" }}>
      {/* Glass navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50" style={{ background: "rgba(10,10,15,0.75)", backdropFilter: "blur(24px) saturate(1.5)", WebkitBackdropFilter: "blur(24px) saturate(1.5)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
        <div className="max-w-7xl mx-auto h-16 flex items-center justify-between px-6">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold tracking-wider" style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(270 50% 60%))", color: "white" }}>A</div>
            <span className="font-semibold text-sm tracking-tight" style={{ color: "hsl(var(--text))" }}>AGENCY</span>
          </Link>

          <div className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const active = pathname === item.to;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="text-sm px-4 py-2 rounded-lg transition-all duration-200"
                  style={{
                    background: active ? "rgba(255,255,255,0.06)" : "transparent",
                    color: active ? "hsl(var(--text))" : "hsl(var(--text-secondary))",
                  }}
                >
                  {item.label}
                </Link>
              );
            })}
            {!isLanding && (
              <Link
                to="/dashboard"
                className="ml-3 text-sm font-medium px-5 py-2 rounded-xl text-white transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
                style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))" }}
              >
                Dashboard
              </Link>
            )}
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main
        className="flex-1 w-full"
        style={{ paddingTop: isLanding ? "0" : "80px" }}
      >
        <Outlet />
      </main>
    </div>
  );
}
