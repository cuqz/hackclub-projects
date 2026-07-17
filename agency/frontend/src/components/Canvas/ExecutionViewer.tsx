import { useRef, useEffect, memo, useMemo } from "react";
import { useWorkflowStore } from "../../store/workflowStore";

function ExecutionViewerComponent() {
  const executionLog = useWorkflowStore((s) => s.executionLog);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [executionLog]);

  const timeStr = () => {
    const n = new Date();
    return n.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
  };

  return (
    <div className="h-full flex flex-col" style={{ background: "hsl(var(--surface))" }}>
      {/* Header */}
      <div className="px-5 py-4 border-b" style={{ borderColor: "hsl(var(--stroke))" }}>
        <h3 className="text-sm font-semibold" style={{ color: "hsl(var(--text))" }}>Execution Log</h3>
        <p className="text-xs mt-0.5" style={{ color: "hsl(var(--muted))" }}>
          {executionLog.length} event{executionLog.length !== 1 && "s"}
        </p>
      </div>

      {/* Log entries */}
      <div className="flex-1 overflow-y-auto p-4 space-y-1.5">
        {executionLog.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-xs" style={{ color: "hsl(var(--muted))" }}>No execution events yet. Run the workflow to see logs.</p>
          </div>
        ) : (
          executionLog.map((entry: any, i: number) => {
            const isRunning = entry.type === "node_status" && entry.status === "running";
            const isDone = entry.type === "node_status" && entry.status === "completed";
            const isFailed = entry.type === "node_status" && entry.status === "failed";
            const isOutput = entry.type === "output";

            return (
              <div
                key={i}
                className="group px-3 py-2 rounded-lg text-[11px] font-mono leading-relaxed transition-colors duration-150"
                style={{
                  background: isRunning ? "rgba(137,170,204,0.06)" : isFailed ? "rgba(239,68,68,0.06)" : "transparent",
                  color: isRunning ? "hsl(210 50% 70%)" : isFailed ? "#ef4444" : isDone ? "#22c55e" : isOutput ? "hsl(var(--text-secondary))" : "hsl(var(--muted))",
                }}
              >
                <div className="flex items-center gap-2">
                  {isRunning && <span className="w-1.5 h-1.5 rounded-full animate-pulse shrink-0" style={{ background: "hsl(210 50% 65%)" }} />}
                  {isDone && <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: "#22c55e" }} />}
                  {isFailed && <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: "#ef4444" }} />}
                  {isOutput && <span className="text-[10px] shrink-0 opacity-50">→</span>}
                  {!isRunning && !isDone && !isFailed && !isOutput && <span className="w-1.5 shrink-0" />}
                  
                  <span className="opacity-50 shrink-0">{timeStr()}</span>
                  <span className="truncate">{entry.message || entry.output || `${entry.status || entry.type}`}</span>
                </div>
                {entry.nodeId && (
                  <div className="mt-0.5 text-[10px] opacity-40 pl-3">node: {entry.nodeId}</div>
                )}
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

export const ExecutionViewer = memo(ExecutionViewerComponent);
