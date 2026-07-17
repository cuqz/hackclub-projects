import { Link } from "react-router-dom";
import { motion } from "framer-motion";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.25, 0.1, 0.25, 1] } },
};

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1, delayChildren: 0.2 } },
};

const SKILLS = [
  { name: "Brand Architect", cat: "Strategy", icon: "🎯", desc: "Brand voice, tone, and positioning" },
  { name: "UI Artisan", cat: "Design", icon: "🎨", desc: "Design specs and wireframes" },
  { name: "Code Forger", cat: "Development", icon: "⚡", desc: "Production-ready code" },
  { name: "Content Weaver", cat: "Content", icon: "✍️", desc: "Copy, docs, and messaging" },
  { name: "Reviewer", cat: "Quality", icon: "🔍", desc: "Quality and consistency audit" },
  { name: "Hardener", cat: "Infrastructure", icon: "🛡️", desc: "Security and performance" },
  { name: "SEO Oracle", cat: "Marketing", icon: "📈", desc: "Search optimization" },
  { name: "Image Alchemist", cat: "Design", icon: "🖼️", desc: "Visual asset generation" },
  { name: "Security Guardian", cat: "Security", icon: "🔐", desc: "Threat modeling & audit" },
];

const STEPS = [
  { num: "01", title: "Pick your skills", desc: "Drag specialized AI agents from the palette. Each has unique capabilities." },
  { num: "02", title: "Connect the pipeline", desc: "Link agents together. Outputs flow automatically between nodes." },
  { num: "03", title: "Execute & ship", desc: "Run the workflow. Watch agents work in real-time, then ship the result." },
];

export function Landing() {
  return (
    <div>
      {/* ─── Hero ─── */}
      <section className="relative overflow-hidden" style={{ background: "hsl(var(--bg))" }}>
        {/* Ambient glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] rounded-full pointer-events-none" style={{ background: "radial-gradient(ellipse, hsl(210 50% 65% / 0.06), transparent 70%)" }} />

        <motion.div
          initial="hidden"
          animate="show"
          variants={stagger}
          className="relative max-w-[1200px] mx-auto px-6 md:px-10 lg:px-16 pt-32 md:pt-40 pb-24 md:pb-32 text-center"
        >
          <motion.div variants={fadeUp} className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-8" style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)", color: "hsl(var(--text-secondary))" }}>
            <span className="w-2 h-2 rounded-full" style={{ background: "hsl(120 50% 55%)" }} />
            LUMA Hackathon 2026
          </motion.div>

          <motion.h1 variants={fadeUp} className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight leading-[1.05]">
            Compose AI agents into{" "}
            <span className="gradient-text">automated workflows</span>
          </motion.h1>

          <motion.p variants={fadeUp} className="mt-6 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed" style={{ color: "hsl(var(--text-secondary))" }}>
            Drag, connect, and configure AI agents on a visual canvas.
            No glue code. No API wrangling. Just results.
          </motion.p>

          <motion.div variants={fadeUp} className="flex items-center justify-center gap-4 mt-10">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl text-white font-medium transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] hover:shadow-lg"
              style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))" }}
            >
              Start building
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </Link>
            <Link
              to="/pricing"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl font-medium transition-all duration-200"
              style={{ border: "1px solid hsl(var(--stroke))", color: "hsl(var(--text))" }}
            >
              View pricing
            </Link>
          </motion.div>

          <motion.div variants={fadeUp} className="mt-8 flex items-center justify-center gap-6 text-sm" style={{ color: "hsl(var(--muted))" }}>
            <span>✦ Free to start</span>
            <span className="w-1 h-1 rounded-full" style={{ background: "hsl(var(--muted))" }} />
            <span>No credit card</span>
            <span className="w-1 h-1 rounded-full" style={{ background: "hsl(var(--muted))" }} />
            <span>3 free workflows/mo</span>
          </motion.div>
        </motion.div>
      </section>

      {/* ─── How it works ─── */}
      <section className="py-24 md:py-32 px-6 md:px-10 lg:px-16 max-w-[1200px] mx-auto">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
        >
          <motion.h2 variants={fadeUp} className="text-3xl md:text-4xl font-bold tracking-tight text-center">How it works</motion.h2>
          <motion.p variants={fadeUp} className="mt-3 text-center max-w-lg mx-auto" style={{ color: "hsl(var(--text-secondary))" }}>
            Three steps to turn an idea into a working AI pipeline.
          </motion.p>

          <div className="grid md:grid-cols-3 gap-6 mt-16">
            {STEPS.map((step) => (
              <motion.div
                key={step.num}
                variants={fadeUp}
                className="relative p-8 rounded-2xl transition-all duration-300 hover:translate-y-[-2px]"
                style={{ background: "hsl(var(--surface))", border: "1px solid hsl(var(--stroke))" }}
              >
                <div className="text-4xl font-bold" style={{ color: "hsl(var(--accent) / 0.15)" }}>{step.num}</div>
                <h3 className="mt-4 text-lg font-semibold">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed" style={{ color: "hsl(var(--text-secondary))" }}>{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ─── Agent Skills ─── */}
      <section className="py-24 md:py-32 px-6 md:px-10 lg:px-16 max-w-[1200px] mx-auto">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
        >
          <motion.h2 variants={fadeUp} className="text-3xl md:text-4xl font-bold tracking-tight text-center">Agent skills</motion.h2>
          <motion.p variants={fadeUp} className="mt-3 text-center max-w-lg mx-auto" style={{ color: "hsl(var(--text-secondary))" }}>
            Specialized nodes you can compose like Lego blocks.
          </motion.p>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-16">
            {SKILLS.map((skill) => (
              <motion.div
                key={skill.name}
                variants={fadeUp}
                className="group p-5 rounded-xl transition-all duration-300 hover:translate-y-[-2px] cursor-default"
                style={{ background: "hsl(var(--surface))", border: "1px solid hsl(var(--stroke))" }}
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center text-lg shrink-0" style={{ background: "hsl(var(--accent) / 0.1)" }}>{skill.icon}</div>
                  <div className="min-w-0">
                    <div className="font-medium text-sm">{skill.name}</div>
                    <div className="text-xs mt-0.5" style={{ color: "hsl(var(--accent))" }}>{skill.cat}</div>
                    <div className="text-xs mt-1.5" style={{ color: "hsl(var(--text-secondary))" }}>{skill.desc}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ─── CTA ─── */}
      <section className="py-24 md:py-32 px-6 md:px-10 lg:px-16 max-w-[1200px] mx-auto">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          variants={stagger}
          className="relative rounded-3xl p-12 md:p-16 text-center overflow-hidden"
          style={{ background: "linear-gradient(135deg, hsl(210 50% 65% / 0.08), hsl(270 50% 60% / 0.05))", border: "1px solid hsl(var(--accent) / 0.15)" }}
        >
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[200px] rounded-full pointer-events-none" style={{ background: "radial-gradient(ellipse, hsl(210 50% 65% / 0.08), transparent 70%)" }} />
          
          <motion.h2 variants={fadeUp} className="text-3xl md:text-4xl font-bold tracking-tight relative">Ready to build?</motion.h2>
          <motion.p variants={fadeUp} className="mt-3 text-lg relative" style={{ color: "hsl(var(--text-secondary))" }}>
            Free to start. No credit card. 3 free workflows per month.
          </motion.p>
          <motion.div variants={fadeUp} className="mt-8 relative">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl text-white font-medium transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
              style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))" }}
            >
              Start building free
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-xs" style={{ color: "hsl(var(--muted))", borderTop: "1px solid hsl(var(--stroke))" }}>
        Built for LUMA Hackathon 2026. Open source.
      </footer>
    </div>
  );
}
