package agents

import (
	"encoding/json"
	"fmt"
	"time"

	"hivemind/featherless"
)

type AgentResult struct {
	Name    string `json:"name"`
	Output  string `json:"output"`
	Status  string `json:"status"`
	Elapsed int    `json:"elapsed_ms"`
}

type Orchestrator struct {
	client     *featherless.Client
	subscriber chan string
}

func NewOrchestrator(client *featherless.Client) *Orchestrator {
	return &Orchestrator{
		client:     client,
		subscriber: make(chan string, 100),
	}
}

func (o *Orchestrator) Subscribe() chan string {
	return o.subscriber
}

func (o *Orchestrator) emit(agentName, content string) {
	data, _ := json.Marshal(map[string]string{
		"agent": agentName,
		"content": content,
	})
	select {
	case o.subscriber <- string(data):
	default:
	}
}

func (o *Orchestrator) RunPipeline(title, description, location string) ([]AgentResult, error) {
	start := time.Now()
	var results []AgentResult

	o.emit("system", fmt.Sprintf("Starting pipeline for: %s", title))

	// Step 1: Intake Agent
	o.emit("intake", "Analyzing problem...")
	intakeResult, err := runAgent(o.client, "intake", title, description, location)
	elapsed := int(time.Since(start).Milliseconds())
	if err != nil {
		intakeResult = fmt.Sprintf("Error: %v", err)
	}
	results = append(results, AgentResult{Name: "intake", Output: intakeResult, Status: "done", Elapsed: elapsed})
	o.emit("intake", intakeResult)

	// Step 2: Analyst Agent
	o.emit("analyst", "Decomposing problem into root causes...")
	analystResult, err := runAgent(o.client, "analyst", title, description, location)
	elapsed = int(time.Since(start).Milliseconds())
	if err != nil {
		analystResult = fmt.Sprintf("Error: %v", err)
	}
	results = append(results, AgentResult{Name: "analyst", Output: analystResult, Status: "done", Elapsed: elapsed})
	o.emit("analyst", analystResult)

	// Step 3: Researcher Agent
	o.emit("researcher", "Searching for existing solutions and knowledge...")
	researcherResult, err := runAgent(o.client, "researcher", title, description, location)
	elapsed = int(time.Since(start).Milliseconds())
	if err != nil {
		researcherResult = fmt.Sprintf("Error: %v", err)
	}
	results = append(results, AgentResult{Name: "researcher", Output: researcherResult, Status: "done", Elapsed: elapsed})
	o.emit("researcher", researcherResult)

	// Step 4: Resource Mapper Agent
	o.emit("resource_mapper", "Identifying local community resources...")
	mapperResult, err := runAgent(o.client, "resource_mapper", title, description, location)
	elapsed = int(time.Since(start).Milliseconds())
	if err != nil {
		mapperResult = fmt.Sprintf("Error: %v", err)
	}
	results = append(results, AgentResult{Name: "resource_mapper", Output: mapperResult, Status: "done", Elapsed: elapsed})
	o.emit("resource_mapper", mapperResult)

	// Step 5: Solution Architect Agent
	o.emit("solution_architect", "Synthesizing final solution plan...")
	architectResult, err := runAgent(o.client, "solution_architect", title, description, location)
	elapsed = int(time.Since(start).Milliseconds())
	if err != nil {
		architectResult = fmt.Sprintf("Error: %v", err)
	}
	results = append(results, AgentResult{Name: "solution_architect", Output: architectResult, Status: "done", Elapsed: elapsed})
	o.emit("solution_architect", architectResult)

	o.emit("system", "Pipeline complete. All agents finished.")
	close(o.subscriber)

	return results, nil
}

func runAgent(client *featherless.Client, agentName, title, description, location string) (string, error) {
	prompt := getSystemPrompt(agentName)
	userMsg := fmt.Sprintf("Problem: %s\n\nDescription: %s\n\nLocation: %s", title, description, location)
	return client.Chat(prompt, userMsg)
}

func getSystemPrompt(agentName string) string {
	prompts := map[string]string{
		"intake": `You are the Intake Agent for HiveMind, a multi-agent community problem solver. Your job is to analyze a community problem and categorize it.

Extract:
1. Primary category (one of: education, health, environment, community, safety, infrastructure, technology, food, housing, economic)
2. Urgency level (low/medium/high/critical)
3. Key stakeholders involved
4. Geographic scope (local/regional/global)
5. 3-5 tags describing the problem

Output a structured JSON summary. Be concise and specific.`,
		"analyst": `You are the Analyst Agent for HiveMind. Your job is to break down the community problem into root causes and sub-problems.

For each root cause:
1. Identify the underlying issue
2. Rate its impact (1-10)
3. Suggest what needs to change
4. Note dependencies between causes

Think like a systems analyst. Look for second-order effects and feedback loops. Output as structured analysis.`,
		"researcher": `You are the Researcher Agent for HiveMind. Search your knowledge base for:
1. Existing solutions to similar problems
2. Case studies from other communities
3. Relevant research or best practices
4. Potential pitfalls to avoid
5. Organizations or programs already working on this

Provide actionable references, not generic advice. Include specific examples of what worked and what didn't.`,
		"resource_mapper": `You are the Resource Mapper Agent for HiveMind. Identify:
1. Local organizations that could help
2. Funding sources or grants
3. Volunteer networks
4. Technology platforms that could be leveraged
5. Community leaders or champions
6. In-kind resources (space, materials, expertise)

Be practical and specific. Consider low-cost and no-cost options first. Tailor to the location if provided.`,
		"solution_architect": `You are the Solution Architect Agent for HiveMind. Based on the analysis, research, and resources identified, synthesize:

1. A one-paragraph solution summary
2. 3-5 actionable steps to implement (be specific, concrete, and ordered)
3. Key resources needed (people, tech, funding)
4. Estimated timeline (short/medium/long term)
5. Success metrics (how to measure impact)
6. Potential challenges and mitigations

Output as a clear, structured action plan that a community could actually execute. Be realistic and practical.`,
	}

	if p, ok := prompts[agentName]; ok {
		return p
	}
	return "You are a helpful AI assistant for community problem solving."
}

// bit of a hack - agent prompt templates inline
var _ = func() string { return "HiveMind Agent System v1" }
