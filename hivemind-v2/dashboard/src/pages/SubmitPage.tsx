import { useState, useEffect, useRef } from 'react';
import { useSubmitProblem, useSolutions } from '../api/problems';
import { SSE_URL } from '../api/client';
import type { AgentUpdate } from '../types';
import { cn } from '../lib/utils';

const AGENT_LABELS: Record<string, string> = {
  intake: 'Intake Agent',
  analyst: 'Analyst Agent',
  researcher: 'Researcher Agent',
  resource_mapper: 'Resource Mapper',
  solution_architect: 'Solution Architect',
};

const AGENT_COLORS: Record<string, string> = {
  intake: 'text-cyan-400',
  analyst: 'text-purple-400',
  researcher: 'text-green-400',
  resource_mapper: 'text-pink-400',
  solution_architect: 'text-amber-400',
};

const AGENT_BORDERS: Record<string, string> = {
  intake: 'border-cyan-500/30',
  analyst: 'border-purple-500/30',
  researcher: 'border-green-500/30',
  resource_mapper: 'border-pink-500/30',
  solution_architect: 'border-amber-500/30',
};

export default function SubmitPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [agents, setAgents] = useState<Record<string, { content: string; status: string }>>({});
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [solutionText, setSolutionText] = useState('');
  const submit = useSubmitProblem();
  const { data: solutions } = useSolutions();
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (done && solutions && solutions.length > 0) {
      setSolutionText(solutions[0].summary.slice(0, 2000));
    }
  }, [done, solutions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description) return;

    setAgents({});
    setDone(false);
    setSolutionText('');
    setRunning(true);

    try {
      await submit.mutateAsync({ title, description, location: location || undefined });
    } catch {
      setRunning(false);
      return;
    }

    const es = new EventSource(SSE_URL);
    esRef.current = es;

    es.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (parsed.type === 'agent_update') {
          const update = JSON.parse(parsed.payload) as AgentUpdate;
          setAgents((prev) => ({
            ...prev,
            [update.agent]: {
              content: prev[update.agent]?.content
                ? prev[update.agent].content + '\n' + update.content
                : update.content,
              status: 'active',
            },
          }));
        } else if (parsed.type === 'complete') {
          setAgents((prev) => {
            const next = { ...prev };
            for (const key of Object.keys(next)) next[key] = { ...next[key], status: 'done' };
            return next;
          });
          setDone(true);
          setRunning(false);
          es.close();
        } else if (parsed.type === 'error') {
          setRunning(false);
          es.close();
        }
      } catch { /* ignore parse wobbles */ }
    };

    es.onerror = () => {
      setRunning(false);
      es.close();
    };
  };

  const agentNames = ['intake', 'analyst', 'researcher', 'resource_mapper', 'solution_architect'];

  return (
    <div className="space-y-10">
      {/* section header */}
      <div className="flex items-center gap-4">
        <span className="h-px w-8 bg-stroke" />
        <span className="text-[11px] font-medium uppercase tracking-[0.3em] text-muted-foreground">
          Submit
        </span>
      </div>

      <div>
        <h1 className="text-3xl font-light tracking-tight">
          What problem are you <span className="text-foreground font-normal">solving</span>?
        </h1>
        <p className="mt-2 max-w-lg text-sm text-muted-foreground">
          Describe a community issue. Five AI agents will analyze it and build a step-by-step solution.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="max-w-2xl space-y-6">
        <div className="space-y-5 rounded-2xl border border-white/5 bg-white/[0.02] p-8 backdrop-blur-xl">
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Problem Title
            </label>
            <input
              className="w-full rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none backdrop-blur-sm transition-all duration-200 focus:border-white/15 focus:shadow-[0_0_20px_rgba(255,255,255,0.03)]"
              placeholder="e.g. No recycling program in our school"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Description
            </label>
            <textarea
              className="w-full min-h-[120px] rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none backdrop-blur-sm transition-all duration-200 focus:border-white/15 focus:shadow-[0_0_20px_rgba(255,255,255,0.03)] resize-y"
              placeholder="Describe the problem. Who is affected? What have you tried? What resources are available?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Location <span className="font-normal lowercase tracking-normal text-muted-foreground/50">(optional)</span>
            </label>
            <input
              className="w-full rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none backdrop-blur-sm transition-all duration-200 focus:border-white/15 focus:shadow-[0_0_20px_rgba(255,255,255,0.03)]"
              placeholder="e.g. Cape Town, South Africa"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={running || !title || !description}
            className="group relative w-full overflow-hidden rounded-full bg-foreground py-3 text-sm font-medium text-background transition-all duration-200 hover:opacity-90 disabled:opacity-30"
          >
            <span className="relative z-10">
              {running ? 'Agents are working...' : 'Launch Agent Fleet'}
            </span>
            {!running && (
              <span className="absolute inset-0 -translate-x-full skew-x-12 bg-gradient-to-r from-transparent via-white/15 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
            )}
          </button>
        </div>
      </form>

      {/* agent fleet */}
      {(running || done) && (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className={cn(
                'h-2 w-2 rounded-full',
                done ? 'bg-green-500' : 'bg-foreground animate-pulse',
              )} />
              <span className="text-sm text-muted-foreground">
                {done ? 'All agents completed' : 'Agents are analyzing your problem...'}
              </span>
            </div>
          </div>

          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {agentNames.map((name) => {
              const state = agents[name];
              const isActive = state?.status === 'active';
              const isDone = state?.status === 'done';

              return (
                <div
                  key={name}
                  className={cn(
                    'group relative rounded-2xl border p-5 backdrop-blur-sm transition-all duration-300',
                    isActive
                      ? 'bg-white/[0.04] shadow-[0_0_30px_rgba(255,255,255,0.02)]'
                      : isDone
                        ? 'bg-white/[0.02]'
                        : 'bg-white/[0.01]',
                    isActive && AGENT_BORDERS[name],
                    isDone && 'border-green-500/10',
                    !isActive && !isDone && 'border-white/5',
                  )}
                >
                  {/* gradient glow on active */}
                  {isActive && (
                    <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent" />
                  )}

                  <div className="relative z-10">
                    <div className="flex items-center gap-2.5 mb-3">
                      <span className={cn(
                        'h-2 w-2 rounded-full transition-colors',
                        isActive ? 'bg-foreground animate-pulse' : isDone ? 'bg-green-500' : 'bg-white/10',
                      )} />
                      <span className={cn('text-sm font-medium', AGENT_COLORS[name] || '')}>
                        {AGENT_LABELS[name] || name}
                      </span>
                      <span className="ml-auto text-[11px] text-muted-foreground/60">
                        {isActive ? 'thinking...' : isDone ? 'done' : 'waiting'}
                      </span>
                    </div>
                    <div className={cn(
                      'max-h-48 overflow-y-auto text-xs leading-relaxed',
                      state?.content ? 'text-muted-foreground' : 'text-muted-foreground/30 italic',
                    )}>
                      {state?.content || 'Waiting for this agent to start...'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {done && solutionText && (
            <div className="relative rounded-2xl border border-white/5 bg-white/[0.02] p-8 backdrop-blur-xl">
              <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-amber-500/[0.02] to-transparent" />
              <div className="relative z-10">
                <div className="flex items-center gap-2 mb-4">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="text-amber-400">
                    <path d="M8 1l2.5 5.5L16 7.5l-4 4 1 5.5-5-3-5 3L4 11.5l-4-4 5.5-1L8 1z" fill="currentColor" />
                  </svg>
                  <span className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">
                    Solution
                  </span>
                </div>
                <div className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
                  {solutionText}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
