import { motion } from "framer-motion";
import { Link } from "react-router-dom";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] } },
};

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};

const PLANS = [
  {
    name: "Starter",
    price: "Free",
    desc: "Perfect for trying out AI workflows.",
    features: ["3 free workflows/month", "All skill nodes", "Basic execution", "Community support"],
    cta: "Get started",
    popular: false,
  },
  {
    name: "Pro",
    price: "$19",
    period: "/mo",
    desc: "For developers building real pipelines.",
    features: ["Unlimited workflows", "All skill nodes", "Parallel execution", "Priority support", "Custom skill builder"],
    cta: "Start trial",
    popular: true,
  },
  {
    name: "Studio",
    price: "$49",
    period: "/mo",
    desc: "For teams shipping at scale.",
    features: ["Everything in Pro", "Team collaboration", "API access", "Custom integrations", "Dedicated support", "SLA guarantee"],
    cta: "Contact sales",
    popular: false,
  },
];

export function Pricing() {
  return (
    <div className="max-w-[1200px] mx-auto px-6 md:px-10 lg:px-16 py-12 md:py-20">
      <motion.div
        initial="hidden"
        animate="show"
        variants={stagger}
      >
        {/* Header */}
        <motion.div variants={fadeUp} className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Simple pricing</h1>
          <p className="mt-3 text-lg" style={{ color: "hsl(var(--text-secondary))" }}>
            Start free. Scale when you need to.
          </p>
        </motion.div>

        {/* Pricing cards */}
        <div className="grid md:grid-cols-3 gap-6 max-w-[1000px] mx-auto">
          {PLANS.map((plan) => (
            <motion.div
              key={plan.name}
              variants={fadeUp}
              className="relative rounded-2xl p-8 transition-all duration-300 hover:translate-y-[-2px]"
              style={{
                background: plan.popular ? "linear-gradient(135deg, hsl(210 50% 65% / 0.08), hsl(270 50% 60% / 0.05))" : "hsl(var(--surface))",
                border: plan.popular ? "1px solid hsl(var(--accent) / 0.2)" : "1px solid hsl(var(--stroke))",
              }}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[11px] font-semibold tracking-wider uppercase" style={{ background: "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))", color: "white" }}>
                  Popular
                </div>
              )}

              <div className="text-sm font-semibold tracking-wider uppercase" style={{ color: "hsl(var(--accent))" }}>{plan.name}</div>
              
              <div className="mt-4 flex items-baseline gap-1">
                <span className="text-4xl font-bold">{plan.price}</span>
                {plan.period && <span className="text-sm" style={{ color: "hsl(var(--muted))" }}>{plan.period}</span>}
              </div>
              
              <p className="mt-2 text-sm" style={{ color: "hsl(var(--text-secondary))" }}>{plan.desc}</p>

              <ul className="mt-8 flex flex-col gap-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2.5 text-sm">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={plan.popular ? "hsl(var(--accent))" : "hsl(var(--text-secondary))"} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                    {f}
                  </li>
                ))}
              </ul>

              <Link
                to="/dashboard"
                className="mt-8 block text-center w-full px-5 py-3 rounded-xl text-sm font-medium transition-all duration-200"
                style={{
                  background: plan.popular ? "linear-gradient(135deg, hsl(210 50% 65%), hsl(240 45% 55%))" : "hsl(var(--bg))",
                  color: plan.popular ? "white" : "hsl(var(--text))",
                  border: plan.popular ? "none" : "1px solid hsl(var(--stroke))",
                }}
              >
                {plan.cta}
              </Link>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
