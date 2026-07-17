export interface Problem {
  id: string
  title: string
  description: string
  location: string
  category: string
  submitted_by: string
  created_at: string
  status: string
}

export interface Solution {
  id: string
  problem_id: string
  summary: string
  steps: string
  resources: string
  impact_score: number
}

export interface ImpactStats {
  total_problems: number
  total_solutions: number
  by_category: Record<string, number>
  avg_impact_score: number
}

export interface AgentResult {
  name: string
  output: string
  status: string
  elapsed_ms: number
}

export interface SubmitResponse {
  problem_id: string
  run_id: string
  status: string
}

export interface AgentUpdate {
  agent: string
  content: string
}

export interface SSEEvent {
  type: 'agent_update' | 'complete' | 'error' | 'connected'
  payload: string
}
