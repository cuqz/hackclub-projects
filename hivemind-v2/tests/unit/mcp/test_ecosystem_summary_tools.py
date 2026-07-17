"""Tests for the 4 Stage G ecosystem-summary MCP tools (mocked _api_call).

The tools are thin wrappers over the summarizer REST endpoints. We mock
``_api_call`` to assert correct URL composition, query string params and
the auto report_save fan-out behaviour.
"""

from __future__ import annotations

from unittest.mock import patch

import aiteam.mcp.tools.ecosystem as eco


class _ToolCapture:
    """Capture @mcp.tool() registered functions."""

    def __init__(self) -> None:
        self.tools: dict = {}

    def tool(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        def decorator(fn):  # type: ignore[no-untyped-def]
            self.tools[fn.__name__] = fn
            return fn

        return decorator


_capture = _ToolCapture()
eco.register(_capture)

_summary_weekly = _capture.tools["ecosystem_summary_weekly"]
_summary_by_tag = _capture.tools["ecosystem_summary_by_tag"]
_summary_top_n = _capture.tools["ecosystem_summary_top_n"]
_summary_health = _capture.tools["ecosystem_summary_health"]


def _stub_api_factory(fake_summary: dict, fake_save: dict | None = None):
    """Return a side_effect that routes by URL prefix.

    GET /api/ecosystem/summary/* -> fake_summary
    POST /api/reports             -> fake_save
    """

    def _side_effect(method: str, path: str, payload: dict | None = None):
        if path.startswith("/api/ecosystem/summary"):
            return fake_summary
        if path == "/api/reports":
            return fake_save or {
                "id": "rep-1",
                "filename": "ecosystem.md",
                "report_type": payload.get("report_type") if payload else "",
                "project_id": "proj-1",
            }
        return None

    return _side_effect


# ============================================================
# ecosystem_summary_weekly
# ============================================================


class TestSummaryWeekly:
    def test_passes_window_days_and_top_movers_limit(self) -> None:
        fake = {"markdown": "# weekly", "window_days": 14, "generated_at": "x"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            result = _summary_weekly(window_days=14, top_movers_limit=3)

        first_call_path = mock_api.call_args_list[0][0][1]
        assert "/api/ecosystem/summary/weekly" in first_call_path
        assert "window_days=14" in first_call_path
        assert "top_movers_limit=3" in first_call_path
        assert result["markdown"] == "# weekly"
        # report saved
        assert result["report"]["success"] is True
        assert result["report"]["id"] == "rep-1"

    def test_save_report_false_skips_persistence(self) -> None:
        fake = {"markdown": "# weekly", "window_days": 7}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            result = _summary_weekly(save_report=False)

        # Only one API call (no /api/reports POST)
        called_paths = [c[0][1] for c in mock_api.call_args_list]
        assert any("/api/ecosystem/summary/weekly" in p for p in called_paths)
        assert all("/api/reports" not in p for p in called_paths)
        assert "report" not in result

    def test_api_failure_returns_error(self) -> None:
        with patch.object(eco, "_api_call", return_value=None):
            result = _summary_weekly()
        assert result["success"] is False

    def test_report_save_uses_correct_report_type(self) -> None:
        fake = {"markdown": "# w"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            _summary_weekly()
        # Find the /api/reports POST and check report_type
        reports_call = next(
            c for c in mock_api.call_args_list if c[0][1] == "/api/reports"
        )
        body = reports_call[0][2]
        assert body["report_type"] == "ecosystem-weekly"
        assert body["topic"].startswith("ecosystem-weekly-")
        assert body["author"] == "ecosystem-summarizer"


# ============================================================
# ecosystem_summary_by_tag
# ============================================================


class TestSummaryByTag:
    def test_includes_tag_param(self) -> None:
        fake = {"markdown": "# bytag", "tag": "memory_system"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            _summary_by_tag(tag="memory_system", include_archived=True, limit=50)

        path = mock_api.call_args_list[0][0][1]
        assert "/api/ecosystem/summary/by_tag" in path
        assert "tag=memory_system" in path
        assert "include_archived=True" in path
        assert "limit=50" in path

    def test_report_topic_includes_tag(self) -> None:
        fake = {"markdown": "# x", "tag": "skill_system"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            _summary_by_tag(tag="skill_system")
        reports_call = next(
            c for c in mock_api.call_args_list if c[0][1] == "/api/reports"
        )
        assert reports_call[0][2]["topic"] == "ecosystem-by-tag-skill_system"
        assert reports_call[0][2]["report_type"] == "ecosystem-by-tag"


# ============================================================
# ecosystem_summary_top_n
# ============================================================


class TestSummaryTopN:
    def test_default_omits_category(self) -> None:
        fake = {"markdown": "# top"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            _summary_top_n(n=5, sort="stars")
        path = mock_api.call_args_list[0][0][1]
        assert "n=5" in path
        assert "sort=stars" in path
        assert "category=" not in path

    def test_passes_category_filter(self) -> None:
        fake = {"markdown": "# top"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            _summary_top_n(category="agent-framework", n=20, sort="pushed_at")
        path = mock_api.call_args_list[0][0][1]
        assert "category=agent-framework" in path
        assert "sort=pushed_at" in path

    def test_report_topic_namespacing(self) -> None:
        fake = {"markdown": "# t"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            _summary_top_n(category="mcp-server", n=15, sort="scan_freshness")
        reports_call = next(
            c for c in mock_api.call_args_list if c[0][1] == "/api/reports"
        )
        body = reports_call[0][2]
        assert body["topic"] == "ecosystem-top-15-scan_freshness-mcp-server"
        assert body["report_type"] == "ecosystem-top-n"


# ============================================================
# ecosystem_summary_health
# ============================================================


class TestSummaryHealth:
    def test_calls_health_endpoint(self) -> None:
        fake = {"markdown": "# health"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            result = _summary_health()
        path = mock_api.call_args_list[0][0][1]
        assert path == "/api/ecosystem/summary/health"
        assert result["markdown"] == "# health"
        assert result["report"]["success"] is True

    def test_save_report_false_skips_persistence(self) -> None:
        fake = {"markdown": "# health"}
        with patch.object(eco, "_api_call", side_effect=_stub_api_factory(fake)) as mock_api:
            result = _summary_health(save_report=False)
        called_paths = [c[0][1] for c in mock_api.call_args_list]
        assert all("/api/reports" not in p for p in called_paths)
        assert "report" not in result

    def test_api_failure_returns_error(self) -> None:
        with patch.object(eco, "_api_call", return_value=None):
            result = _summary_health()
        assert result["success"] is False
