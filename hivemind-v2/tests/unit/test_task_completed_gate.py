"""Unit tests for task_completed_gate hook."""

from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch


def _import_module():
    import importlib

    mod_name = "aiteam.hooks.task_completed_gate"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


def _make_mock_resp(body: dict):
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = json.dumps(body).encode()
    return mock_resp


class TestCheckTask:
    """Tests for _check_task logic."""

    def test_blocks_when_memo_empty_and_result_empty(self):
        """Both memo and result missing → exit(2)."""
        mod = _import_module()
        task_resp = {
            "data": {
                "result": "",
                "config": {"memo": []},
            }
        }
        with patch("urllib.request.urlopen", return_value=_make_mock_resp(task_resp)):
            try:
                mod._check_task("task-001", "My Task")
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 2

    def test_blocks_when_memo_missing_only(self):
        """Has result but no memos → exit(2)."""
        mod = _import_module()
        task_resp = {
            "data": {
                "result": "Done",
                "config": {"memo": []},
            }
        }
        with patch("urllib.request.urlopen", return_value=_make_mock_resp(task_resp)):
            try:
                mod._check_task("task-002", "My Task")
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 2

    def test_blocks_when_result_missing_only(self):
        """Has memos but no result → exit(2)."""
        mod = _import_module()
        task_resp = {
            "data": {
                "result": None,
                "config": {"memo": [{"content": "progress note"}]},
            }
        }
        with patch("urllib.request.urlopen", return_value=_make_mock_resp(task_resp)):
            try:
                mod._check_task("task-003", "My Task")
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 2

    def test_passes_when_both_memo_and_result_present(self):
        """Both memo and result present → exit(0)."""
        mod = _import_module()
        task_resp = {
            "data": {
                "result": "Implemented feature X",
                "config": {"memo": [{"content": "progress recorded"}]},
            }
        }
        with patch("urllib.request.urlopen", return_value=_make_mock_resp(task_resp)):
            try:
                mod._check_task("task-004", "My Task")
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 0

    def test_block_message_mentions_task_subject(self, capsys):
        """Block message includes the task subject name."""
        mod = _import_module()
        task_resp = {
            "data": {
                "result": "",
                "config": {"memo": []},
            }
        }
        with patch("urllib.request.urlopen", return_value=_make_mock_resp(task_resp)):
            try:
                mod._check_task("task-005", "Deploy Service")
            except SystemExit:
                pass
        captured = capsys.readouterr()
        assert "Deploy Service" in captured.err
        assert "[OS BLOCK]" in captured.err


class TestMain:
    """Tests for main() entry point."""

    def test_silent_pass_when_api_unreachable(self):
        """API connection error → exit(0) silently."""
        mod = _import_module()
        payload = json.dumps({
            "task_id": "task-001",
            "task_subject": "Build Auth",
        })
        with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.read.return_value = payload
                try:
                    mod.main()
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    assert e.code == 0

    def test_silent_pass_when_invalid_json(self):
        """Invalid JSON stdin → exit(0) silently."""
        mod = _import_module()
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = "not-valid-json{"
            try:
                mod.main()
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 0

    def test_silent_pass_when_no_task_id(self):
        """Missing task_id → exit(0) silently."""
        mod = _import_module()
        payload = json.dumps({"task_subject": "Some task"})
        with patch("urllib.request.urlopen") as mock_urlopen:
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.read.return_value = payload
                try:
                    mod.main()
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    assert e.code == 0
        mock_urlopen.assert_not_called()

    def test_blocks_when_task_has_no_memo_no_result(self):
        """Valid task_id, task missing memo+result → exit(2)."""
        mod = _import_module()
        payload = json.dumps({
            "task_id": "task-001",
            "task_subject": "Implement Feature",
        })
        task_resp = {
            "data": {
                "result": "",
                "config": {"memo": []},
            }
        }
        with patch("urllib.request.urlopen", return_value=_make_mock_resp(task_resp)):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.read.return_value = payload
                try:
                    mod.main()
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    assert e.code == 2

    def test_passes_when_task_has_memo_and_result(self):
        """Valid task with memo and result → exit(0)."""
        mod = _import_module()
        payload = json.dumps({
            "task_id": "task-002",
            "task_subject": "Fix Bug",
        })
        task_resp = {
            "data": {
                "result": "Bug fixed in auth middleware",
                "config": {"memo": [{"content": "identified root cause"}]},
            }
        }
        with patch("urllib.request.urlopen", return_value=_make_mock_resp(task_resp)):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.read.return_value = payload
                try:
                    mod.main()
                    assert False, "Expected SystemExit"
                except SystemExit as e:
                    assert e.code == 0

    def test_silent_pass_on_empty_stdin(self):
        """Empty stdin → exit(0) silently (no task_id)."""
        mod = _import_module()
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = ""
            try:
                mod.main()
                assert False, "Expected SystemExit"
            except SystemExit as e:
                assert e.code == 0
