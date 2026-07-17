# Bridge — Offline-First Information for the Underserved

> **Hackathon:** Code for Humanity 2026–2027
> **Track:** Social Impact & Accessibility

---

## Inspiration

**3.5 billion people** don't have reliable internet access. When a health emergency happens, a legal question arises, or a natural disaster strikes — they can't Google it. They can't look up their rights. They can't access the information that could save their lives.

Bridge was built to close that gap. An offline-first platform that puts critical information — health, legal, education, emergency — into the hands of people who need it most, regardless of their internet connection.

## What it does

Bridge is a Progressive Web App that works entirely offline after the initial load. It delivers:

- **40+ articles** across Health, Education, Legal, and Emergency categories
- **5 languages** — English, Swahili, French, Spanish, Hausa
- **AI Assistant** — rule-based content matching (no internet required)
- **Community Q&A** — offline-sync questions and answers
- **Emergency Alerts** — critical notifications that work without a signal

### How it works

1. **First visit** — user downloads the full content library (happens once)
2. **Works offline** — all 40+ articles, the AI assistant, and Q&A are cached locally
3. **No data costs** — zero ongoing internet usage after install
4. **PWA install** — works like a native app, no app store needed
5. **Background sync** — when connectivity returns, Q&A posts sync automatically

### Use Case: Maternal Health in Rural Kenya

A mother in a village with intermittent 2G access needs to know about pregnancy warning signs. She opens Bridge (installed as a PWA), navigates to Health → Maternal Care, and reads the article in Swahili — all offline. The AI Assistant answers follow-up questions using the cached knowledge base. No internet required.

## How we built it

| Layer | Technology |
|-------|-----------|
| **Backend** | Go with SQLite (no CGO) |
| **Frontend** | React 19 + TypeScript + Vite |
| **Offline Strategy** | PWA with Service Worker + Cache API |
| **Content** | 40+ articles in 5 languages, SQLite-backed |
| **AI Assistant** | Rule-based content-matching engine (zero external API calls) |

### Architecture

```
┌──────────────────────────────────────────────────┐
│              Bridge PWA (React 19)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Content  │  │ AI       │  │ Community│       │
│  │ Library  │  │ Assistant│  │ Q&A      │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│         ↕ Service Worker (Cache-First)            │
├──────────────────────────────────────────────────┤
│            Go Backend + SQLite                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Articles │  │ Q&A Sync │  │ Alerts   │       │
│  └──────────┘  └──────────┘  └──────────┘       │
└──────────────────────────────────────────────────┘
```

Key technical decisions:
- **No CGO** — pure Go SQLite means easy cross-compilation and deployment
- **Cache-first strategy** — prioritize offline availability; network is a bonus
- **Rule-based AI** — no API calls means no cost, no latency, no internet dependency
- **Single binary deployment** — backend embeds the frontend, deploy anywhere

## Challenges we ran into

- **Content translation at scale** — ensuring medical and legal accuracy across 5 languages required careful review. We couldn't just machine-translate; local experts would need to validate.
- **Service Worker complexity** — caching 40+ articles with media in multiple languages while keeping the initial bundle small required a chunked caching strategy.
- **Offline-first AI** — building an assistant that's actually useful without calling an API meant designing a robust rule engine that can match user questions to cached content accurately.

## Accomplishments that we're proud of

- A fully functional offline-first PWA that delivers real value without any internet
- 40+ articles across 4 critical categories in 5 languages — that's 200+ content items
- The AI Assistant works genuinely well offline — it's not a gimmick
- Clean, accessible UI designed for low-literacy users with large text and icon-based navigation

## What we learned

- **Offline-first is harder than it sounds**, but it's the right approach for the 3.5 billion people without reliable internet.
- **PWAs are incredibly powerful** — installable, offline-capable, no app store friction. This is the distribution model for underserved markets.
- **Simple technology wins for social impact.** No Kubernetes, no cloud AI APIs, no complex infrastructure. Go + SQLite + a Service Worker. That's it.

## What's next for Bridge

- **More languages** — add Portuguese, Arabic, Hindi, Bengali
- **Audio content** — text-to-speech for low-literacy users
- **SMS integration** — deliver critical information via text message for feature phones
- **Partner with NGOs** — distribute pre-loaded Bridge deployments to community health workers

---

## Demo

**Try it locally:**
```bash
git clone https://github.com/cuqz/bridge
cd bridge
cd backend && go run . &
cd ../frontend && npm install && npm run dev
```

Open the app, install it as a PWA, then disconnect your internet. Everything still works.
