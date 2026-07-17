import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Content {
  id: number; title: string; body: string; category: string;
  language: string; tags: string[]; summary: string; created_at: string;
}

interface Props { language: string }

const API_BASE = "";
const CATEGORIES = [
  { id: "all", label: "All" }, { id: "health", label: "Health" },
  { id: "education", label: "Education" }, { id: "legal", label: "Legal" },
  { id: "emergency", label: "Emergency" },
];

export default function ContentPage({ language }: Props) {
  const [content, setContent] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("all");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Content | null>(null);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ language });
    if (category !== "all") params.set("category", category);
    fetch(`${API_BASE}/api/content?${params}`)
      .then(r => r.json()).then(d => { setContent(d); setLoading(false); })
      .catch(() => { setContent([]); setLoading(false); });
  }, [language, category]);

  const filtered = search
    ? content.filter(c => c.title.toLowerCase().includes(search.toLowerCase()) || c.summary.toLowerCase().includes(search.toLowerCase()))
    : content;

  return (
    <div>
      {/* Header */}
      <div className="py-6">
        <h2 className="text-xl font-bold" style={{ color: "var(--color-text-primary)" }}>Content Library</h2>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>Browse health, education, legal, and emergency information</p>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-sm" style={{ color: "var(--color-text-muted)" }}>🔍</span>
        <input
          className="w-full pl-9 pr-4 py-3 rounded-xl text-sm outline-none transition-all duration-200"
          style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
          type="search" placeholder="Search content..." value={search} onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* Category filters */}
      <div className="flex gap-2 overflow-x-auto pb-3 -mx-1 px-1" style={{ scrollbarWidth: "none" }}>
        {CATEGORIES.map(cat => (
          <button key={cat.id} onClick={() => setCategory(cat.id)}
            className="shrink-0 px-4 py-2 rounded-full text-xs font-medium transition-all duration-200"
            style={{
              background: category === cat.id ? "var(--color-accent)" : "var(--color-bg-card)",
              color: category === cat.id ? "white" : "var(--color-text-secondary)",
              border: category === cat.id ? "none" : "1px solid var(--color-border)",
            }}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Content list */}
      {loading ? (
        <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
          <div className="w-5 h-5 rounded-full border-2 animate-spin mx-auto" style={{ borderColor: "var(--color-border)", borderTopColor: "var(--color-accent)" }} />
          <p className="text-sm mt-3">Loading...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
          <div className="text-3xl mb-3 opacity-50">📚</div>
          <p className="text-sm">No content found for this selection.</p>
        </div>
      ) : (
        <motion.div className="flex flex-col gap-3 pb-4" initial="hidden" animate="show" variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}>
          {filtered.map((item) => (
            <motion.div key={item.id} variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
              onClick={() => setSelected(item)}
              className="p-4 rounded-xl cursor-pointer transition-all duration-200 hover:translate-y-[-1px]"
              style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}
            >
              <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--color-accent)" }}>{item.category}</div>
              <div className="font-semibold text-sm mb-1" style={{ color: "var(--color-text-primary)" }}>{item.title}</div>
              <div className="text-xs leading-relaxed mb-2" style={{ color: "var(--color-text-secondary)" }}>{item.summary}</div>
              <div className="flex gap-1.5 flex-wrap">
                {item.tags.map((tag, j) => <span key={j} className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(108,140,191,0.15)", color: "var(--color-accent)" }}>{tag}</span>)}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Article Modal */}
      <AnimatePresence>
        {selected && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center" style={{ background: "rgba(0,0,0,0.6)" }} onClick={() => setSelected(null)}
          >
            <motion.div initial={{ y: 100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 100, opacity: 0 }}
              className="w-full max-w-lg max-h-[80vh] overflow-y-auto mx-4 rounded-2xl" onClick={e => e.stopPropagation()}
              style={{ background: "var(--color-bg-elevated)", border: "1px solid var(--color-border)" }}
            >
              <div className="sticky top-0 flex items-center gap-3 p-4" style={{ background: "var(--color-bg-elevated)", borderBottom: "1px solid var(--color-border)" }}>
                <button onClick={() => setSelected(null)} className="text-sm" style={{ color: "var(--color-text-secondary)" }}>← Back</button>
                <div>
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: "var(--color-accent)" }}>{selected.category}</div>
                  <div className="font-semibold text-sm" style={{ color: "var(--color-text-primary)" }}>{selected.title}</div>
                </div>
              </div>
              <div className="p-5 text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--color-text-secondary)" }}>{selected.body}</div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
