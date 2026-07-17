import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { Node } from "reactflow";
import { AnimatePresence, motion } from "framer-motion";
import { useWorkflowStore } from "../store/workflowStore";
import { WorkflowCanvas } from "../components/Canvas/WorkflowCanvas";
import { SkillPalette } from "../components/Canvas/SkillPalette";
import { ExecutionViewer } from "../components/Canvas/ExecutionViewer";
import { NodeConfig } from "../components/Canvas/NodeConfig";

export function WorkflowEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const wf = useWorkflowStore((s) => s.currentWorkflow);
  const selectWorkflow = useWorkflowStore((s) => s.selectWorkflow);
  const saveWorkflow = useWorkflowStore((s) => s.saveWorkflow);
  const executeWorkflow = useWorkflowStore((s) => s.executeWorkflow);
  const resetExecution = useWorkflowStore((s) => s.resetExecution);
  const isExecuting = useWorkflowStore((s) => s.isExecuting);
  const apiKey = useWorkflowStore((s) => s.apiKey);
  const setApiKey = useWorkflowStore((s) => s.setApiKey);
  const [panel, setPanel] = useState<"skills" | "config" | "logs">("skills");
  const [selNode, setSelNode] = useState<Node | null>(null);
  const [saved, setSaved] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [localKey, setLocalKey] = useState(apiKey);
  const st = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => { if (id) selectWorkflow(id); }, [id, selectWorkflow]);

  const handleSave = async () => { await saveWorkflow(); setSaved(true); clearTimeout(st.current!); st.current = setTimeout(() => setSaved(false), 2000); };

  const handleExec = () => { if (!id) return; resetExecution(); setPanel("logs"); setSelNode(null); executeWorkflow(id); };

  const handleNodeClick = useCallback((_: any, n: Node) => { setSelNode(n); setPanel("config"); }, []);
  const handleCanvasClick = useCallback(() => setSelNode(null), []);

  if (!wf) return <div className="flex items-center justify-center min-h-[60vh]" style={{ color: "hsl(var(--muted))" }}><div className="w-5 h-5 rounded-full border-2 animate-spin" style={{ borderColor: "hsl(var(--stroke))", borderTopColor: "#89aacc" }} /></div>;

  const allDone = wf.nodes.length > 0 && wf.nodes.every((n) => n.status === "completed");

  return (
    <div className="flex h-screen max-w-none" style={{ paddingTop: "0px", background: "hsl(var(--bg))" }}>
      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between px-4 py-2" style={{ background: "hsl(var(--surface))", borderBottom: "1px solid hsl(var(--stroke))" }}>
          <div className="flex items-center gap-3">
            <button onClick={() => navigate("/dashboard")} className="text-sm px-3 py-1.5 rounded-lg" style={{ color: "hsl(var(--muted))" }}>&larr; Back</button>
            <span className="text-sm font-semibold" style={{ color: "hsl(var(--text))" }}>{wf.name}</span>
            <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: wf.status === "completed" ? "rgba(34,197,94,0.1)" : wf.status === "running" ? "rgba(137,170,204,0.1)" : "hsl(var(--stroke))", color: wf.status === "completed" ? "#22c55e" : wf.status === "running" ? "#89aacc" : "hsl(var(--muted))" }}>{wf.status}</span>
          </div>
          <div className="flex items-center gap-1.5">
            {(["skills", "config", "logs"] as const).map((t) => (
              <button key={t} onClick={() => { setPanel(t); if (t !== "config") setSelNode(null); }} className="text-sm px-3 py-1.5 rounded-lg transition-all" style={{ background: panel === t ? "hsl(var(--stroke))" : "transparent", color: panel === t ? "hsl(var(--text))" : "hsl(var(--muted))" }}>{t.charAt(0).toUpperCase() + t.slice(1)}</button>
            ))}
            <div className="w-px h-5 mx-1" style={{ background: "hsl(var(--stroke))" }} />
            <div className="relative">
              <button onClick={() => setShowKey(!showKey)} className="text-sm px-2 py-1 rounded-lg" style={{ color: apiKey ? "#22c55e" : "hsl(var(--muted))" }} title="API Key">&#9881;</button>
              {showKey && (
                <div className="absolute top-full right-0 mt-2 w-64 p-4 rounded-2xl z-50" style={{ background: "hsl(var(--surface))", border: "1px solid hsl(var(--stroke))", boxShadow: "0 8px 32px rgba(0,0,0,0.5)" }}>
                  <label className="block text-xs font-medium mb-1.5" style={{ color: "hsl(var(--muted))" }}>OpenRouter API Key</label>
                  <div className="flex gap-2">
                    <input type="password" value={localKey} onChange={(e) => setLocalKey(e.target.value)} placeholder="sk-or-..." className="flex-1 px-3 py-1.5 rounded-xl text-sm outline-none" style={{ background: "hsl(var(--bg))", border: "1px solid hsl(var(--stroke))", color: "hsl(var(--text))" }} />
                    <button onClick={() => { setApiKey(localKey); setShowKey(false); }} className="text-sm px-3 py-1.5 rounded-xl text-white" style={{ background: "linear-gradient(135deg, #89aacc, #4e85bf)" }}>Save</button>
                  </div>
                  <p className="text-xs mt-2" style={{ color: "hsl(var(--muted))" }}>Without a key, agents use demo mode with pre-generated outputs.</p>
                </div>
              )}
            </div>
            <button onClick={handleSave} className="text-sm px-3 py-1.5 rounded-lg" style={{ color: "hsl(var(--muted))" }}>{saved ? "Saved" : "Save"}</button>
            <button onClick={handleExec} disabled={isExecuting || wf.nodes.length === 0} className="text-sm font-medium px-4 py-1.5 rounded-lg text-white disabled:opacity-30" style={{ background: "linear-gradient(135deg, #89aacc, #4e85bf)" }}>{isExecuting ? "Running..." : "Execute"}</button>
          </div>
        </div>
        <div className="flex-1"><WorkflowCanvas onNodeClick={handleNodeClick} onCanvasClick={handleCanvasClick} /></div>
      </div>

      <AnimatePresence>
        {panel && (
          <motion.div initial={{ width: 0, opacity: 0 }} animate={{ width: 300, opacity: 1 }} exit={{ width: 0, opacity: 0 }} transition={{ duration: 0.15 }} className="overflow-hidden flex-shrink-0" style={{ background: "hsl(var(--surface))", borderLeft: "1px solid hsl(var(--stroke))" }}>
            <div className="w-[300px] h-full overflow-y-auto">
              {panel === "logs" && <ExecutionViewer />}
              {panel === "config" && <NodeConfig selectedNode={selNode} />}
              {panel === "skills" && <SkillPalette />}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {allDone && !isExecuting && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 16 }} className="absolute bottom-6 left-1/2 -translate-x-1/2 z-50 px-5 py-3 rounded-full text-sm" style={{ background: "hsl(var(--surface))", border: "1px solid rgba(34,197,94,0.3)", color: "#22c55e", boxShadow: "0 4px 24px rgba(0,0,0,0.3)" }}>
            &#10003; All agents completed
            <button onClick={() => setPanel("logs")} className="ml-3 underline text-sm" style={{ color: "#89aacc" }}>View outputs</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
