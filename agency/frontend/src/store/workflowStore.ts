import { create } from "zustand";
import type { Skill, Workflow, ExecutionMessage } from "../types";
import { api } from "../api/client";

interface WFState {
  skills: Skill[]; workflows: Workflow[]; currentWorkflow: Workflow | null;
  executionLog: ExecutionMessage[]; isExecuting: boolean; ws: WebSocket | null; loading: boolean; apiKey: string;
  loadSkills: () => Promise<void>; loadWorkflows: () => Promise<void>;
  createWorkflow: (name: string) => Promise<Workflow>; selectWorkflow: (id: string) => Promise<void>;
  saveWorkflow: () => Promise<void>; deleteWorkflow: (id: string) => Promise<void>;
  updateNodes: (nodes: Workflow["nodes"]) => void; updateEdges: (edges: Workflow["edges"]) => void;
  updateNodeConfig: (nodeId: string, config: Record<string, string>) => void;
  executeWorkflow: (id: string) => void; resetExecution: () => void; setApiKey: (key: string) => void;
}

export const useWorkflowStore = create<WFState>((set, get) => ({
  skills: [], workflows: [], currentWorkflow: null, executionLog: [], isExecuting: false,
  ws: null, loading: false, apiKey: typeof window !== "undefined" ? localStorage.getItem("agency_api_key") || "" : "",

  loadSkills: async () => { try { set({ skills: await api.getSkills() }); } catch {} },
  loadWorkflows: async () => { set({ loading: true }); try { set({ workflows: await api.listWorkflows(), loading: false }); } catch { set({ loading: false }); } },
  createWorkflow: async (name) => { const wf = await api.createWorkflow(name); set((s) => ({ workflows: [...s.workflows, wf], currentWorkflow: wf })); return wf; },
  selectWorkflow: async (id) => { try { set({ currentWorkflow: await api.getWorkflow(id), executionLog: [] }); } catch {} },
  saveWorkflow: async () => { const wf = get().currentWorkflow; if (!wf) return; try { set({ currentWorkflow: await api.saveWorkflow(wf.id, { nodes: wf.nodes, edges: wf.edges }) }); } catch {} },
  deleteWorkflow: async (id) => { try { await api.deleteWorkflow(id); set((s) => ({ workflows: s.workflows.filter((w) => w.id !== id), currentWorkflow: s.currentWorkflow?.id === id ? null : s.currentWorkflow })); } catch {} },
  updateNodes: (nodes) => { const wf = get().currentWorkflow; if (wf) set({ currentWorkflow: { ...wf, nodes } }); },
  updateEdges: (edges) => { const wf = get().currentWorkflow; if (wf) set({ currentWorkflow: { ...wf, edges } }); },
  updateNodeConfig: (nodeId, config) => { const wf = get().currentWorkflow; if (wf) set({ currentWorkflow: { ...wf, nodes: wf.nodes.map((n) => n.id === nodeId ? { ...n, config } : n) } }); },

  executeWorkflow: (id) => {
    get().ws?.close();
    const ws = api.executeWorkflow(id, get().apiKey || undefined);
    set({ isExecuting: true, executionLog: [], ws });
    ws.onmessage = (event) => {
      const msg: ExecutionMessage = JSON.parse(event.data);
      set((s) => ({ executionLog: [...s.executionLog, msg] }));
      if (msg.type === "node_status") { const wf = get().currentWorkflow; if (wf) set({ currentWorkflow: { ...wf, nodes: wf.nodes.map((n) => n.id === msg.nodeId ? { ...n, status: msg.status as any } : n) } }); }
      if (msg.type === "output") { const wf = get().currentWorkflow; if (wf) set({ currentWorkflow: { ...wf, nodes: wf.nodes.map((n) => n.id === msg.nodeId ? { ...n, output: msg.output, status: "completed" as const } : n) } }); }
      if (msg.type === "complete") set({ isExecuting: false });
    };
    ws.onerror = () => set({ isExecuting: false });
    ws.onclose = () => set({ isExecuting: false });
  },

  resetExecution: () => {
    get().ws?.close();
    const wf = get().currentWorkflow;
    set({ executionLog: [], isExecuting: false, ws: null });
    if (wf) set({ currentWorkflow: { ...wf, nodes: wf.nodes.map((n) => ({ ...n, status: "idle" as const, output: undefined })), status: "draft" } });
  },

  setApiKey: (key) => { set({ apiKey: key }); localStorage.setItem("agency_api_key", key); },
}));
