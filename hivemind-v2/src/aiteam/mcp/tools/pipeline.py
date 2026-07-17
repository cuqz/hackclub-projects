"""Pipeline (workflow stage) MCP tools — Phase 1.3 redesign.

pipeline_create: writes PipelineState into task.config, no longer generates
                 ceremonial subtasks (Council R1 decision).
pipeline_advance: advances current stage with optional force + triggered_by.
pipeline_status: returns PipelineState + recent stage_history.
"""

from __future__ import annotations

from typing import Any

from aiteam.mcp._base import _api_call


def register(mcp):
    """Register all pipeline-related MCP tools."""

    @mcp.tool()
    def pipeline_create(
        task_id: str,
        task_type: str,
    ) -> dict[str, Any]:
        """Initialize a pipeline on a task using a lifecycle template.

        Writes PipelineState into task.config['pipeline'] and records the first
        stage in stage_history. Does NOT generate ceremonial subtasks.

        Lifecycle templates:
          feature:   research → meeting → decompose → implement → test → review → retest
          hotfix:    diagnose → fix → test
          quick-fix: fix → test
          research:  research → report
          spike:     research → implement
          refactor:  decompose → implement → test → review
          debate:    meeting → decision

        Args:
            task_id: Task ID to attach the pipeline to
            task_type: Template name (feature/hotfix/quick-fix/research/spike/refactor/debate)

        Returns:
            Full PipelineState as a dict (template, current_stage, current_stage_class, ...)
        """
        return _api_call("POST", f"/api/tasks/{task_id}/pipeline/v2", {"task_type": task_type})

    @mcp.tool()
    def pipeline_advance(
        task_id: str,
        target_stage: str | None = None,
        force: bool = False,
        triggered_by: str = "manual",
    ) -> dict[str, Any]:
        """Advance the pipeline to the next (or specified) stage.

        When force=False, exit conditions are evaluated before advancing.
        When force=True, exit checks are skipped (Leader override).

        Args:
            task_id: Task ID with an active pipeline
            target_stage: Explicit target stage; if omitted, auto-selects next in sequence
            force: Skip exit condition checks (default False)
            triggered_by: Source of advance — "manual" / "auto" / "force" / "system"

        Returns:
            Updated PipelineState dict with from_stage, to_stage, and stage_history entry
        """
        payload: dict[str, Any] = {
            "force": force,
            "triggered_by": triggered_by,
        }
        if target_stage is not None:
            payload["target_stage"] = target_stage
        return _api_call("POST", f"/api/tasks/{task_id}/pipeline/v2/advance", payload)

    @mcp.tool()
    def pipeline_status(task_id: str) -> dict[str, Any]:
        """Get current pipeline state and recent stage history for a task.

        Args:
            task_id: Task ID with a pipeline

        Returns:
            PipelineState fields + last 5 stage_history entries
        """
        return _api_call("GET", f"/api/tasks/{task_id}/pipeline/v2")
