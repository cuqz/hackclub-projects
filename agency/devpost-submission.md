# AGENCY — Visual AI Agent Orchestrator

> **Hackathon:** LUMA Hackathon (Sep 20–28, 2026)
> **Track:** AI Tools & Developer Productivity

---

## Inspiration

Building an AI agent workflow today means writing glue code. You stitch together prompts, API calls, and output parsers — and if anything changes, you rewrite it all. There's no visual way to compose agents, no way to see the flow, no way to reuse a pipeline you built once.

AGENCY was built to change that. It's a **visual node-based editor** where you drag, connect, and configure AI agents into automated workflows — no glue code required.

Think of it as Zapier for AI agents, but more powerful — because each node isn't a simple API call, it's a full AI agent with its own reasoning, context, and capabilities.

## What it does

AGENCY lets you compose AI agents into executable workflows using a visual canvas:

- **Drag-and-drop skill nodes** — specialized agents for design, development, content, and infrastructure
- **Connect nodes visually** — outputs flow automatically between agents
- **Execute with one click** — the DAG resolver runs agents in parallel where possible, sequentially where needed
- **Real-time streaming** — watch each agent work, node by node
- **Reusable pipelines** — save workflows and run them again with different inputs

### Example workflow: "Build a Landing Page"

```
[Brand Architect] → [UI Artisan] → [Code Forger] → [Reviewer]
                                     ↓
                               [Content Weaver]
```

Each node is a specialized agent. The Brand Architect defines the voice, the UI Artisan creates the design specs, the Code Forger writes the HTML/CSS, and the Reviewer checks the output. All of this runs with one click.

## How we built it

| Layer | Technology |
|-------|-----------|
| **Backend** | Go — concurrent agent execution with goroutines |
| **Real-time** | WebSocket streaming for live node status |
| **Frontend** | React 19 + TypeScript + Vite |
| **Visual Canvas** | React Flow — drag, connect, configure nodes |
| **State Management** | Zustand — persistent workflow state |
| **Styling** | Tailwind CSS v4 |

### Architecture

```
┌──────────────────────────────────────────────────┐
│              AGENCY Canvas (React 19)             │
│  [Skill Palette] ↔ [Node Editor] ↔ [Workflow]   │
│                       ↕ WebSocket                 │
│              Real-time Node Status                │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│              Go Execution Engine                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Node A   │→ │ Node B   │→ │ Node C   │        │
│  │ (Design) │  │ (Code)   │  │ (Review) │        │
│  └──────────┘  └──────────┘  └──────────┘        │
│  DAG Resolver → Topological Sort → Parallel Exec  │
└──────────────────────────────────────────────────┘
```

### Skill Nodes

| Node | Purpose |
|------|---------|
| Brand Architect | Defines brand voice, tone, and positioning |
| UI Artisan | Generates design specs and wireframes |
| Code Forger | Writes production-ready code |
| Content Weaver | Creates copy, documentation, and messaging |
| Reviewer | Audits output for quality and consistency |
| Hardener | Security and performance optimization |

## Challenges we ran into

- **Canvas performance at scale** — React Flow struggled with 50+ connected nodes. We had to implement virtualization and level-of-detail rendering.
- **DAG execution with WebSocket feedback** — sending real-time status updates for each node while maintaining correct topological order required careful goroutine management.
- **Node configuration UX** — making each skill node's configuration form intuitive without cluttering the canvas was a constant design tension.

## Accomplishments that we're proud of

- A fully functional visual node editor where you can build, run, and save real AI workflows
- Go backend handles concurrent agent execution with millisecond-level streaming
- The "Build a Landing Page" workflow actually produces deployable code in under 2 minutes
- Clean, professional UI that looks like a real product, not a hackathon prototype

## What we learned

- **Visual programming for AI is the future.** Dragging nodes is 10x faster than writing glue code for common patterns.
- **Go's goroutine model is ideal** for concurrent agent execution — each node runs in its own goroutine, results flow through channels, and the main thread just orchestrates.
- **The business model matters even at a hackathon.** We designed the monetization (free tier → pro → studio) alongside the architecture, which forced us to think about scalability from day one.

## What's next for AGENCY

- **Skill Marketplace** — community-shared nodes with 70/30 revenue split
- **Custom node SDK** — let anyone build their own skill nodes
- **Workflow templates** — pre-built pipelines for common use cases
- **Persistent storage** — PostgreSQL backend for saved workflows and teams

---

## Demo

**Clone and run:**
```bash
git clone https://github.com/cuqz/agency
cd agency
cd backend && go run . &
cd ../frontend && npm install && npm run dev
```

Open the canvas, drag a few nodes, connect them, and hit Execute. Watch the agents work in real-time.
