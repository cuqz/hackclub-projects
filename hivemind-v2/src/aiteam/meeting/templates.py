"""Meeting template loader — reads from plugin/skills/meeting-facilitate/templates/*.md."""

from __future__ import annotations

from pathlib import Path

import yaml

_TEMPLATE_DIR = (
    Path(__file__).parent.parent.parent.parent
    / "plugin"
    / "skills"
    / "meeting-facilitate"
    / "templates"
)

_cache: tuple[dict, dict] | None = None


def _load_templates() -> tuple[dict, dict]:
    """Scan template dir, parse frontmatter, return (rounds_dict, keywords_dict)."""
    rounds: dict = {}
    keywords: dict = {}
    if not _TEMPLATE_DIR.exists():
        return rounds, keywords

    for md_file in sorted(_TEMPLATE_DIR.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    fm = yaml.safe_load(content[3:end])
                    name = fm.get("template_name")
                    if name:
                        rounds[name] = {
                            "total_rounds": fm.get("total_rounds", 0),
                            "description": fm.get("description", ""),
                            "rounds": fm.get("rounds", []),
                        }
                        kws = fm.get("keywords")
                        if kws:
                            keywords[name] = kws
        except Exception:
            continue
    return rounds, keywords


def _get_cached() -> tuple[dict, dict]:
    global _cache
    if _cache is None:
        _cache = _load_templates()
    return _cache


class _LazyDict:
    """Proxy dict that loads templates on first access."""

    def __init__(self, key_idx: int) -> None:
        self._idx = key_idx

    def __getitem__(self, k: str):
        return _get_cached()[self._idx][k]

    def __contains__(self, k: object) -> bool:
        return k in _get_cached()[self._idx]

    def __iter__(self):
        return iter(_get_cached()[self._idx])

    def __len__(self) -> int:
        return len(_get_cached()[self._idx])

    def keys(self):
        return _get_cached()[self._idx].keys()

    def values(self):
        return _get_cached()[self._idx].values()

    def items(self):
        return _get_cached()[self._idx].items()

    def get(self, k: str, default=None):
        return _get_cached()[self._idx].get(k, default)


TEMPLATE_ROUNDS: dict[str, dict] = _LazyDict(0)  # type: ignore[assignment]
TEMPLATE_KEYWORDS: dict[str, list[str]] = _LazyDict(1)  # type: ignore[assignment]


def recommend_template(topic: str) -> tuple[str, str]:
    """Recommend a meeting template based on topic text.

    Returns (template_name, reason). Falls back to 'brainstorm' if no match.
    """
    topic_lower = topic.lower()
    scores: dict[str, int] = {}
    for tpl, keywords in TEMPLATE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in topic_lower)
        if score > 0:
            scores[tpl] = score

    if not scores:
        return "brainstorm", "no keyword match, defaulting to brainstorm"

    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    return best, f"matched {scores[best]} keyword(s) for '{best}'"
