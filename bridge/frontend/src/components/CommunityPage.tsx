import { useState, useEffect } from "react";

interface Props { language: string }

const API_BASE = "";

export default function CommunityPage({ language }: Props) {
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newQuestion, setNewQuestion] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/questions?${new URLSearchParams({ language })}`)
      .then(r => r.json()).then(d => { setQuestions(d); setLoading(false); })
      .catch(() => { setQuestions([]); setLoading(false); });
  }, [language]);

  const submitQuestion = async () => {
    if (!newQuestion.trim() || submitting) return;
    setSubmitting(true);
    try {
      await fetch(`${API_BASE}/api/questions`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: newQuestion.trim(), language }),
      });
      setNewQuestion("");
      const res = await fetch(`${API_BASE}/api/questions?${new URLSearchParams({ language })}`);
      setQuestions(await res.json());
    } catch {}
    setSubmitting(false);
  };

  return (
    <div>
      <div className="py-6">
        <h2 className="text-xl font-bold" style={{ color: "var(--color-text-primary)" }}>Community</h2>
        <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>Ask questions and share knowledge with your community</p>
      </div>

      {/* Ask a question */}
      <div className="p-4 rounded-xl mb-6" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}>
        <textarea
          value={newQuestion}
          onChange={(e) => setNewQuestion(e.target.value)}
          placeholder="Ask a question..."
          rows={3}
          className="w-full px-3 py-2.5 rounded-xl text-sm outline-none resize-none transition-all duration-200"
          style={{ background: "var(--color-bg)", border: "1px solid var(--color-border)", color: "var(--color-text-primary)" }}
        />
        <div className="flex justify-end mt-2">
          <button
            onClick={submitQuestion}
            disabled={!newQuestion.trim() || submitting}
            className="px-5 py-2 rounded-xl text-white font-medium text-sm transition-all duration-200 disabled:opacity-40"
            style={{ background: "var(--color-accent)" }}
          >
            {submitting ? "Posting..." : "Post question"}
          </button>
        </div>
      </div>

      {/* Questions list */}
      {loading ? (
        <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
          <div className="w-5 h-5 rounded-full border-2 animate-spin mx-auto" style={{ borderColor: "var(--color-border)", borderTopColor: "var(--color-accent)" }} />
        </div>
      ) : questions.length === 0 ? (
        <div className="text-center py-16" style={{ color: "var(--color-text-muted)" }}>
          <p className="text-sm">No questions yet. Be the first to ask!</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {questions.map((q: any) => (
            <div key={q.id} className="p-4 rounded-xl" style={{ background: "var(--color-bg-card)", border: "1px solid var(--color-border)" }}>
              <div className="text-sm font-medium" style={{ color: "var(--color-text-primary)" }}>{q.text}</div>
              <div className="text-xs mt-1" style={{ color: "var(--color-text-muted)" }}>{q.category || "General"} · {q.date || "Recent"}</div>
              {q.answer && (
                <div className="mt-3 pt-3 text-sm leading-relaxed" style={{ borderTop: "1px solid var(--color-border)", color: "var(--color-text-secondary)" }}>
                  <span style={{ color: "var(--color-accent)" }}>Answer: </span>{q.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
