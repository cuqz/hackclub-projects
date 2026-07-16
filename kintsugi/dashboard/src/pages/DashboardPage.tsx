import { cn } from '../lib/utils';
import { useStats, useProblems, useSolutions } from '../api/problems';

const categoryColors: Record<string, string> = {
  education: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  health: 'bg-green-500/10 text-green-400 border-green-500/20',
  environment: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  community: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  safety: 'bg-red-500/10 text-red-400 border-red-500/20',
  technology: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  food: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  economic: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  infrastructure: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  housing: 'bg-pink-500/10 text-pink-400 border-pink-500/20',
};

const statusStyles: Record<string, string> = {
  processing: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  completed: 'bg-green-500/10 text-green-400 border-green-500/20',
  pending: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  default: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
};

export default function DashboardPage() {
  const { data: stats } = useStats();
  const { data: problems } = useProblems();
  const { data: solutions } = useSolutions();

  const statCards = [
    { label: 'Problems Submitted', value: stats?.total_problems ?? 0 },
    { label: 'Solutions Generated', value: stats?.total_solutions ?? 0 },
    { label: 'Avg Impact Score', value: stats?.avg_impact_score?.toFixed(1) ?? '—' },
    { label: 'Categories', value: Object.keys(stats?.by_category ?? {}).length },
  ];

  return (
    <div className="space-y-10">
      {/* section header */}
      <div className="flex items-center gap-4">
        <span className="h-px w-8 bg-stroke" />
        <span className="text-[11px] font-medium uppercase tracking-[0.3em] text-muted-foreground">
          Overview
        </span>
      </div>

      <div>
        <h1 className="text-3xl font-light tracking-tight">
          Community <span className="text-foreground font-normal">Impact</span>
        </h1>
        <p className="mt-2 max-w-lg text-sm text-muted-foreground">
          Track problems submitted, solutions generated, and impact across categories.
        </p>
      </div>

      {/* stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div
            key={card.label}
            className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-xl transition-all duration-300 hover:bg-white/[0.04] hover:border-white/10"
          >
            <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground/60">
              {card.label}
            </p>
            <p className="mt-3 text-4xl font-light tracking-tight text-foreground">
              {card.value}
            </p>
          </div>
        ))}
      </div>

      {/* two column: problems + solutions */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-5">
            <span className="h-px w-4 bg-white/10" />
            <span className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground/60">
              Recent Problems
            </span>
          </div>

          {(!problems || problems.length === 0) ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className="mb-3 text-white/10">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" />
                <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              <p className="text-sm text-muted-foreground/50">No problems yet</p>
              <p className="text-xs text-muted-foreground/30 mt-1">Submit one to get started</p>
            </div>
          ) : (
            <div className="space-y-1">
              {problems.slice(0, 6).map((p) => (
                <div
                  key={p.id}
                  className="flex items-center justify-between rounded-xl px-4 py-3 transition-colors hover:bg-white/[0.02]"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{p.title}</p>
                    <p className="text-xs text-muted-foreground/50 mt-0.5">
                      {p.category ? (
                        <span className="capitalize">{p.category}</span>
                      ) : ''}
                      {p.location && <span> &middot; {p.location}</span>}
                    </p>
                  </div>
                  <span className={cn(
                    'ml-3 shrink-0 rounded-full border px-3 py-0.5 text-[11px] font-medium capitalize',
                    statusStyles[p.status] || statusStyles.default,
                  )}>
                    {p.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-5">
            <span className="h-px w-4 bg-white/10" />
            <span className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground/60">
              Top Solutions
            </span>
          </div>

          {(!solutions || solutions.length === 0) ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className="mb-3 text-white/10">
                <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" />
              </svg>
              <p className="text-sm text-muted-foreground/50">No solutions yet</p>
              <p className="text-xs text-muted-foreground/30 mt-1">Solutions appear after agents finish</p>
            </div>
          ) : (
            <div className="space-y-1">
              {solutions.slice(0, 6).map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between rounded-xl px-4 py-3 transition-colors hover:bg-white/[0.02]"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm truncate">{s.summary.slice(0, 90)}</p>
                    <p className="text-[11px] text-muted-foreground/40 mt-0.5">Solution</p>
                  </div>
                  <div className="ml-3 shrink-0 text-right">
                    <p className="text-lg font-light text-amber-400">{s.impact_score}</p>
                    <p className="text-[10px] uppercase tracking-wider text-muted-foreground/40">Impact</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* categories */}
      {stats?.by_category && Object.keys(stats.by_category).length > 0 && (
        <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-5">
            <span className="h-px w-4 bg-white/10" />
            <span className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground/60">
              By Category
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stats.by_category).map(([cat, count]) => (
              <div
                key={cat}
                className={cn(
                  'flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-medium',
                  categoryColors[cat] || 'bg-white/5 text-muted-foreground border-white/10',
                )}
              >
                <span className="capitalize">{cat}</span>
                <span className="font-mono opacity-60">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

