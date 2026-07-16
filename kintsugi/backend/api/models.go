package api

import "time"

type Problem struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Description string    `json:"description"`
	Location    string    `json:"location"`
	Category    string    `json:"category"`
	SubmittedBy string    `json:"submitted_by"`
	CreatedAt   time.Time `json:"created_at"`
	Status      string    `json:"status"`
}

type AgentRun struct {
	ID        string    `json:"id"`
	ProblemID string    `json:"problem_id"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
}

type AgentOutput struct {
	ID        int    `json:"id"`
	RunID     string `json:"run_id"`
	AgentName string `json:"agent_name"`
	Content   string `json:"content"`
	Status    string `json:"status"`
}

type Solution struct {
	ID          string `json:"id"`
	ProblemID   string `json:"problem_id"`
	Summary     string `json:"summary"`
	Steps       string `json:"steps"`
	Resources   string `json:"resources"`
	ImpactScore int    `json:"impact_score"`
}

type ImpactStats struct {
	TotalProblems  int            `json:"total_problems"`
	TotalSolutions int            `json:"total_solutions"`
	ByCategory     map[string]int `json:"by_category"`
	AvgImpactScore float64        `json:"avg_impact_score"`
}

type SSEEvent struct {
	Type    string `json:"type"`
	Payload string `json:"payload"`
}

type SubmitRequest struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	Location    string `json:"location"`
	SubmittedBy string `json:"submitted_by"`
}
