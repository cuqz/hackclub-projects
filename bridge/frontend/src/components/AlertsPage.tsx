import { useState, useEffect } from "react";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/alerts/active")
      .then(r => r.json()).then(d => { setAlerts(d); setLoading(false); })
      .catch(() => { setAlerts([]); setLoading(false); });
  }, []);

  const severityConfig: Record<string, { color: string; bg: string; label: string }> = {
    high: { color: "#ef4444", bg: "rgba(239,68,68,0.1)", label: "High" },
    warning: { color: "#d4a056", bg: "rgba(212,160,86,0.1)", label: "Warning" },
    info: { color: "var(--color-accent)", bg: "rgba(108,140,191,0.1)", label: "Info" },
  };

  return (
    <div>
      <div className="py-6">
        <h2 className="text-xl font-bold" style={{ color: "var(--color-text-primary)" }}>Emergency Alerts</h2>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>Active alerts and warnings for your area</p>
      </div>

      {loading ? (
        <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
          <div className="w-5 h-5 rounded-full border-2 animate-spin mx-auto" style={{ borderColor: "var(--color-border)", borderTopColor: "var(--color-accent)" }} />
        </div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
          <div className="text-3xl mb-3 opacity-50">✅</div>
          <p className="text-sm">No active alerts in your area.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {alerts.map((alert: any) => {
            const cfg = severityConfig[alert.severity] || severityConfig.info;
            return (
              <div key={alert.id} className="p-4 rounded-xl" style={{ background: "var(--color-bg-card)", border: `1px solid ${cfg.color}33` }}>
                <div className="flex items-center gap-2.5 mb-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold" style={{ background: cfg.bg, color: cfg.color }}>{cfg.label}</span>
                  {alert.region && <span className="text-[10px]" style={{ color: "var(--color-text-muted)" }}>{alert.region}</span>}
                </div>
                <div className="font-semibold text-sm" style={{ color: "var(--color-text-primary)" }}>{alert.title}</div>
                <div className="text-sm mt-1 leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>{alert.body}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
