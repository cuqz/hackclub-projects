export interface Skill {
  id: string; name: string; description: string; icon: string; color: string;
  category: string; outputType: string; config: SkillConfig[];
}
export interface SkillConfig { key: string; label: string; type: string; default: string; }
export interface WorkflowNode {
  id: string; skillId: string; label: string; position: { x: number; y: number };
  config: Record<string, string>; status: "idle" | "running" | "completed" | "failed"; output?: string;
}
export interface WorkflowEdge { id: string; source: string; target: string; }
export interface Workflow {
  id: string; name: string; nodes: WorkflowNode[]; edges: WorkflowEdge[];
  status: "draft" | "running" | "completed" | "failed"; createdAt: string;
}
export interface ExecutionMessage {
  type: string; nodeId?: string; status?: string; message?: string; output?: string; percent?: number;
}
