import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useWorkflowStore } from "../store/workflowStore";

const statusConfig: Record<string, { color: string; label: string }> = {
  completed: { color: "#22c55e", label: "Completed" },
  running: { color: "hsl(210 50% 65%)", label: "Running" },
  draft: { color: "hsl(var(--muted))", label: "Draft" },
  failed: { color: "#ef4444", label: "Failed" },
};

export function Dashboard() {
  const navigate = useNavigate();
  const workflows = useWorkflowStore((s) => s.workflows);
  const loadWorkflows = useWorkflowStore((s) => s.loadWorkflows);
  const createWorkflow = useWorkflowStore((s) => s.createWorkflow);
  const deleteWorkflow = useWorkflowStore((s) => s.deleteWorkflow);
  const [createOpen, setCreateOpen] = useState(false);
  const [name, setName] = useState("");

  useEffect(() => { loadWorkflows(); }, [loadWorkflows]);

  const handleCreate = async () => {
    if (!name.trim()) return;
    const wf = await createWorkflow(name.trim());
    setName("");
    setCreateOpen(false);
    if (wf?.id) navigate(`/workflow/${wf.id}`);
  };

  return (
    <div className="max-w-[900px] mx-auto px-6 md:px-10 py-12 md:py-20">
      {/* Header */}
      <div className="flex items-end justify-between mb-10">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
          <p className="mt-1.5 text-sm" style={{ color: "hsl(var(--text-secondary))" }}>
            {workflows.length} pipeline{workflows.length !== 1 && "s"}
          </p>
        </div>
        <button
          onClick={() => setCreateOpen(true)}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-white font-medium text-sm transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
          style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))" }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          New workflow
        </button>
      </div>

      {/* Create modal */}
      <AnimatePresence>
        {createOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center"
            style={{ background: "rgba(0,0,0,0.6)" }}
            onClick={() => setCreateOpen(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              className="w-full max-w-md mx-4 p-6 rounded-2xl"
              style={{ background: "hsl(var(--surface))", border: "1px solid hsl(var(--stroke))" }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-lg font-semibold">Create workflow</h2>
              <p className="text-sm mt-1" style={{ color: "hsl(var(--text-secondary))" }}>Give your pipeline a name to get started.</p>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                placeholder="My pipeline"
                className="w-full mt-4 px-4 py-3 rounded-xl text-sm outline-none transition-all duration-200"
                style={{ background: "hsl(var(--bg))", border: "1px solid hsl(var(--stroke))", color: "hsl(var(--text))" }}
                autoFocus
              />
              <div className="flex items-center justify-end gap-3 mt-4">
                <button
                  onClick={() => setCreateOpen(false)}
                  className="px-4 py-2 rounded-xl text-sm transition-all duration-200"
                  style={{ color: "hsl(var(--text-secondary))" }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreate}
                  disabled={!name.trim()}
                  className="px-5 py-2 rounded-xl text-white font-medium text-sm transition-all duration-200 disabled:opacity-40"
                  style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))" }}
                >
                  Create
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Workflow list */}
      {workflows.length === 0 ? (
        <div className="text-center py-24">
          <div className="text-5xl mb-4 opacity-30">⚡</div>
          <p className="text-lg font-medium">No workflows yet</p>
          <p className="text-sm mt-1" style={{ color: "hsl(var(--text-secondary))" }}>Create your first AI pipeline to get started.</p>
          <button
            onClick={() => setCreateOpen(true)}
            className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-white font-medium text-sm transition-all duration-200"
            style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))" }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            Create workflow
          </button>
        </div>
      ) : (
        <motion.div className="flex flex-col gap-3" initial="hidden" animate="show" variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}>
          {workflows.map((wf) => {
            const cfg = statusConfig[wf.status] || statusConfig.draft;
            return (
              <motion.div
                key={wf.id}
                variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
                className="group relative p-5 rounded-xl cursor-pointer transition-all duration-200 hover:translate-y-[-1px]"
                style={{ background: "hsl(var(--surface))", border: "1px solid hsl(var(--stroke))" }}
                onClick={() => navigate(`/workflow/${wf.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="min-w-0">
                    <h3 className="font-semibold text-sm truncate">{wf.name}</h3>
                    <div className="flex items-center gap-3 mt-1.5">
                      <span className="flex items-center gap-1.5 text-xs" style={{ color: cfg.color }}>
                        <span className="w-1.5 h-1.5 rounded-full" style={{ background: cfg.color }} />
                        {cfg.label}
                      </span>
                      <span className="text-xs" style={{ color: "hsl(var(--muted))" }}>
                        {wf.nodes?.length || 0} nodes
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => { e.stopPropagation(); navigate(`/workflow/${wf.id}`); }}
                      className="px-4 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 opacity-0 group-hover:opacity-100"
                      style={{ background: "hsl(var(--accent) / 0.1)", color: "hsl(var(--accent))" }}
                    >
                      Open
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteWorkflow(wf.id); }}
                      className="p-1.5 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100 hover:bg-red-500/10"
                      style={{ color: "hsl(var(--muted))" }}
                      title="Delete"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </div>
  );
}
