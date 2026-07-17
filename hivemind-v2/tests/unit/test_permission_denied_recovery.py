"""Unit tests for permission_denied_recovery hook (diagnose_denial classifier version)."""

from __future__ import annotations

import importlib
import io
import json
import sys
import time
from unittest.mock import MagicMock, patch


def _import_module():
    mod_name = "aiteam.hooks.permission_denied_recovery"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


def _fake_stdin_buffer(payload: dict):
    raw = json.dumps(payload).encode("utf-8")
    buf = MagicMock()
    buf.read.return_value = raw
    return buf


def _build_classification(category: str, hint: str = "", additional_context: str = "") -> dict:
    return {"category": category, "hint": hint, "additional_context": additional_context}


def _run_main(
    payload: dict,
    retry_state: dict | None = None,
    api_response: dict | None = ...,  # type: ignore[assignment]
) -> tuple[str, int]:
    """Run main() with given payload.

    api_response=... (Ellipsis default) → API call returns _fallback_classify output (simulates unreachable).
    api_response=None → _call_diagnose returns None (API unreachable, triggers fallback).
    api_response=dict → _call_diagnose returns that dict.
    """
    mod = _import_module()
    if retry_state is None:
        retry_state = {}

    captured_stdout = io.StringIO()
    exit_code_holder = [0]

    def fake_exit(code=0):
        exit_code_holder[0] = code
        raise SystemExit(code)

    fake_stdin = MagicMock()
    fake_stdin.buffer = _fake_stdin_buffer(payload)

    if api_response is ...:
        # Let the real _call_diagnose fail silently → fallback path
        diagnose_mock = patch.object(mod, "_call_diagnose", return_value=None)
    else:
        diagnose_mock = patch.object(mod, "_call_diagnose", return_value=api_response)

    with (
        patch("aiteam.hooks.permission_denied_recovery.sys.stdin", fake_stdin),
        patch("aiteam.hooks.permission_denied_recovery.sys.stdout", captured_stdout),
        patch("aiteam.hooks.permission_denied_recovery.sys.stderr", io.StringIO()),
        patch.object(mod, "_load_retry_state", return_value=retry_state),
        patch.object(mod, "_save_retry_state"),
        patch.object(mod, "_post_event"),
        patch.object(mod, "_post_briefing_async"),
        patch("aiteam.hooks.permission_denied_recovery.sys.exit", side_effect=fake_exit),
        diagnose_mock,
    ):
        try:
            mod.main()
        except SystemExit:
            pass

    return captured_stdout.getvalue(), exit_code_holder[0]


# ---------------------------------------------------------------------------
# Tests: API returns recoverable_with_retry
# ---------------------------------------------------------------------------


class TestRecoverableWithRetry:
    def test_first_retry_allowed(self):
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/data.json"},
            "reason": "rate limit exceeded",
            "tool_use_id": "toolu_retry1",
            "session_id": "sess1",
        }
        api_resp = _build_classification(
            "recoverable_with_retry",
            hint="Rate limit — retrying.",
        )
        stdout, code = _run_main(payload, retry_state={}, api_response=api_resp)
        assert code == 0
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["retry"] is True

    def test_second_retry_blocked_anti_loop(self):
        tool_use_id = "toolu_retry2"
        already_retried = {tool_use_id: {"ts": time.time(), "retried": True}}
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/data.json"},
            "reason": "transient error",
            "tool_use_id": tool_use_id,
            "session_id": "sess2",
        }
        api_resp = _build_classification("recoverable_with_retry", hint="Transient.")
        stdout, code = _run_main(payload, retry_state=already_retried, api_response=api_resp)
        assert code == 0
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["retry"] is False
        assert "already attempted" in result["hookSpecificOutput"].get("additionalContext", "")

    def test_retry_without_tool_use_id_is_blocked(self):
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/x"},
            "reason": "temporary",
            "tool_use_id": "",  # no ID
            "session_id": "sess3",
        }
        api_resp = _build_classification("recoverable_with_retry")
        stdout, code = _run_main(payload, retry_state={}, api_response=api_resp)
        assert code == 0
        result = json.loads(stdout)
        # Without tool_use_id, _already_retried returns False on "" but _mark_retried
        # writes "" key — still should retry once (empty string is falsy, treated as no-id)
        # The hook checks `if tool_use_id and not _already_retried(...)` so empty → blocked
        assert result["hookSpecificOutput"]["retry"] is False


# ---------------------------------------------------------------------------
# Tests: API returns recoverable_with_workaround
# ---------------------------------------------------------------------------


class TestRecoverableWithWorkaround:
    def test_no_retry_with_workaround_context(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/home/user/.claude/data/reports/report.md"},
            "reason": "write to OS data directory blocked",
            "tool_use_id": "toolu_write1",
            "session_id": "sess4",
        }
        api_resp = _build_classification(
            "recoverable_with_workaround",
            hint="Use report_save instead.",
            additional_context="Call report_save() MCP tool to save reports.",
        )
        stdout, code = _run_main(payload, api_response=api_resp)
        assert code == 0
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["retry"] is False
        ctx = result["hookSpecificOutput"].get("additionalContext", "")
        assert "report_save" in ctx


# ---------------------------------------------------------------------------
# Tests: API returns needs_user_approval
# ---------------------------------------------------------------------------


class TestNeedsUserApproval:
    def test_no_retry_and_briefing_created(self):
        mod = _import_module()
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "git push origin main --force"},
            "reason": "force push to main branch denied",
            "tool_use_id": "toolu_bash1",
            "session_id": "sess5",
        }
        api_resp = _build_classification(
            "needs_user_approval",
            hint="Create a briefing to request user approval.",
            additional_context="Dangerous Bash command blocked.",
        )
        posted_briefings = []
        fake_stdin = MagicMock()
        fake_stdin.buffer = _fake_stdin_buffer(payload)

        with (
            patch("aiteam.hooks.permission_denied_recovery.sys.stdin", fake_stdin),
            patch("aiteam.hooks.permission_denied_recovery.sys.stdout", io.StringIO()),
            patch("aiteam.hooks.permission_denied_recovery.sys.stderr", io.StringIO()),
            patch.object(mod, "_load_retry_state", return_value={}),
            patch.object(mod, "_save_retry_state"),
            patch.object(mod, "_post_event"),
            patch.object(
                mod,
                "_post_briefing_async",
                side_effect=lambda title, description, session_id: posted_briefings.append(title),
            ),
            patch.object(mod, "_call_diagnose", return_value=api_resp),
            patch("aiteam.hooks.permission_denied_recovery.sys.exit", side_effect=SystemExit),
        ):
            try:
                mod.main()
            except SystemExit:
                pass

        assert len(posted_briefings) == 1
        assert "Bash" in posted_briefings[0]

    def test_no_retry_output(self):
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
            "reason": "destructive command denied",
            "tool_use_id": "toolu_bash2",
            "session_id": "sess6",
        }
        api_resp = _build_classification(
            "needs_user_approval",
            additional_context="Dangerous Bash command blocked: destructive command denied.",
        )
        stdout, code = _run_main(payload, api_response=api_resp)
        assert code == 0
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["retry"] is False


# ---------------------------------------------------------------------------
# Tests: API returns permanent_denial
# ---------------------------------------------------------------------------


class TestPermanentDenial:
    def test_no_retry_no_briefing(self):
        mod = _import_module()
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/classified/data"},
            "reason": "security policy forbids access",
            "tool_use_id": "toolu_perm1",
            "session_id": "sess7",
        }
        api_resp = _build_classification(
            "permanent_denial",
            additional_context="Permission denied with no known recovery path.",
        )
        posted_briefings = []
        fake_stdin = MagicMock()
        fake_stdin.buffer = _fake_stdin_buffer(payload)

        with (
            patch("aiteam.hooks.permission_denied_recovery.sys.stdin", fake_stdin),
            patch("aiteam.hooks.permission_denied_recovery.sys.stdout", io.StringIO()),
            patch("aiteam.hooks.permission_denied_recovery.sys.stderr", io.StringIO()),
            patch.object(mod, "_load_retry_state", return_value={}),
            patch.object(mod, "_save_retry_state"),
            patch.object(mod, "_post_event"),
            patch.object(
                mod,
                "_post_briefing_async",
                side_effect=lambda **kw: posted_briefings.append(kw),
            ),
            patch.object(mod, "_call_diagnose", return_value=api_resp),
            patch("aiteam.hooks.permission_denied_recovery.sys.exit", side_effect=SystemExit),
        ):
            try:
                mod.main()
            except SystemExit:
                pass

        assert len(posted_briefings) == 0  # no briefing for permanent denial

    def test_no_retry_output(self):
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/classified"},
            "reason": "access permanently denied",
            "tool_use_id": "toolu_perm2",
            "session_id": "sess8",
        }
        api_resp = _build_classification("permanent_denial")
        stdout, code = _run_main(payload, api_response=api_resp)
        assert code == 0
        if stdout.strip():
            result = json.loads(stdout)
            assert result["hookSpecificOutput"]["retry"] is False


# ---------------------------------------------------------------------------
# Tests: API unreachable — fallback to keyword matching
# ---------------------------------------------------------------------------


class TestApiFallback:
    def test_bash_fallback_no_retry(self):
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls /tmp"},
            "reason": "auto denied",
            "tool_use_id": "toolu_fallback1",
            "session_id": "sess9",
        }
        # api_response=None simulates unreachable API → triggers _fallback_classify
        stdout, code = _run_main(payload, api_response=None)
        assert code == 0
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["retry"] is False

    def test_transient_fallback_retries(self):
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/data"},
            "reason": "transient network error",
            "tool_use_id": "toolu_fallback2",
            "session_id": "sess10",
        }
        stdout, code = _run_main(payload, retry_state={}, api_response=None)
        assert code == 0
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["retry"] is True

    def test_path_outside_fallback_no_retry(self):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/etc/shadow"},
            "reason": "path outside the project directory",
            "tool_use_id": "toolu_fallback3",
            "session_id": "sess11",
        }
        stdout, code = _run_main(payload, api_response=None)
        assert code == 0
        result = json.loads(stdout)
        assert result["hookSpecificOutput"]["retry"] is False

    def test_api_unreachable_does_not_raise(self):
        import urllib.error

        mod = _import_module()
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls /tmp"},
            "reason": "auto denied",
            "tool_use_id": "toolu_fallback4",
            "session_id": "sess12",
        }

        def raise_url_error(*args, **kwargs):
            raise urllib.error.URLError("connection refused")

        fake_stdin = MagicMock()
        fake_stdin.buffer = _fake_stdin_buffer(payload)

        with (
            patch("aiteam.hooks.permission_denied_recovery.sys.stdin", fake_stdin),
            patch("aiteam.hooks.permission_denied_recovery.sys.stdout", io.StringIO()),
            patch("aiteam.hooks.permission_denied_recovery.sys.stderr", io.StringIO()),
            patch.object(mod, "_load_retry_state", return_value={}),
            patch.object(mod, "_save_retry_state"),
            patch("urllib.request.urlopen", side_effect=raise_url_error),
            patch("aiteam.hooks.permission_denied_recovery.sys.exit", side_effect=SystemExit),
        ):
            try:
                mod.main()
            except SystemExit:
                pass
            except Exception as e:
                raise AssertionError(f"Hook raised unexpectedly: {e}") from e


# ---------------------------------------------------------------------------
# Tests: edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_stdin_exits_cleanly(self):
        mod = _import_module()
        empty_buf = MagicMock()
        empty_buf.read.return_value = b""
        fake_stdin = MagicMock()
        fake_stdin.buffer = empty_buf

        with (
            patch("aiteam.hooks.permission_denied_recovery.sys.stdin", fake_stdin),
            patch("aiteam.hooks.permission_denied_recovery.sys.stdout", io.StringIO()),
            patch("aiteam.hooks.permission_denied_recovery.sys.stderr", io.StringIO()),
            patch("aiteam.hooks.permission_denied_recovery.sys.exit", side_effect=SystemExit),
        ):
            try:
                mod.main()
            except SystemExit:
                pass
            except Exception as e:
                raise AssertionError(f"Hook raised on empty stdin: {e}") from e

    def test_event_always_posted(self):
        mod = _import_module()
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/x"},
            "reason": "some denial",
            "tool_use_id": "toolu_evt1",
            "session_id": "sess_evt",
        }
        posted_events = []
        fake_stdin = MagicMock()
        fake_stdin.buffer = _fake_stdin_buffer(payload)
        api_resp = _build_classification("permanent_denial")

        with (
            patch("aiteam.hooks.permission_denied_recovery.sys.stdin", fake_stdin),
            patch("aiteam.hooks.permission_denied_recovery.sys.stdout", io.StringIO()),
            patch("aiteam.hooks.permission_denied_recovery.sys.stderr", io.StringIO()),
            patch.object(mod, "_load_retry_state", return_value={}),
            patch.object(mod, "_save_retry_state"),
            patch.object(mod, "_post_event", side_effect=lambda e: posted_events.append(e)),
            patch.object(mod, "_post_briefing_async"),
            patch.object(mod, "_call_diagnose", return_value=api_resp),
            patch("aiteam.hooks.permission_denied_recovery.sys.exit", side_effect=SystemExit),
        ):
            try:
                mod.main()
            except SystemExit:
                pass

        assert len(posted_events) == 1
        assert posted_events[0]["hook_event_name"] == "PermissionDenied"
        assert posted_events[0]["tool_name"] == "Read"
