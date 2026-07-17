import { useState, useRef, useEffect } from "react";

interface Props { language: string }
const API_BASE = "";

const WELCOME: Record<string, string> = {
  en: "Hello! Ask me anything about health, education, legal rights, or emergency preparedness.",
  sw: "Habari! Uliza chochote kuhusu afya, elimu, haki za kisheria, au maandalizi ya dharura.",
  fr: "Bonjour! Demandez-moi tout sur la santé, l'éducation, le droit ou la préparation aux urgences.",
  es: "¡Hola! Pregúntame cualquier cosa sobre salud, educación, derechos legales o emergencias.",
  ha: "Sannu! Tambaye ni komai game da lafiya, ilimi, hakkoki, ko shirye-shiryen gaggawa.",
};

export default function AIPage({ language }: Props) {
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([{ role: "bot", text: WELCOME[language] || WELCOME.en }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEnd = useRef<HTMLDivElement>(null);

  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: "smooth" }) }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput("");
    setMessages(p => [...p, { role: "user", text: msg }]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/ai/ask`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: msg, language }) });
      const data = await res.json();
      setMessages(p => [...p, { role: "bot", text: data.answer }]);
    } catch {
      setMessages(p => [...p, { role: "bot", text: "Sorry, couldn't reach the server." }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      {/* Header */}
      <div className="py-6">
        <h2 className="text-xl font-bold" style={{ color: "var(--color-text-primary)" }}>AI Assistant</h2>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>Ask questions about health, education, legal rights, and more</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 pb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-xs md:max-w-md lg:max-w-lg p-3 rounded-2xl text-sm leading-relaxed ${
              msg.role === "user" ? "rounded-br-md" : "rounded-bl-md"
            }`} style={{
              background: msg.role === "user" ? "var(--color-accent)" : "var(--color-bg-card)",
              border: msg.role === "user" ? "none" : "1px solid var(--color-border)",
              color: msg.role === "user" ? "white" : "var(--color-text-primary)",
            }}>{msg.text}</div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="p-4 rounded-2xl rounded-bl-md flex gap-1.5" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}>
              {[0, 1, 2].map((i) => (
                <div key={i} className="w-2 h-2 rounded-full animate-bounce" style={{ background: "var(--color-text-muted)", animationDelay: `${i * 0.15}s` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={chatEnd} />
      </div>

      {/* Input */}
      <div className="pt-3 pb-4 sticky bottom-0" style={{ background: "var(--color-bg)" }}>
        <div className="flex gap-2">
          <input
            className="flex-1 px-4 py-3 rounded-xl text-sm outline-none transition-all duration-200"
            style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
            placeholder="Ask a question..." value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()}
          />
          <button
            className="px-6 py-3 rounded-xl text-white font-medium text-sm transition-all duration-200 disabled:opacity-40"
            style={{ background: "var(--color-accent)" }}
            onClick={send} disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
