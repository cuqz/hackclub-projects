package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"hivemind/agents"
	"hivemind/db"

	"github.com/google/uuid"
)

type Handler struct {
	store        *db.Store
	orchestrator *agents.Orchestrator
	broker       *SSEBroker
}

func NewHandler(store *db.Store, orch *agents.Orchestrator, broker *SSEBroker) *Handler {
	return &Handler{
		store:        store,
		orchestrator: orch,
		broker:       broker,
	}
}

func (h *Handler) HandleSubmit(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "method not allowed", 405)
		return
	}

	var req SubmitRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", 400)
		return
	}

	if req.Title == "" || req.Description == "" {
		http.Error(w, "title and description required", 400)
		return
	}

	problemID := uuid.New().String()
	runID := uuid.New().String()

	problem := db.Problem{
		ID:          problemID,
		Title:       req.Title,
		Description: req.Description,
		Location:    req.Location,
		Category:    inferCategory(req.Title, req.Description),
		SubmittedBy: req.SubmittedBy,
		CreatedAt:   time.Now(),
		Status:      "processing",
	}

	if err := h.store.SaveProblem(&problem); err != nil {
		http.Error(w, fmt.Sprintf("save error: %v", err), 500)
		return
	}

	run := db.AgentRun{
		ID:        runID,
		ProblemID: problemID,
		Status:    "running",
		CreatedAt: time.Now(),
	}
	h.store.SaveAgentRun(&run)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"problem_id": problemID,
		"run_id":     runID,
		"status":     "processing",
	})

	go h.runPipeline(problemID, runID, req)
}

func (h *Handler) runPipeline(problemID, runID string, req SubmitRequest) {
	orchChan := h.orchestrator.Subscribe()
	done := make(chan bool)

	go func() {
		for msg := range orchChan {
			h.broker.Publish(SSEEvent{
				Type:    "agent_update",
				Payload: msg,
			})
		}
		done <- true
	}()

	results, err := h.orchestrator.RunPipeline(req.Title, req.Description, req.Location)
	if err != nil {
		h.broker.Publish(SSEEvent{Type: "error", Payload: err.Error()})
		return
	}

	<-done

	for _, result := range results {
		h.store.SaveAgentOutput(&db.AgentOutput{
			RunID:     runID,
			AgentName: result.Name,
			Content:   result.Output,
			Status:    result.Status,
		})
	}

	var solutionContent string
	for _, r := range results {
		if r.Name == "solution_architect" {
			solutionContent = r.Output
			break
		}
	}

	solutionID := uuid.New().String()
	solution := db.Solution{
		ID:          solutionID,
		ProblemID:   problemID,
		Summary:     solutionContent,
		Steps:       "[]",
		Resources:   "[]",
		ImpactScore: 8,
	}
	h.store.SaveSolution(&solution)

	h.broker.Publish(SSEEvent{
		Type:    "complete",
		Payload: fmt.Sprintf(`{"problem_id":"%s","solution_id":"%s"}`, problemID, solutionID),
	})
}

func (h *Handler) HandleProblems(w http.ResponseWriter, r *http.Request) {
	dbProblems, err := h.store.GetProblems()
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	problems := make([]Problem, len(dbProblems))
	for i, p := range dbProblems {
		problems[i] = Problem{
			ID:          p.ID,
			Title:       p.Title,
			Description: p.Description,
			Location:    p.Location,
			Category:    p.Category,
			SubmittedBy: p.SubmittedBy,
			CreatedAt:   p.CreatedAt,
			Status:      p.Status,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(problems)
}

func (h *Handler) HandleSolutions(w http.ResponseWriter, r *http.Request) {
	dbSolutions, err := h.store.GetSolutions()
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	solutions := make([]Solution, len(dbSolutions))
	for i, s := range dbSolutions {
		solutions[i] = Solution{
			ID:          s.ID,
			ProblemID:   s.ProblemID,
			Summary:     s.Summary,
			Steps:       s.Steps,
			Resources:   s.Resources,
			ImpactScore: s.ImpactScore,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(solutions)
}

func (h *Handler) HandleStats(w http.ResponseWriter, r *http.Request) {
	dbStats, err := h.store.GetStats()
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	stats := ImpactStats{
		TotalProblems:  dbStats.TotalProblems,
		TotalSolutions: dbStats.TotalSolutions,
		ByCategory:     dbStats.ByCategory,
		AvgImpactScore: dbStats.AvgImpactScore,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

func (h *Handler) HandleSSE(w http.ResponseWriter, r *http.Request) {
	h.broker.ServeHTTP(w, r)
}

func (h *Handler) HandleCORS(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	w.WriteHeader(200)
}

func inferCategory(title, desc string) string {
	t := strings.ToLower(title + " " + desc)
	switch {
	case strings.Contains(t, "school") || strings.Contains(t, "teacher") || strings.Contains(t, "learn") || strings.Contains(t, "student") || strings.Contains(t, "educat"):
		return "education"
	case strings.Contains(t, "health") || strings.Contains(t, "hospital") || strings.Contains(t, "doctor") || strings.Contains(t, "medical") || strings.Contains(t, "mental"):
		return "health"
	case strings.Contains(t, "trash") || strings.Contains(t, "recycl") || strings.Contains(t, "climate") || strings.Contains(t, "carbon") || strings.Contains(t, "pollution") || strings.Contains(t, "green"):
		return "environment"
	case strings.Contains(t, "crime") || strings.Contains(t, "police") || strings.Contains(t, "safety") || strings.Contains(t, "violence"):
		return "safety"
	case strings.Contains(t, "road") || strings.Contains(t, "bridge") || strings.Contains(t, "water") || strings.Contains(t, "electricity"):
		return "infrastructure"
	case strings.Contains(t, "food") || strings.Contains(t, "hunger") || strings.Contains(t, "meal"):
		return "food"
	case strings.Contains(t, "job") || strings.Contains(t, "employ") || strings.Contains(t, "money") || strings.Contains(t, "poverty"):
		return "economic"
	case strings.Contains(t, "tech") || strings.Contains(t, "internet") || strings.Contains(t, "software") || strings.Contains(t, "app") || strings.Contains(t, "digital"):
		return "technology"
	case strings.Contains(t, "neighbor") || strings.Contains(t, "volunteer") || strings.Contains(t, "community") || strings.Contains(t, "event"):
		return "community"
	case strings.Contains(t, "house") || strings.Contains(t, "shelter") || strings.Contains(t, "home") || strings.Contains(t, "rent") || strings.Contains(t, "homeless"):
		return "housing"
	}
	return "community"
}
