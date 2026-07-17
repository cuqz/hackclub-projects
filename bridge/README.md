# Bridge

**Information for everyone. Offline-first. Multi-language. Free.**

Bridge is an offline-first AI-powered information platform built for underserved communities — people in rural areas, low-income regions, disaster zones, and anywhere internet access is limited or unavailable.

It delivers vital knowledge about **health, education, legal rights, and emergency preparedness** in **5 languages** (English, Swahili, French, Spanish, Hausa), running entirely offline after initial load. No internet required. No data costs. No barriers.

---

## The Problem

Over 3.5 billion people live in areas with limited or no internet access. When you can't get online:
- You can't look up first aid procedures
- You can't check your legal rights
- You can't find emergency contacts
- You can't access health education
- You can't ask someone for help

Existing solutions assume connectivity. Bridge doesn't.

## What It Does

**Content Library** — 40+ articles across health, education, legal rights, and emergency preparedness. Written in plain language. Available in 5 languages. Works offline.

**AI Assistant** — Ask questions in your language. Bridge searches its knowledge base and returns relevant answers. No ChatGPT dependency. No API costs.

**Community Q&A** — Ask questions, share knowledge, get answers from the community. Works offline, syncs when connected.

**Emergency Alerts** — Active alerts for cyclones, disease outbreaks, heatwaves, and other emergencies. Region-specific. Timely.

**Language Support** — English, Kiswahili, Français, Español, Hausa. More coming.

**PWA** — Install on any device. Works offline. No app store needed. Low bandwidth.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Go, SQLite (modernc.org/sqlite, no CGO) |
| Frontend | React 19, TypeScript, Vite |
| PWA | Service Worker, Manifest |
| AI | Rule-based + content matching (no external API) |
| Database | SQLite (embedded, zero config) |

---

## Quick Start

### Prerequisites
- Go 1.21+
- Node.js 18+

### Run

```bash
# Terminal 1: Start the backend
cd backend
go run . --addr :8080

# Terminal 2: Build and serve the frontend
cd frontend
npm install
npm run build
```

Then open http://localhost:8080

### Development

```bash
cd frontend
npm run dev     # Frontend on :5173

cd backend
go run .        # Backend on :8080, serves built frontend
```

---

## Project Structure

```
bridge/
├── backend/
│   ├── main.go          # Server, routes, handlers, DB init, seed data
│   ├── go.mod
│   └── bridge-server.exe
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main app with navigation
│   │   ├── components/
│   │   │   ├── HomePage.tsx      # Landing with category grid
│   │   │   ├── ContentPage.tsx   # Browse/search content library
│   │   │   ├── AIPage.tsx        # AI assistant chat interface
│   │   │   ├── CommunityPage.tsx # Q&A forum
│   │   │   ├── AlertsPage.tsx    # Emergency alerts
│   │   │   └── LanguageSelector.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   ├── public/
│   │   └── sw.js               # Service worker
│   ├── dist/                    # Built frontend
│   └── package.json
├── README.md
└── bridge.db                    # Created on first run
```

---

## Content

Bridge ships with 40+ articles across 4 categories in 5 languages:

| Category | Topics |
|----------|--------|
| Health | Clean water, first aid, nutrition, pregnancy, newborn care, mental health, emergency care |
| Education | Math skills, financial literacy, climate resilience, small business |
| Legal | Human rights, children's rights, women's rights, digital rights |
| Emergency | Disaster prep, flood safety, cyclone prep, emergency contacts |

All content is pre-loaded in the SQLite database — no download needed.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| GET | /api/content | List content (filters: ?language, ?category) |
| GET | /api/content/{id} | Get content by ID |
| GET | /api/content/search?q= | Search content |
| POST | /api/ai/ask | Ask AI (body: {question, language}) |
| GET | /api/questions | List questions (?language, ?category) |
| POST | /api/questions | Ask a question |
| POST | /api/questions/{id}/answer | Answer a question |
| GET | /api/alerts | All alerts |
| GET | /api/alerts/active | Active alerts |
| GET | /api/languages | Supported languages |

---

## Deployment

### Single binary
```bash
cd backend
go build -o bridge-server .
./bridge-server   # Serves API + frontend on :8080
```

### Docker
```dockerfile
FROM golang:1.21 AS backend
WORKDIR /app
COPY backend/ .
RUN go build -o server .

FROM node:18 AS frontend
WORKDIR /app
COPY frontend/ .
RUN npm install && npm run build

FROM alpine
COPY --from=backend /app/server .
COPY --from=frontend /app/dist ./frontend/dist
EXPOSE 8080
CMD ["./server"]
```

---

## License

MIT

---

*Built for Code for Humanity 2026-2027. Information for everyone, everywhere.*
