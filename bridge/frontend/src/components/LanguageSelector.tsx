interface Props { current: string; onChange: (lang: string) => void }

const LANGUAGES: Record<string, string> = {
  en: "EN", sw: "SW", fr: "FR", es: "ES", ha: "HA",
};

export default function LanguageSelector({ current, onChange }: Props) {
  return (
    <select value={current} onChange={e => onChange(e.target.value)}
      className="bg-bg-card border border-border rounded-lg text-text-primary text-xs px-2 py-1.5 outline-none cursor-pointer hover:border-accent/30 transition-colors"
    >
      {Object.entries(LANGUAGES).map(([code, label]) => (
        <option key={code} value={code}>{label}</option>
      ))}
    </select>
  );
}
