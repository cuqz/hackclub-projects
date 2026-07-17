import { motion } from "framer-motion";

interface Props {
  language: string;
  onNavigate: (page: "content" | "ai" | "community" | "alerts") => void;
}

const CATEGORIES = [
  { id: "health", label: "Health", icon: "🏥", desc: "First aid, nutrition, pregnancy, mental health" },
  { id: "education", label: "Education", icon: "📚", desc: "Math, finance, farming, business" },
  { id: "legal", label: "Legal Rights", icon: "⚖️", desc: "Rights, justice, protection" },
  { id: "emergency", label: "Emergency", icon: "🆘", desc: "Disaster prep, flood safety, cyclone" },
];

const COPY: Record<string, { title: string; subtitle: string; actions: string[] }> = {
  en: { title: "Information for", subtitle: "Free, offline-first access to health, education, legal, and emergency information. Built for communities that need it most.", actions: ["Ask the AI Assistant", "Browse Content Library", "Community Q&A", "Emergency Alerts"] },
  sw: { title: "Taarifa kwa", subtitle: "Huduma ya bure, inayofanya kazi bila mtandao kwa afya, elimu, haki za kisheria, na dharura.", actions: ["Muulize Msaidizi wa AI", "Vinjari Maktaba", "Maswali ya Jamii", "Tahadhari za Dharura"] },
  fr: { title: "Information pour", subtitle: "Plateforme hors ligne avec IA pour la santé, l'éducation, les droits légaux et les urgences.", actions: ["Demander à l'IA", "Explorer la bibliothèque", "Questions de la communauté", "Alertes d'urgence"] },
  es: { title: "Información para", subtitle: "Plataforma gratuita sin conexión con IA para salud, educación, derechos legales y emergencias.", actions: ["Preguntar a la IA", "Explorar biblioteca", "Preguntas de la comunidad", "Alertas de emergencia"] },
  ha: { title: "Bayani ga", subtitle: "Dandali na AI mara kyauta, mai aiki ba tare da intanet ba don lafiya, ilimi, hakkokin shari'a, da gaggawa.", actions: ["Tambayi AI", "Bincika ɗakin karatu", "Tambayoyin Al'umma", "Faɗakarwar Gaggawa"] },
};

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const itemAnim = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

export default function HomePage({ language, onNavigate }: Props) {
  const t = COPY[language] || COPY.en;

  return (
    <motion.div variants={container} initial="hidden" animate="show">
      {/* Hero */}
      <section className="text-center py-16">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-6" style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)", color: "var(--color-text-secondary)" }}>
          <span className="w-2 h-2 rounded-full" style={{ background: "var(--color-accent)" }} />
          Offline-first PWA
        </div>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight leading-tight">
          {t.title} <span style={{ color: "var(--color-accent)" }}>Everyone</span>
        </h1>
        <p className="mt-4 text-sm max-w-lg mx-auto leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
          {t.subtitle}
        </p>
      </section>

      {/* Category Grid */}
      <motion.div variants={itemAnim} className="grid grid-cols-2 gap-3 mb-6">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => onNavigate("content")}
            className="group relative rounded-xl p-5 text-center transition-all duration-300 hover:translate-y-[-2px]"
            style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}
          >
            <span className="text-2xl block mb-2">{cat.icon}</span>
            <div className="font-semibold text-sm" style={{ color: "var(--color-text-primary)" }}>{cat.label}</div>
            <div className="text-xs mt-1 leading-relaxed" style={{ color: "var(--color-text-muted)" }}>{cat.desc}</div>
          </button>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemAnim} className="flex flex-col gap-2.5">
        <QuickBtn icon="✦" label={t.actions[0]} sub="Get answers instantly" onClick={() => onNavigate("ai")} />
        <QuickBtn icon="📖" label={t.actions[1]} sub="Explore health, education, legal, emergency" onClick={() => onNavigate("content")} />
        <QuickBtn icon="💬" label={t.actions[2]} sub="Ask questions and share knowledge" onClick={() => onNavigate("community")} />
        <QuickBtn icon="🔔" label={t.actions[3]} sub="Stay informed about emergencies" onClick={() => onNavigate("alerts")} />
      </motion.div>
    </motion.div>
  );
}

function QuickBtn({ icon, label, sub, onClick }: { icon: string; label: string; sub: string; onClick: () => void }) {
  return (
    <button onClick={onClick} className="flex items-center gap-3 p-4 rounded-xl transition-all duration-300 text-left hover:translate-y-[-1px] group" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}>
      <div className="w-9 h-9 flex items-center justify-center rounded-lg shrink-0" style={{ background: "var(--color-accent)", color: "white", opacity: 0.9 }}>{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm" style={{ color: "var(--color-text-primary)" }}>{label}</div>
        <div className="text-xs mt-px" style={{ color: "var(--color-text-muted)" }}>{sub}</div>
      </div>
      <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>→</span>
    </button>
  );
}
