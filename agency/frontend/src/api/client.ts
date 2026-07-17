import type { Skill, Workflow } from "../types";

async function j<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${url}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export const api = {
  getSkills: () => j<Skill[]>("/skills"),
  listWorkflows: () => j<Workflow[]>("/workflows"),
  createWorkflow: (name: string) => j<Workflow>("/workflows", { method: "POST", body: JSON.stringify({ name }) }),
  getWorkflow: (id: string) => j<Workflow>(`/workflows/${id}`),
  saveWorkflow: (id: string, data: { nodes: Workflow["nodes"]; edges: Workflow["edges"] }) =>
    j<Workflow>(`/workflows/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteWorkflow: (id: string) => fetch(`/api/workflows/${id}`, { method: "DELETE" }),
  executeWorkflow: (id: string, apiKey?: string): WebSocket => {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const keyParam = apiKey ? `?key=${encodeURIComponent(apiKey)}` : "";
    return new WebSocket(`${proto}//${window.location.host}/api/workflows/${id}/execute${keyParam}`);
  },
};
