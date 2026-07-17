package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{CheckOrigin: func(r *http.Request) bool { return true }}

type Skill struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Icon        string   `json:"icon"`
	Color       string   `json:"color"`
	Category    string   `json:"category"`
	OutputType  string   `json:"outputType"`
	Config      []Config `json:"config"`
}

type Config struct {
	Key     string `json:"key"`
	Label   string `json:"label"`
	Type    string `json:"type"`
	Default string `json:"default"`
}

type Workflow struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Nodes     []Node `json:"nodes"`
	Edges     []Edge `json:"edges"`
	Status    string `json:"status"`
	CreatedAt string `json:"createdAt"`
}

type Node struct {
	ID       string            `json:"id"`
	SkillID  string            `json:"skillId"`
	Label    string            `json:"label"`
	Position Position          `json:"position"`
	Config   map[string]string `json:"config"`
	Status   string            `json:"status"`
	Output   string            `json:"output,omitempty"`
}

type Position struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
}

type Edge struct {
	ID     string `json:"id"`
	Source string `json:"source"`
	Target string `json:"target"`
}

type ExecutionMessage struct {
	Type    string `json:"type"`
	NodeID  string `json:"nodeId,omitempty"`
	Status  string `json:"status,omitempty"`
	Message string `json:"message,omitempty"`
	Output  string `json:"output,omitempty"`
	Percent int    `json:"percent,omitempty"`
}

type OpenRouterRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Stream   bool      `json:"stream"`
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type OpenRouterResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error"`
}

var (
	skills    []Skill
	workflows = make(map[string]*Workflow)
	mu        sync.RWMutex
)

func initSkills() {
	skills = []Skill{
		{ID: "brand-architect", Name: "Brand Architect", Description: "Generates brand identity systems — logos, color palettes, typography, and voice guidelines.", Icon: "sparkles", Color: "#4a9eff", Category: "Design", OutputType: "Brand Kit", Config: []Config{{Key: "industry", Label: "Industry", Type: "text", Default: "tech"}, {Key: "vibe", Label: "Vibe", Type: "text", Default: "minimal"}}},
		{ID: "ui-artisan", Name: "UI Artisan", Description: "Polishes interfaces with premium design principles — spacing, typography, color systems.", Icon: "eye", Color: "#22c55e", Category: "Design", OutputType: "Design Tokens", Config: []Config{{Key: "style", Label: "Style direction", Type: "text", Default: "dark"}, {Key: "accent", Label: "Accent color", Type: "text", Default: "#4a9eff"}}},
		{ID: "content-weaver", Name: "Content Weaver", Description: "Writes compelling copy — landing pages, taglines, product descriptions.", Icon: "document-text", Color: "#a855f7", Category: "Content", OutputType: "Copy", Config: []Config{{Key: "tone", Label: "Tone of voice", Type: "text", Default: "professional"}, {Key: "length", Label: "Output length", Type: "text", Default: "medium"}}},
		{ID: "security-guardian", Name: "Security Guardian", Description: "Hardens project configurations — CSP headers, firewall rules, auth.", Icon: "shield-check", Color: "#ef4444", Category: "Infrastructure", OutputType: "Security Config", Config: []Config{{Key: "framework", Label: "Framework", Type: "text", Default: "react"}, {Key: "level", Label: "Hardening level", Type: "text", Default: "standard"}}},
		{ID: "code-forger", Name: "Code Forger", Description: "Generates production-ready code — components, APIs, schemas.", Icon: "code-bracket", Color: "#f59e0b", Category: "Development", OutputType: "Source Code", Config: []Config{{Key: "language", Label: "Language", Type: "text", Default: "typescript"}, {Key: "framework", Label: "Framework", Type: "text", Default: "react"}}},
		{ID: "doc-sage", Name: "Documentation Sage", Description: "Creates comprehensive docs — API references, README files.", Icon: "book-open", Color: "#06b6d4", Category: "Content", OutputType: "Documentation", Config: []Config{{Key: "type", Label: "Doc type", Type: "text", Default: "readme"}, {Key: "audience", Label: "Audience", Type: "text", Default: "developers"}}},
		{ID: "seo-oracle", Name: "SEO Oracle", Description: "Optimizes content for search — keywords, meta tags, structured data.", Icon: "chart-bar", Color: "#ec4899", Category: "Marketing", OutputType: "SEO Report", Config: []Config{{Key: "target", Label: "Target keyword", Type: "text", Default: ""}, {Key: "platform", Label: "Platform", Type: "text", Default: "web"}}},
		{ID: "image-alchemist", Name: "Image Alchemist", Description: "Generates visual assets — hero images, icons, illustrations, mockups.", Icon: "photo", Color: "#14b8a6", Category: "Design", OutputType: "Visual Assets", Config: []Config{{Key: "style", Label: "Art style", Type: "text", Default: "minimal"}, {Key: "format", Label: "Format", Type: "text", Default: "svg"}}},
		{ID: "reviewer", Name: "Code Reviewer", Description: "Analyzes code for bugs, security issues, performance problems.", Icon: "magnifying-glass", Color: "#f97316", Category: "Development", OutputType: "Review Report", Config: []Config{{Key: "severity", Label: "Severity filter", Type: "text", Default: "all"}}},
	}
}

func enableCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if r.Method == "OPTIONS" { w.WriteHeader(http.StatusOK); return }
		next.ServeHTTP(w, r)
	})
}

func sendJSON(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func handleSkills(w http.ResponseWriter, r *http.Request) { sendJSON(w, skills) }

func handleWorkflows(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case "GET":
		mu.RLock()
		list := make([]*Workflow, 0, len(workflows))
		for _, wf := range workflows { list = append(list, wf) }
		mu.RUnlock()
		sendJSON(w, list)
	case "POST":
		var req struct{ Name string `json:"name"` }
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "bad request", http.StatusBadRequest); return
		}
		wf := &Workflow{ID: uuid.New().String(), Name: req.Name, Nodes: []Node{}, Edges: []Edge{}, Status: "draft", CreatedAt: "Just now"}
		mu.Lock(); workflows[wf.ID] = wf; mu.Unlock()
		sendJSON(w, wf)
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}

func handleWorkflowByID(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	mu.RLock(); wf, ok := workflows[id]; mu.RUnlock()
	if !ok { http.Error(w, "not found", http.StatusNotFound); return }
	switch r.Method {
	case "GET": sendJSON(w, wf)
	case "PUT":
		var updated Workflow
		if err := json.NewDecoder(r.Body).Decode(&updated); err != nil {
			http.Error(w, "bad request", http.StatusBadRequest); return
		}
		mu.Lock(); wf.Nodes = updated.Nodes; wf.Edges = updated.Edges; mu.Unlock()
		sendJSON(w, wf)
	case "DELETE":
		mu.Lock(); delete(workflows, id); mu.Unlock()
		w.WriteHeader(http.StatusNoContent)
	}
}

func buildPrompt(skill *Skill, node *Node, context []string) string {
	prompts := map[string]string{
		"brand-architect":  fmt.Sprintf("Generate a brand identity kit for a %s company with a %s vibe. Include: color palette, typography recommendations, brand voice guidelines, and a brand positioning statement. Be specific and actionable.", node.Config["industry"], node.Config["vibe"]),
		"ui-artisan":       fmt.Sprintf("Generate a design token system for a %s-themed UI with accent color %s. Include: CSS custom properties for colors, spacing scale, typography scale, border radii, and shadows. Follow dark theme best practices.", node.Config["style"], node.Config["accent"]),
		"content-weaver":   fmt.Sprintf("Write marketing copy for AGENCY (an AI agent orchestration platform) with a %s tone. Include: a hero headline, subheadline, 4 key selling points, and a CTA. Keep total under 200 words.", node.Config["tone"]),
		"security-guardian": fmt.Sprintf("Generate a security hardening checklist for a %s application at %s level. Include: CSP headers, CSRF protection, rate limiting, auth best practices, dependency scanning, and HTTPS configuration.", node.Config["framework"], node.Config["level"]),
		"code-forger":      fmt.Sprintf("Generate a production-ready %s utility function in %s. The function should handle errors gracefully, include TypeScript types if applicable, and follow best practices. Include a brief usage example.", node.Config["language"], node.Config["framework"]),
		"doc-sage":         fmt.Sprintf("Write a %s document for a project called AGENCY — a visual AI agent orchestration platform. Target audience: %s. Cover: what it is, quick start, architecture overview, and API endpoints.", node.Config["type"], node.Config["audience"]),
		"seo-oracle":       fmt.Sprintf("Generate an SEO optimization report for a %s platform targeting '%s'. Include: meta title/description recommendations, keyword suggestions, structured data markup, and Core Web Vitals tips.", node.Config["target"], node.Config["platform"]),
		"image-alchemist":  fmt.Sprintf("Describe in detail a %s-style visual asset in %s format for AGENCY's hero section. Include: composition, color palette, lighting, mood, and layout. This is a design description, not code.", node.Config["style"], node.Config["format"]),
		"reviewer":         fmt.Sprintf("Review this code for %s-severity issues:\n\n```typescript\nfunction processData(input: any) {\n  const result = [];\n  for (let i = 0; i < input.length; i++) {\n    result.push(input[i].value * 2);\n  }\n  return result;\n}\n```\n\nCheck for: type safety, null safety, performance, security, and style. Be concise.", node.Config["severity"]),
	}
	if p, ok := prompts[skill.ID]; ok {
		if len(context) > 0 {
			prefix := "Previous steps generated:\n"
			for _, c := range context { prefix += "- " + c + "\n" }
			return prefix + "\n" + p
		}
		return p
	}
	return fmt.Sprintf("Explain what a %s agent does and provide a sample output.", skill.Name)
}

func callOpenRouter(apiKey, prompt string) (string, error) {
	body := OpenRouterRequest{
		Model: "google/gemini-2.0-flash-001",
		Messages: []Message{
			{Role: "system", Content: "You are an expert AI agent. Generate concise, production-quality output. Use markdown formatting. Keep responses under 500 words."},
			{Role: "user", Content: prompt},
		},
		Stream: false,
	}
	b, _ := json.Marshal(body)
	req, _ := http.NewRequest("POST", "https://openrouter.ai/api/v1/chat/completions", bytes.NewReader(b))
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("HTTP-Referer", "https://agency.local")
	req.Header.Set("X-Title", "AGENCY")

	client := &http.Client{Timeout: 60 * time.Second}
	resp, err := client.Do(req)
	if err != nil { return "", fmt.Errorf("request failed: %w", err) }
	defer resp.Body.Close()

	raw, _ := io.ReadAll(resp.Body)
	var orResp OpenRouterResponse
	if err := json.Unmarshal(raw, &orResp); err != nil {
		return "", fmt.Errorf("parse failed: %w", err)
	}
	if orResp.Error != nil {
		return "", fmt.Errorf("API error: %s", orResp.Error.Message)
	}
	if len(orResp.Choices) == 0 {
		return "", fmt.Errorf("no response from API")
	}
	return orResp.Choices[0].Message.Content, nil
}

func handleExecute(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	apiKey := r.URL.Query().Get("key")

	mu.RLock(); wf, ok := workflows[id]; mu.RUnlock()
	if !ok { http.Error(w, "not found", http.StatusNotFound); return }

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil { log.Printf("ws upgrade: %v", err); return }
	defer conn.Close()

	mu.Lock()
	wf.Status = "running"
	for i := range wf.Nodes { wf.Nodes[i].Status = "idle"; wf.Nodes[i].Output = "" }
	mu.Unlock()

	send := func(msg ExecutionMessage) { conn.WriteJSON(msg) }

	adj := map[string][]string{}
	inDeg := map[string]int{}
	nodeMap := map[string]*Node{}
	for i := range wf.Nodes { nodeMap[wf.Nodes[i].ID] = &wf.Nodes[i]; inDeg[wf.Nodes[i].ID] = 0 }
	for _, e := range wf.Edges { adj[e.Source] = append(adj[e.Source], e.Target); inDeg[e.Target]++ }

	queue := []string{}
	for id, d := range inDeg { if d == 0 { queue = append(queue, id) } }

	completed := 0
	total := len(wf.Nodes)
	stepPct := 100 / max(total, 1)
	contextLog := []string{}

	for len(queue) > 0 {
		current := queue[0]; queue = queue[1:]
		node, ok := nodeMap[current]
		if !ok { continue }

		var skill *Skill
		for i := range skills { if skills[i].ID == node.SkillID { skill = &skills[i]; break } }

		node.Status = "running"
		send(ExecutionMessage{Type: "node_status", NodeID: node.ID, Status: "running", Message: fmt.Sprintf("%s is working...", node.Label)})

		if apiKey != "" && skill != nil {
			prompt := buildPrompt(skill, node, contextLog)
			send(ExecutionMessage{Type: "progress", NodeID: node.ID, Status: "running", Message: "Calling AI agent...", Percent: 30})

			output, err := callOpenRouter(apiKey, prompt)
			if err != nil {
				send(ExecutionMessage{Type: "progress", NodeID: node.ID, Status: "running", Message: fmt.Sprintf("API error: %v, using fallback", err), Percent: 60})
				output = generateFallbackOutput(skill, node)
			} else {
				send(ExecutionMessage{Type: "progress", NodeID: node.ID, Status: "running", Message: "Response received, processing...", Percent: 80})
			}
			node.Output = output
			contextLog = append(contextLog, node.Label+": generated")
		} else {
			for _, m := range []string{"Analyzing inputs...", "Applying skill logic...", "Generating output...", "Finalizing..."} {
				send(ExecutionMessage{Type: "progress", NodeID: node.ID, Status: "running", Message: m, Percent: 25})
			}
			node.Output = generateFallbackOutput(skill, node)
		}

		node.Status = "completed"
		completed++
		send(ExecutionMessage{Type: "output", NodeID: node.ID, Status: "completed", Output: node.Output, Percent: completed * stepPct})

		for _, next := range adj[current] {
			inDeg[next]--
			if inDeg[next] == 0 { queue = append(queue, next) }
		}
	}

	mu.Lock(); wf.Status = "completed"; mu.Unlock()
	send(ExecutionMessage{Type: "complete", Status: "completed", Message: "All agents finished. Your workflow is ready.", Percent: 100})
}

func generateFallbackOutput(skill *Skill, node *Node) string {
	if skill == nil { return fmt.Sprintf("[%s] completed.", node.Label) }
	templates := map[string]string{
		"brand-architect": fmt.Sprintf("# Brand Kit\n\n**Industry:** %s\n**Vibe:** %s\n\n## Color Palette\n- Primary: #4a9eff\n- Background: #0a0a0a\n- Surface: #141414\n- Text: #e8e8e8\n\n## Typography\n- Headings: Inter, sans-serif\n- Body: system-ui\n\n## Voice\nProfessional, direct, premium. Short sentences. No jargon.", capitalize(node.Config["industry"])),
		"ui-artisan": fmt.Sprintf("## Design Tokens\n\n**Theme:** %s\n**Accent:** %s\n\n```css\n:root {\n  --bg: #0a0a0a;\n  --bg-elevated: #111111;\n  --bg-card: #141414;\n  --text-primary: #e8e8e8;\n  --text-secondary: #a0a0a0;\n  --accent: %s;\n  --radius: 12px;\n}\n```", capitalize(node.Config["style"]), node.Config["accent"], node.Config["accent"]),
		"content-weaver": fmt.Sprintf("## Copy\n\n**Tone:** %s\n\n---\n\n# Headline\nBuild Smarter. Ship Faster.\n\n## Subheadline\nAgency orchestrates AI agents into automated workflows.\n\n## Key Messages\n- Drag-and-drop agent composition\n- 10+ specialized AI skills\n- Real-time execution streaming\n- Production-ready output\n\n## CTA\nStart building free", capitalize(node.Config["tone"])),
		"security-guardian": fmt.Sprintf("## Security Report\n\n**Framework:** %s\n**Level:** %s\n\n### Headers\n```\nContent-Security-Policy: default-src 'self';\nX-Frame-Options: DENY\n```\n\n### Recommendations\n- Enable CSP\n- Rate limiting: 100 req/min\n- CSRF protection\n- Environment secrets\n- 2FA for admin", capitalize(node.Config["framework"]), capitalize(node.Config["level"])),
	}
	if t, ok := templates[skill.ID]; ok { return t }
	return fmt.Sprintf("[%s] Execution complete. Artifacts generated.", skill.Name)
}

func max(a, b int) int { if a > b { return a }; return b }
func capitalize(s string) string {
	if s == "" { return "" }
	r := []rune(s)
	if r[0] >= 'a' && r[0] <= 'z' { r[0] -= 32 }
	return string(r)
}

func main() {
	initSkills()
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/skills", handleSkills)
	mux.HandleFunc("GET /api/workflows", handleWorkflows)
	mux.HandleFunc("POST /api/workflows", handleWorkflows)
	mux.HandleFunc("GET /api/workflows/{id}", handleWorkflowByID)
	mux.HandleFunc("PUT /api/workflows/{id}", handleWorkflowByID)
	mux.HandleFunc("DELETE /api/workflows/{id}", handleWorkflowByID)
	mux.HandleFunc("GET /api/workflows/{id}/execute", handleExecute)
	mux.HandleFunc("GET /api/health", func(w http.ResponseWriter, r *http.Request) { sendJSON(w, map[string]string{"status": "ok"}) })
	fmt.Println("AGENCY backend on :8080")
	log.Fatal(http.ListenAndServe(":8080", enableCORS(mux)))
}
