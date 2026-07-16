package db

import (
	"database/sql"
	"fmt"
	"time"

	_ "modernc.org/sqlite"
)

type Problem struct {
	ID          string
	Title       string
	Description string
	Location    string
	Category    string
	SubmittedBy string
	CreatedAt   time.Time
	Status      string
}

type AgentRun struct {
	ID        string
	ProblemID string
	Status    string
	CreatedAt time.Time
}

type AgentOutput struct {
	ID        int
	RunID     string
	AgentName string
	Content   string
	Status    string
}

type Solution struct {
	ID          string
	ProblemID   string
	Summary     string
	Steps       string
	Resources   string
	ImpactScore int
}

type ImpactStats struct {
	TotalProblems  int
	TotalSolutions int
	ByCategory     map[string]int
	AvgImpactScore float64
}

type Store struct {
	db *sql.DB
}

func New(path string) (*Store, error) {
	db, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, fmt.Errorf("open db: %w", err)
	}

	if _, err := db.Exec("PRAGMA journal_mode=WAL"); err != nil {
		return nil, fmt.Errorf("set wal: %w", err)
	}

	s := &Store{db: db}
	if err := s.migrate(); err != nil {
		return nil, fmt.Errorf("migrate: %w", err)
	}
	return s, nil
}

func (s *Store) migrate() error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS problems (
			id TEXT PRIMARY KEY,
			title TEXT NOT NULL,
			description TEXT NOT NULL,
			location TEXT DEFAULT '',
			category TEXT DEFAULT '',
			submitted_by TEXT DEFAULT '',
			created_at TEXT NOT NULL,
			status TEXT DEFAULT 'pending'
		)`,
		`CREATE TABLE IF NOT EXISTS agent_runs (
			id TEXT PRIMARY KEY,
			problem_id TEXT NOT NULL,
			status TEXT DEFAULT 'running',
			created_at TEXT NOT NULL,
			FOREIGN KEY (problem_id) REFERENCES problems(id)
		)`,
		`CREATE TABLE IF NOT EXISTS agent_outputs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			run_id TEXT NOT NULL,
			agent_name TEXT NOT NULL,
			content TEXT NOT NULL,
			status TEXT DEFAULT 'running',
			created_at TEXT NOT NULL,
			FOREIGN KEY (run_id) REFERENCES agent_runs(id)
		)`,
		`CREATE TABLE IF NOT EXISTS solutions (
			id TEXT PRIMARY KEY,
			problem_id TEXT NOT NULL,
			summary TEXT NOT NULL,
			steps TEXT DEFAULT '[]',
			resources TEXT DEFAULT '[]',
			impact_score INTEGER DEFAULT 0,
			created_at TEXT NOT NULL,
			FOREIGN KEY (problem_id) REFERENCES problems(id)
		)`,
	}

	for _, q := range queries {
		if _, err := s.db.Exec(q); err != nil {
			return fmt.Errorf("exec %q: %s", q[:40], err)
		}
	}
	return nil
}

func (s *Store) SaveProblem(p *Problem) error {
	_, err := s.db.Exec(
		`INSERT INTO problems (id, title, description, location, category, submitted_by, created_at, status)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
		p.ID, p.Title, p.Description, p.Location, p.Category, p.SubmittedBy, p.CreatedAt.Format(time.RFC3339), p.Status,
	)
	return err
}

func (s *Store) SaveAgentRun(r *AgentRun) error {
	_, err := s.db.Exec(
		`INSERT INTO agent_runs (id, problem_id, status, created_at) VALUES (?, ?, ?, ?)`,
		r.ID, r.ProblemID, r.Status, r.CreatedAt.Format(time.RFC3339),
	)
	return err
}

func (s *Store) SaveAgentOutput(o *AgentOutput) error {
	_, err := s.db.Exec(
		`INSERT INTO agent_outputs (run_id, agent_name, content, status, created_at) VALUES (?, ?, ?, ?, ?)`,
		o.RunID, o.AgentName, o.Content, o.Status, time.Now().Format(time.RFC3339),
	)
	return err
}

func (s *Store) SaveSolution(sol *Solution) error {
	_, err := s.db.Exec(
		`INSERT INTO solutions (id, problem_id, summary, steps, resources, impact_score, created_at)
		VALUES (?, ?, ?, ?, ?, ?, ?)`,
		sol.ID, sol.ProblemID, sol.Summary, sol.Steps, sol.Resources, sol.ImpactScore, time.Now().Format(time.RFC3339),
	)
	return err
}

func (s *Store) GetProblems() ([]Problem, error) {
	rows, err := s.db.Query(`SELECT id, title, description, location, category, submitted_by, created_at, status FROM problems ORDER BY created_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var problems []Problem
	for rows.Next() {
		var p Problem
		var createdAt string
		if err := rows.Scan(&p.ID, &p.Title, &p.Description, &p.Location, &p.Category, &p.SubmittedBy, &createdAt, &p.Status); err != nil {
			return nil, err
		}
		p.CreatedAt, _ = time.Parse(time.RFC3339, createdAt)
		problems = append(problems, p)
	}
	return problems, nil
}

func (s *Store) GetSolutions() ([]Solution, error) {
	rows, err := s.db.Query(`SELECT id, problem_id, summary, steps, resources, impact_score FROM solutions ORDER BY impact_score DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var solutions []Solution
	for rows.Next() {
		var sol Solution
		if err := rows.Scan(&sol.ID, &sol.ProblemID, &sol.Summary, &sol.Steps, &sol.Resources, &sol.ImpactScore); err != nil {
			return nil, err
		}
		solutions = append(solutions, sol)
	}
	return solutions, nil
}

func (s *Store) GetStats() (*ImpactStats, error) {
	stats := &ImpactStats{
		ByCategory: make(map[string]int),
	}

	row := s.db.QueryRow(`SELECT COUNT(*) FROM problems`)
	row.Scan(&stats.TotalProblems)

	row = s.db.QueryRow(`SELECT COUNT(*) FROM solutions`)
	row.Scan(&stats.TotalSolutions)

	row = s.db.QueryRow(`SELECT COALESCE(AVG(impact_score), 0) FROM solutions`)
	row.Scan(&stats.AvgImpactScore)

	rows, err := s.db.Query(`SELECT category, COUNT(*) as cnt FROM problems GROUP BY category`)
	if err != nil {
		return stats, nil
	}
	defer rows.Close()

	for rows.Next() {
		var cat string
		var cnt int
		rows.Scan(&cat, &cnt)
		stats.ByCategory[cat] = cnt
	}

	return stats, nil
}
