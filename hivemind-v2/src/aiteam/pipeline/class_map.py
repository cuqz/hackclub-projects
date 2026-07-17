"""Stage 到 Class 的映射 — Council R1 决议核心，Phase 1 基础依赖。"""
from typing import Literal

StageClass = Literal["Plan", "Execute", "Verify"]

# 默认映射（来自 docs/pipeline-redesign.md 第 4/5 节）
STAGE_CLASS_MAP: dict[str, StageClass] = {
    "research":  "Plan",
    "meeting":   "Plan",
    "decompose": "Plan",
    "review":    "Plan",
    "diagnose":  "Plan",
    "implement": "Execute",
    "fix":       "Execute",
    "test":      "Verify",
    "retest":    "Verify",
    "report":    "Plan",    # research 模板的最后阶段
    "decision":  "Plan",    # debate 模板的最后阶段
}


def get_stage_class(
    stage: str,
    template_overrides: dict[str, StageClass] | None = None,
) -> StageClass:
    """获取 stage 类别。模板可覆盖默认映射（arch-overall 的预留扩展点）。"""
    if template_overrides and stage in template_overrides:
        return template_overrides[stage]
    if stage not in STAGE_CLASS_MAP:
        raise ValueError(f"unknown stage: {stage}")
    return STAGE_CLASS_MAP[stage]
