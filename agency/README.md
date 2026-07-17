# AGENCY — Visual AI Agent Orchestrator

**LUMA Hackathon 2026** | Built by [cuqz]

Compose AI agents into automated workflows. Drag, connect, and execute multi-agent pipelines that build, design, and ship.

## The Problem

Building with AI today means juggling tools, APIs, and prompts. Every new task means starting from scratch. There's no way to chain specialized AI agents into repeatable pipelines — so every project is a one-off.

AGENCY solves this by turning AI skills into composable nodes on a visual canvas.

## The Build

### Stack
- **Backend:** Go (gorilla/websocket, google/uuid) — concurrent agent orchestration, WebSocket streaming
- **Frontend:** React 19 + TypeScript + Vite, React Flow (canvas), Zustand (state), Framer Motion (animations), Tailwind CSS 4
- **Architecture:** REST API for CRUD, WebSocket for real-time execution streaming

### Key Technical Decisions
- **Go backend** chosen for goroutine-based concurrent agent execution — each skill node runs as an independent goroutine
- **WebSocket streaming** lets users watch agents execute in real-time (node_status, progress, output events)
- **React Flow** provides battle-tested canvas interaction (drag, connect, delete, pan, zoom)
- **Dark bento-grid UI** — 0a0a0a base, blue accent (#4a9eff), 12px radius cards, no glassmorphism, no gradients on text

### Architecture
```
Frontend (React/Vite) ←→ REST API ←→ Go Backend ←→ Agent Engine
                        ↕ WebSocket
                   Real-time Execution Stream
```

Each skill node executes via the agent engine which:
1. Resolves dependencies (topological sort on the DAG)
2. Executes nodes in dependency order
3. Streams status updates via WebSocket
4. Passes context between nodes in the pipeline

## The Demo

1. Create a workflow and name it
2. Drag skill nodes onto the canvas (Brand Architect, UI Artisan, Content Weaver, etc.)
3. Connect nodes to form a pipeline
4. Configure each node's parameters
5. Hit Execute — watch agents run in real-time
6. Review outputs from each agent

## Business Model

### Revenue Streams
- **Subscription tiers:** Free (3 workflows/mo), Pro ($19/mo, unlimited), Studio ($49/mo, teams)
- **Skill marketplace:** Community-contributed skills with 70/30 revenue split
- **API credits:** Pay-as-you-go for API-based execution beyond subscription

### Unit Economics
- COGS: ~$0.02/workflow at scale (API costs)
- Target margin: 70%+ (80% at scale)
- CAC payback: Under 3 months (self-serve + viral loop)

### Path to Sustainability
Target early-adopter developers first (TAM ~500K), then agency teams. Freemium funnel converts at projected 4-6%. Breakeven at 200 Pro subscribers ($3.8K MRR). Marketplace take rate adds 20-30%.

## Scalability

- **Horizontal scaling:** Go backend is stateless (workflows in memory, easily swapped for SQLite/PostgreSQL)
- **Concurrent execution:** Each agent runs in its own goroutine — scales across CPU cores
- **WebSocket fan-out:** Execution events can be broadcast to multiple subscribers
- **Pipeline DAG:** Topological sort ensures efficient parallel execution of independent branches
- **Storage:** In-memory for MVP, swap to PostgreSQL for production (one schema change)

## Getting Started

```bash
# Backend
cd backend
go run . --dns-addr :8080

# Frontend
cd frontend
npm install
npm run dev
```

## Skills (Agent Nodes)

| Skill | Category | Output |
|-------|----------|--------|
| Brand Architect | Design | Brand Kit (colors, typography, voice) |
| UI Artisan | Design | Design Tokens (spacing, components) |
| Content Weaver | Content | Copy (taglines, landing pages) |
| Security Guardian | Infrastructure | Security Config (CSP, headers) |
| Code Forger | Development | Source Code (components, APIs) |
| Documentation Sage | Content | Documentation (README, guides) |
| SEO Oracle | Marketing | SEO Report (keywords, metadata) |
| Image Alchemist | Design | Visual Assets (icons, illustrations) |
| Code Reviewer | Development | Review Report (bugs, security) |
