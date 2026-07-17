## Inspiration

We noticed something at our school. People talk about problems all the time — the broken water fountain, the food waste in the cafeteria, the lack of recycling bins — but nobody ever actually does anything about them. It's not because they don't care. It's because nobody knows where to start.

That's where the idea came from. What if you could describe a problem and have a team of AI agents figure out the rest? Not just give you generic advice, but actually break down the root causes, find existing solutions from other communities, identify local people who could help, and build a real action plan with timeline and metrics.

## What it does

Kintsugi is a multi-agent system. You submit a community problem — could be anything from "no recycling at our school" to "elderly neighbors can't access grocery delivery" — and five AI agents work through it in sequence:

1. **Intake Agent** categorizes the problem, tags it, assesses urgency
2. **Analyst Agent** breaks it into root causes and systemic issues
3. **Researcher Agent** finds similar cases from other communities and what worked
4. **Resource Mapper** identifies local organizations, funding sources, and volunteers
5. **Solution Architect** synthesizes everything into a concrete action plan with steps, resources, timeline, and success metrics

The agents stream their reasoning live to the dashboard. You watch them think in real-time. When they're done, you get a full solution plan.

## How we built it

Backend is Go with modernc.org/sqlite (zero-dependency SQLite). Each agent is just a prompt to the Featherless.ai API — we send the problem with a system prompt that defines the agent's role. The agents run sequentially because each one builds on the last.

Frontend is React 19 with Vite and shadcn/ui components for the UI. Tailwind CSS v4 for styling. We used the dashboard template from an open-source project called AI-company as the base because it already had a sidebar layout, dark theme, and WebSocket infrastructure.

Real-time streaming uses Server-Sent Events from the Go backend to the frontend. When you submit a problem, the backend starts the pipeline and pushes each agent's output as it comes in. The frontend just displays it.

## Challenges we ran into

Getting SSE to work with the Vite dev proxy was annoying. The EventSource API doesn't send headers so CORS was being weird. Ended up fixing it by having the frontend connect to the proxied path.

The Featherless.ai API requires a subscription to use. We built a mock mode that returns realistic-looking agent responses so the demo works without paying. The real integration is there, just needs an API key.

The AI-company template had like 600 files and was deeply coupled to Claude Code. Stripping it down to just the dashboard and replacing the API layer took several passes. Probably should have started fresh but the shadcn components were worth keeping.

Also port 8080 was always in use from a previous project. Kept getting bind errors until we found the old process.

## Accomplishments that we're proud of

The agent fleet view — watching all five cards populate with live reasoning looks genuinely cool. It actually looks like a team of people working.

The solution output is surprisingly good for just prompt engineering. The mock data reads like a real community action plan.

Dark glass UI came out clean. It actually looks like a real product, not a hackathon project.

## What we learned

Prompt engineering matters way more than we expected. The difference between a generic answer and a useful action plan is entirely in how you define the agent's role and constraints.

Go is great for this kind of thing. Single binary, no runtime dependencies, SQLite just works.

A working demo with mock data beats a broken demo with real AI every time. Ship what works, plug in the API later.

## What's next for Kintsugi

- Connect the Featherless.ai API for real (the code is there, just needs a key)
- Add user accounts so people can track their submitted problems
- Let the community upvote solutions so the best ones rise to the top
- A mobile version for people who aren't at a computer
- Multi-language support — community problems don't only happen in English
