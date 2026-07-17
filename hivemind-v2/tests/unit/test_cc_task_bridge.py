"""Unit tests for cc_task_bridge hook."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch


def _import_module():
    import importlib
    import sys

    # Re-import fresh each time to avoid state bleed
    mod_name = "aiteam.hooks.cc_task_bridge"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


class TestResolveProjectId:
    """Tests for _resolve_project_id."""

    def test_uses_cache_when_fresh(self):
        mod = _import_module()
        state = {"cached_project_id": "proj-123", "cached_project_id_at": __import__("time").time()}
        with patch.object(mod, "_load_state", return_value=state):
            with patch.object(mod, "_save_state") as mock_save:
                result = mod._resolve_project_id("/some/cwd")
        assert result == "proj-123"
        mock_save.assert_not_called()

    def test_fetches_from_api_when_cache_expired(self):
        mod = _import_module()
        state = {"cached_project_id": "old-id", "cached_project_id_at": 0}
        api_response = json.dumps({"project_id": "new-proj"}).encode()

        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = api_response

        with patch.object(mod, "_load_state", return_value=state):
            with patch.object(mod, "_save_state") as mock_save:
                with patch("urllib.request.urlopen", return_value=mock_resp):
                    result = mod._resolve_project_id("/some/cwd")

        assert result == "new-proj"
        mock_save.assert_called_once()

    def test_returns_none_when_api_unreachable(self):
        mod = _import_module()
        state = {}
        with patch.object(mod, "_load_state", return_value=state):
            with patch.object(mod, "_save_state"):
                with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
                    result = mod._resolve_project_id("/some/cwd")
        assert result is None


class TestCreateTask:
    """Tests for _create_task."""

    def test_calls_correct_endpoint(self):
        mod = _import_module()
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b'{"success": true}'

        captured_req = {}

        def fake_urlopen(req, timeout=None):
            captured_req["url"] = req.full_url
            captured_req["data"] = json.loads(req.data.decode())
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            mod._create_task("proj-abc", "Build auth API", "Add login endpoints", "backend-dev")

        assert "/api/projects/proj-abc/tasks" in captured_req["url"]
        body = captured_req["data"]
        assert body["title"] == "Build auth API"
        assert body["description"] == "Add login endpoints"
        assert body["assigned_to"] == "backend-dev"
        assert "cc-task" in body["tags"]
        assert body["priority"] == "medium"
        assert body["horizon"] == "short"

    def test_omits_assigned_to_when_owner_none(self):
        mod = _import_module()
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b"{}"

        captured_data = {}

        def fake_urlopen(req, timeout=None):
            captured_data.update(json.loads(req.data.decode()))
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            mod._create_task("proj-abc", "Some task", "", None)

        assert "assigned_to" not in captured_data


class TestMain:
    """Tests for main() entry point."""

    def test_parses_task_created_payload_and_calls_api(self):
        mod = _import_module()
        payload = json.dumps({
            "hook_event_name": "TaskCreated",
            "task_id": "task-001",
            "task_subject": "Implement user auth",
            "task_description": "Add login and signup endpoints",
            "teammate_name": "backend",
            "team_name": "my-team",
            "cwd": "/some/project",
            "session_id": "sess-123",
        })

        with patch.object(mod, "_resolve_project_id", return_value="proj-xyz") as mock_resolve:
            with patch.object(mod, "_create_task") as mock_create:
                with patch("sys.stdin") as mock_stdin:
                    mock_stdin.read.return_value = payload
                    mod.main()

        mock_resolve.assert_called_once_with("/some/project")
        mock_create.assert_called_once_with(
            "proj-xyz",
            "Implement user auth",
            "Add login and signup endpoints",
            "backend",
        )

    def test_silent_when_no_title(self):
        mod = _import_module()
        payload = json.dumps({"hook_event_name": "TaskCreated", "task_subject": "", "cwd": "/x"})

        with patch.object(mod, "_resolve_project_id") as mock_resolve:
            with patch.object(mod, "_create_task") as mock_create:
                with patch("sys.stdin") as mock_stdin:
                    mock_stdin.read.return_value = payload
                    mod.main()

        mock_resolve.assert_not_called()
        mock_create.assert_not_called()

    def test_silent_when_project_not_found(self):
        mod = _import_module()
        payload = json.dumps({
            "task_subject": "Some task",
            "cwd": "/unknown/project",
        })

        with patch.object(mod, "_resolve_project_id", return_value=None):
            with patch.object(mod, "_create_task") as mock_create:
                with patch("sys.stdin") as mock_stdin:
                    mock_stdin.read.return_value = payload
                    mod.main()

        mock_create.assert_not_called()

    def test_does_not_raise_when_create_fails(self):
        mod = _import_module()
        payload = json.dumps({
            "task_subject": "Some task",
            "task_description": "desc",
            "cwd": "/some/project",
        })

        with patch.object(mod, "_resolve_project_id", return_value="proj-xyz"):
            with patch.object(mod, "_create_task", side_effect=Exception("API down")):
                with patch("sys.stdin") as mock_stdin:
                    mock_stdin.read.return_value = payload
                    mod.main()  # Must not raise

    def test_silent_when_invalid_json_payload(self):
        mod = _import_module()
        with patch.object(mod, "_resolve_project_id") as mock_resolve:
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.read.return_value = "not-valid-json{"
                mod.main()  # Must not raise
        mock_resolve.assert_not_called()
