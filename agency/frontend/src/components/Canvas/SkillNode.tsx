import { memo } from "react";
import type { NodeProps } from "reactflow";
import { Handle, Position } from "reactflow";

const statusColors: Record<string, string> = {
  idle: "hsl(var(--muted))",
  running: "hsl(210 50% 65%)",
  completed: "#22c55e",
  failed: "#ef4444",
};

const categoryColors: Record<string, string> = {
  Strategy: "hsl(210 70% 60%)",
  Design: "hsl(270 60% 60%)",
  Development: "hsl(150 60% 50%)",
  Content: "hsl(40 80% 55%)",
  Quality: "hsl(190 60% 55%)",
  Infrastructure: "hsl(0 60% 55%)",
  Marketing: "hsl(320 60% 55%)",
  Security: "hsl(120 50% 50%)",
};

function SkillNodeComponent({ data }: NodeProps) {
  const statusColor = statusColors[data.status] || statusColors.idle;
  const catColor = categoryColors[data.category] || "hsl(var(--muted))";
  const isRunning = data.status === "running";

  return (
    <div
      className="relative px-4 py-3 rounded-xl min-w-[160px] transition-all duration-200"
      style={{
        background: "hsl(var(--surface))",
        border: `1px solid ${data.status === "completed" ? "rgba(34,197,94,0.3)" : data.status === "running" ? "rgba(137,170,204,0.3)" : "hsl(var(--stroke))"}`,
        boxShadow: isRunning ? "0 0 20px rgba(137,170,204,0.15)" : "0 2px 12px rgba(0,0,0,0.2)",
      }}
    >
      {/* Status dot + pulse */}
      <div className="absolute -top-1.5 -right-1.5">
        <div className="w-3 h-3 rounded-full border-2" style={{ borderColor: "hsl(var(--bg))", background: statusColor }} />
        {isRunning && (
          <div className="absolute inset-0 w-3 h-3 rounded-full animate-ping" style={{ background: statusColor, opacity: 0.3 }} />
        )}
      </div>

      {/* Category badge */}
      <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: catColor }}>
        {data.category || "General"}
      </div>

      {/* Label */}
      <div className="text-sm font-semibold" style={{ color: "hsl(var(--text))" }}>
        {data.label}
      </div>

      {/* Output type */}
      {data.outputType && (
        <div className="text-[10px] mt-1 font-mono" style={{ color: "hsl(var(--muted))" }}>
          {data.outputType}
        </div>
      )}

      {/* Handles */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: "hsl(var(--stroke))", width: 8, height: 8, border: "2px solid hsl(var(--bg))" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: "hsl(var(--accent))", width: 8, height: 8, border: "2px solid hsl(var(--bg))" }}
      />
    </div>
  );
}

export const SkillNode = memo(SkillNodeComponent);
