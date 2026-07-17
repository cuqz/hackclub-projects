"""Lifecycle templates for the new pipeline state machine.

Council R1 decision: pipeline_create no longer generates ceremonial subtasks.
Instead it writes PipelineState into task.config['pipeline'] using these templates.
"""

from __future__ import annotations

LIFECYCLE_TEMPLATES: dict[str, list[str]] = {
    "feature":   ["research", "meeting", "decompose", "implement", "test", "review", "retest"],
    "hotfix":    ["diagnose", "fix", "test"],
    "quick-fix": ["fix", "test"],
    "research":  ["research", "report"],
    "spike":     ["research", "implement"],
    "refactor":  ["decompose", "implement", "test", "review"],
    "debate":    ["meeting", "decision"],
}


def get_template(name: str) -> list[str]:
    """Return ordered stage list for a template name."""
    if name not in LIFECYCLE_TEMPLATES:
        raise ValueError(f"unknown template: {name}")
    return LIFECYCLE_TEMPLATES[name]


def get_next_stage(template: str, current: str) -> str | None:
    """Return the stage after current in the template, or None if current is last."""
    stages = get_template(template)
    try:
        idx = stages.index(current)
    except ValueError:
        raise ValueError(f"stage '{current}' not found in template '{template}'")
    if idx + 1 < len(stages):
        return stages[idx + 1]
    return None
