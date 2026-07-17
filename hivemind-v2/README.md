# HiveMind — Multi-Agent Community Problem Solver

> TechCommons Hacks V1 — Global & Local Impact

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**HiveMind** is a multi-agent AI system that analyzes community problems and generates actionable solutions. Submit a problem, and watch five specialized AI agents collaborate in real-time to understand, research, and build a concrete plan.

### The Problem

Communities everywhere face problems — broken infrastructure, food deserts, educational gaps, environmental issues. But most people don't know where to start solving them. They need help breaking down complex issues, finding existing solutions, and building a concrete action plan.

### How It Works

```
You submit a problem → 5 agents analyze it → Actionable solution
                              ↓
               Watch them think in real-time
```

**The 5 Agents:**
| Agent | Job |
|-------|-----|
| **Intake** | Categorizes, tags, assesses urgency |
| **Analyst** | Root cause decomposition |
| **Researcher** | Finds existing solutions & best practices |
| **Resource Mapper** | Identifies local orgs, funding, volunteers |
| **Solution Architect** | Synthesizes a step-by-step action plan |

### Tech Stack

- **Backend:** Go — modernc.org/sqlite, SSE streaming, Featherless.ai API
- **Frontend:** React 19 + Vite + Tailwind CSS v4 + shadcn/ui + TanStack Query
- **AI:** Featherless.ai (OpenAI-compatible, Qwen3-32B) — with built-in mock mode for demo
- **Database:** SQLite (WAL mode, zero-config)

### Quick Start (No API key required)

```bash
# Backend
cd backend
go run .     # runs in DEMO mode with mock data

# Frontend (new terminal)
cd dashboard
npm install
npm run dev

# Open http://localhost:5174
```

To use real AI, set `FEATHERLESS_API_KEY` env variable.

### Demo Video (3 min)

1. **0:00-0:15** — Landing / What is HiveMind
2. **0:15-0:30** — Dashboard shows community impact stats
3. **0:30-1:00** — Submit a problem ("No recycling program at our school")
4. **1:00-2:00** — Watch 5 agents work in real-time with live streaming
5. **2:00-2:30** — Solution appears: step-by-step action plan
6. **2:30-3:00** — Dashboard updates with new stats

### Project Structure

```
hivemind-v2/
├── backend/          # Go API server
│   ├── agents/       # 5 agent implementations
│   ├── api/          # HTTP handlers + SSE streaming
│   ├── db/           # SQLite store
│   └── featherless/  # AI client (+ mock fallback)
├── dashboard/        # React frontend
│   └── src/
│       ├── api/      # TanStack Query hooks
│       ├── pages/    # Dashboard + Submit page
│       └── components/layout/  # Sidebar, header
└── README.md
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/submit` | Submit a new problem |
| GET | `/api/problems` | List all problems |
| GET | `/api/solutions` | List all solutions |
| GET | `/api/stats` | Impact statistics |
| GET | `/api/events` | SSE stream for live agent updates |

### Built for TechCommons Hacks V1

Prize eligibility: Grand Prize, Social Impact Award, Technical Excellence.
