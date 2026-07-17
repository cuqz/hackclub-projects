"""Tool classification — implements Council R1 Issue 1 full-tool whitelist + deny-by-default.

Source data: docs/pipeline-tool-audit.md
"""

# Cross-stage exempt (infra tools, allowed in all stages)
ALL_EXEMPT: frozenset[str] = frozenset({
    "context_resolve", "pipeline_advance", "pipeline_status",
    "task_memo_add", "task_memo_read", "task_status",
    "team_list", "team_briefing", "team_status",
    "agent_list", "agent_template_list", "agent_activity_query",
    "memory_search", "team_knowledge", "os_health_check",
    "event_list", "cache_stats", "agent_heartbeat",
    "watchdog_check", "verify_completion",
    "decision_log", "prompt_version_list", "prompt_effectiveness",
    "project_list", "meeting_list", "meeting_read_messages",
    # CC built-in
    "Read", "SendMessage",
})

PLAN_CLASS_TOOLS: frozenset[str] = frozenset({
    "pattern_search", "what_if_analysis", "task_decompose",
    "meeting_template_list", "ecosystem_recipes",
    "agent_template_recommend", "find_skill",
    "briefing_resolve", "briefing_dismiss",
    # Plan + Verify also grouped into Plan
    "project_summary", "taskwall_view", "task_list_project",
    "loop_status", "report_list", "report_read",
    "briefing_list", "phase_list",
    # CC built-in
    "Glob", "Grep", "WebFetch", "WebSearch",
    # Plan-only CC built-in
    "TeamCreate",
})

EXECUTE_CLASS_TOOLS: frozenset[str] = frozenset({
    "task_run", "task_create", "task_update", "task_auto_match",
    "task_subtasks", "cache_clear", "channel_send", "channel_read",
    "channel_mentions", "agent_trust_update", "report_save",
    "file_lock_acquire", "file_lock_release", "file_lock_check",
    "file_lock_list", "failure_analysis", "pattern_record",
    "loop_start", "loop_pause", "loop_resume", "loop_next_task",
    "loop_advance", "loop_review", "error_budget_update",
    "project_update", "dismiss_project_registration",
    "meeting_attendance_check", "meeting_update", "debate_code_review",
    "git_status_check",
    # Plan + Execute dual-stage
    "meeting_create", "meeting_send_message", "meeting_conclude",
    "debate_start",
    # CC built-in
    "Edit", "Write", "Bash", "Agent", "TaskCreate",
    "EnterWorktree", "ExitWorktree", "NotebookEdit",
    # Glob/Grep also in Execute (Plan + Execute)
    "Glob", "Grep", "WebFetch",
})

VERIFY_CLASS_TOOLS: frozenset[str] = frozenset({
    "task_replay", "task_compare", "task_execution_trace",
    "diagnose_task_failure", "error_budget_status",
    "verify_run",  # pending Issue 2 implementation
    # Bash temporarily allowed in Verify until verify_run wrapper ships
    "Bash",
})

REQUIRES_USER_ACK: frozenset[str] = frozenset({
    "agent_register", "team_create", "team_delete", "team_close",
    "project_create", "project_delete", "phase_create",
    "scheduler_create", "scheduler_delete", "scheduler_pause",
    "git_auto_commit", "git_create_pr",
    "send_notification", "cross_project_send",
    # CC built-in
    "TeamCreate",
})

# Stage class → allowed tool set
STAGE_CLASS_WHITELIST: dict[str, frozenset[str]] = {
    "Plan": ALL_EXEMPT | PLAN_CLASS_TOOLS,
    "Execute": ALL_EXEMPT | EXECUTE_CLASS_TOOLS,
    "Verify": ALL_EXEMPT | VERIFY_CLASS_TOOLS,
}


def normalize_tool_name(raw: str) -> str:
    """Strip mcp__ai-team-os__ prefix, leave CC built-in names unchanged.

    Example: mcp__ai-team-os__task_create → task_create
    Example: Read → Read
    """
    return raw.removeprefix("mcp__ai-team-os__")


def is_allowed(tool_name: str, stage_class: str) -> bool:
    """Return True if the tool is allowed in the given stage_class (ignores user_ack)."""
    name = normalize_tool_name(tool_name)
    whitelist = STAGE_CLASS_WHITELIST.get(stage_class, frozenset())
    return name in whitelist


def requires_user_ack(tool_name: str) -> bool:
    """Return True if the tool requires user acknowledgement in autonomous mode."""
    return normalize_tool_name(tool_name) in REQUIRES_USER_ACK
