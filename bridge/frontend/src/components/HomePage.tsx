import { motion } from "framer-motion";

interface Props { language: string; onNavigate: (page: "content" | "ai" | "community" | "alerts") => void; }

const ICONS = [
  <svg key="h" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z"/><path d="M12 7v5l3 3"/></svg>,
  <svg key="e" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>,
  <svg key="l" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  <svg key="e2" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>,
  <svg key="s" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 2a4 4 0 0 0-4 4v1H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2V6a4 4 0 0 0-4-4Z"/><path d="M8 9h8"/></svg>,
  <svg key="b" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>,
  <svg key="c" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  <svg key="a" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>,
];

const CATEGORIES = [
  { id: "health", label: "Health", icon: ICONS[0], desc: "First aid, nutrition, pregnancy, mental health", color: "#4a9eff" },
  { id: "education", label: "Education", icon: ICONS[1], desc: "Math, finance, farming, business", color: "#22c55e" },
  { id: "legal", label: "Legal Rights", icon: ICONS[2], desc: "Rights, justice, protection", color: "#a855f7" },
  { id: "emergency", label: "Emergency", icon: ICONS[3], desc: "Disaster prep, flood safety, cyclone", color: "#ef4444" },
];

const QUICK = [
  { icon: ICONS[4], label: "Ask the AI Assistant", sub: "Get answers instantly", page: "ai" as const },
  { icon: ICONS[5], label: "Browse Content Library", sub: "Explore health, education, legal, emergency", page: "content" as const },
  { icon: ICONS[6], label: "Community Q&A", sub: "Ask questions and share knowledge", page: "community" as const },
  { icon: ICONS[7], label: "Emergency Alerts", sub: "Stay informed about emergencies", page: "alerts" as const },
];

const container = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const itemAnim = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

export default function HomePage({ onNavigate }: Props) {
  return (
    <motion.div variants={container} initial="hidden" animate="show">
      <section className="text-center py-16">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-6" style={{ background: "rgba(74,158,255,0.08)", border: "1px solid rgba(74,158,255,0.15)", color: "#4a9eff" }}>
          <span className="w-1.5 h-1.5 rounded-full bg-[#4a9eff]" />
          Offline-first PWA
        </div>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight leading-tight">
          Information for <span style={{ color: "#4a9eff" }}>Everyone</span>
        </h1>
        <p className="mt-4 text-sm max-w-lg mx-auto leading-relaxed" style={{ color: "#a0a0a0" }}>
          Free, offline-first access to health, education, legal, and emergency information. Built for communities that need it most.
        </p>
      </section>

      <motion.div variants={itemAnim} className="grid grid-cols-2 gap-3 mb-6">
        {CATEGORIES.map((cat) => (
          <button key={cat.id} onClick={() => onNavigate("content")}
            className="group relative rounded-xl p-5 text-center transition-all duration-300 hover:-translate-y-0.5"
            style={{ background: "#141414", border: "1px solid rgba(255,255,255,0.06)" }}>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-3" style={{ background: `${cat.color}15`, color: cat.color }}>{cat.icon}</div>
            <div className="font-semibold text-sm">{cat.label}</div>
            <div className="text-xs mt-1 leading-relaxed" style={{ color: "#555" }}>{cat.desc}</div>
          </button>
        ))}
      </motion.div>

      <motion.div variants={itemAnim} className="flex flex-col gap-2.5">
        {QUICK.map((q, i) => (
          <button key={i} onClick={() => onNavigate(q.page)} className="flex items-center gap-3 p-4 rounded-xl transition-all duration-300 text-left hover:-translate-y-0.5 group" style={{ background: "#141414", border: "1px solid rgba(255,255,255,0.06)" }}>
            <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0" style={{ background: "rgba(74,158,255,0.12)", color: "#4a9eff" }}>{q.icon}</div>
            <div className="flex-1 min-w-0">
              <div className="font-medium text-sm">{q.label}</div>
              <div className="text-xs mt-px" style={{ color: "#555" }}>{q.sub}</div>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#555" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        ))}
      </motion.div>
    </motion.div>
  );
}
