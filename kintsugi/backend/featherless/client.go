package featherless

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type Client struct {
	apiKey  string
	baseURL string
	model   string
	http    *http.Client
	mock    bool
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	MaxTokens   int       `json:"max_tokens,omitempty"`
	Temperature float64   `json:"temperature,omitempty"`
	Stream      bool      `json:"stream"`
}

type ChatResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
}

func New(apiKey, model string) *Client {
	if model == "" {
		model = "Qwen/Qwen3-32B"
	}
	mock := apiKey == "" || strings.EqualFold(apiKey, "mock")
	return &Client{
		apiKey:  apiKey,
		baseURL: "https://api.featherless.ai/v1",
		model:   model,
		mock:    mock,
		http: &http.Client{
			Timeout: 120 * time.Second,
		},
	}
}

func (c *Client) Mock() bool {
	return c.mock
}

// TODO: come back and add retries with backoff
func (c *Client) Chat(system, user string) (string, error) {
	if c.mock {
		return c.mockChat(system, user)
	}

	body := ChatRequest{
		Model:       c.model,
		MaxTokens:   2048,
		Temperature: 0.7,
		Stream:      false,
		Messages: []Message{
			{Role: "system", Content: system},
			{Role: "user", Content: user},
		},
	}

	payload, err := json.Marshal(body)
	if err != nil {
		return "", fmt.Errorf("marshal: %w", err)
	}

	req, err := http.NewRequest("POST", c.baseURL+"/chat/completions", bytes.NewReader(payload))
	if err != nil {
		return "", fmt.Errorf("new req: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("HTTP-Referer", "https://hivemind.dev")
	req.Header.Set("X-Title", "HiveMind")

	resp, err := c.http.Do(req)
	if err != nil {
		return "", fmt.Errorf("do req: %w", err)
	}
	defer resp.Body.Close()

	raw, _ := io.ReadAll(resp.Body)

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("featherless API %d: %s", resp.StatusCode, string(raw))
	}

	var chatResp ChatResponse
	if err := json.Unmarshal(raw, &chatResp); err != nil {
		return "", fmt.Errorf("unmarshal: %w", err)
	}

	if len(chatResp.Choices) == 0 {
		return "", fmt.Errorf("no choices in response")
	}

	return chatResp.Choices[0].Message.Content, nil
}

// mocked responses for demo mode — no API key needed
func (c *Client) mockChat(system, user string) (string, error) {
	time.Sleep(time.Duration(800+time.Now().Nanosecond()%1200) * time.Millisecond)

	agent := guessAgent(system)
	switch agent {
	case "intake":
		return mockIntake(user), nil
	case "analyst":
		return mockAnalyst(user), nil
	case "researcher":
		return mockResearcher(user), nil
	case "resource_mapper":
		return mockResourceMapper(user), nil
	case "solution_architect":
		return mockSolutionArchitect(user), nil
	default:
		return "Analysis complete. No critical issues detected.", nil
	}
}

func guessAgent(system string) string {
	switch {
	case strings.Contains(system, "Intake Agent"):
		return "intake"
	case strings.Contains(system, "Analyst Agent"):
		return "analyst"
	case strings.Contains(system, "Researcher Agent"):
		return "researcher"
	case strings.Contains(system, "Resource Mapper"):
		return "resource_mapper"
	case strings.Contains(system, "Solution Architect"):
		return "solution_architect"
	}
	return ""
}

func mockIntake(problem string) string {
	return fmt.Sprintf(`{
  "category": "community",
  "urgency": "high",
  "stakeholders": ["residents", "local businesses", "municipal council"],
  "scope": "local",
  "tags": ["social", "infrastructure", "community_action"]
}

Analysis: This is a community-level issue requiring coordination between residents and local government. The urgency is high due to the direct impact on quality of life.`)
}

func mockAnalyst(problem string) string {
	return `ROOT CAUSE ANALYSIS

1. Lack of Awareness (Impact: 7/10)
   - Community members don't know where to start
   - No central information channel exists

2. Resource Gap (Impact: 8/10)
   - No dedicated budget allocated
   - Volunteers untrained and disorganized

3. Coordination Failure (Impact: 6/10)
   - Multiple groups working in isolation
   - No shared timeline or accountability

SYSTEMIC INSIGHT: The core issue is the absence of a feedback loop between community needs and available resources. Fix that and the rest follows.`
}

func mockResearcher(problem string) string {
	return `EXISTING SOLUTIONS & CASE STUDIES

1. Community Action Network (Portland, OR)
   - Digital platform matching volunteers to local needs
   - 40% increase in participation within 6 months
   - Key lesson: gamification drives engagement

2. NeighborLink (Indianapolis)
   - Web app connecting seniors with nearby volunteers
   - 12,000+ requests fulfilled
   - Key lesson: trust is built through identity verification

3. Open Community Platform (Barcelona)
   - Open-source toolkit for participatory budgeting
   - 70,000+ citizens participated in first year
   - Key lesson: transparency is non-negotiable

BEST PRACTICES: Start small, show immediate wins, scale from there.`
}

func mockResourceMapper(problem string) string {
	return `LOCAL RESOURCES IDENTIFIED

ORGANIZATIONS
- Local community center (space, meeting rooms)
- Nearby school (volunteer network, communication channels)
- Small business association (funding, in-kind donations)

FUNDING
- Municipal community development grant (up to $5,000)
- Local crowdfunding platforms
- Corporate social responsibility programs

VOLUNTEER NETWORKS
- School parent-teacher association
- Neighborhood WhatsApp groups
- Local religious organizations

TECHNOLOGY
- Free Slack/Discord for coordination
- Google Workspace for non-profits (free tier)
- Open-source project management tools

RECOMMENDATION: Start with the community center as headquarters and the school's volunteer network as the initial workforce.`
}

func mockSolutionArchitect(problem string) string {
	return `ACTION PLAN

SUMMARY: Establish a community coordination hub that connects people who want to help with problems that need solving, using a digital platform and physical meeting space.

STEP 1: Community Survey (Week 1-2)
- Distribute digital and paper surveys
- Identify top 5 priority issues
- Map existing resources and gaps
- Success metric: 200+ responses collected

STEP 2: Launch Coordination Hub (Week 3-4)
- Set up Discord server for communication
- Establish weekly community meetings at local center
- Recruit 5 initial team leads
- Success metric: 50+ active members

STEP 3: First Pilot Project (Week 5-8)
- Pick the highest-priority issue from survey
- Run an 4-week targeted campaign
- Document process and outcomes
- Success metric: measurable improvement in pilot area

STEP 4: Scale & Sustain (Week 9+)
- Onboard 3 more neighborhood blocks
- Train volunteer coordinators
- Apply for municipal grant
- Success metric: 3 additional active projects

RESOURCES NEEDED: 2 volunteer coordinators, Discord server (free), meeting space (donated), survey tools (Google Forms - free)

TIMELINE: 8 weeks to first measurable impact
CHALLENGES: Sustaining volunteer engagement, securing funding
MITIGATIONS: Gamification (badges, leaderboards), transparent impact reporting`
}
