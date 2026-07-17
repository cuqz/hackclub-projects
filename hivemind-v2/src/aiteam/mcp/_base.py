"""Shared infrastructure for AI Team OS MCP tools.

Contains the HTTP helper, project/team resolvers, and global state
that all tool modules depend on.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from aiteam.mcp._error_recovery import get_business_recovery, get_connection_recovery, get_http_recovery

logger = logging.getLogger(__name__)

_PORT_FILE = os.path.join(os.path.expanduser("~"), ".claude", "data", "ai-team-os", "api_port.txt")


def _get_api_port() -> int:
    """Read port from port file. Returns 8000 if file missing or invalid."""
    try:
        return int(open(_PORT_FILE).read().strip())
    except (FileNotFoundError, ValueError):
        return 8000


def _get_api_url() -> str:
    """Return the current API URL. AITEAM_API_URL env var takes highest priority."""
    env_url = os.environ.get("AITEAM_API_URL")
    if env_url:
        return env_url
    return f"http://localhost:{_get_api_port()}"


# Module-level alias for backwards compatibility (used in _autostart import guard)
API_URL = os.environ.get("AITEAM_API_URL", "http://localhost:8000")
# Project directory for DB isolation — set by Claude Code environment
PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", "")

# Process-level project ID — resolved once at startup from cwd → root_path match.
# Safe because each CC session spawns its own MCP server subprocess.
# Set by _init_session_project() after API is ready, before mcp.run().
_session_project_id: str = ""


# ============================================================
# HTTP helper
# ============================================================


def _api_call(
    method: str,
    path: str,
    data: dict[str, Any] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Unified API call helper using urllib standard library.

    Args:
        method: HTTP method (GET / POST / PUT / DELETE)
        path: API path, e.g., /api/teams
        data: Request body data (used for POST/PUT only)
        extra_headers: Additional headers to merge into the request
            (e.g. {"X-Project-Id": "..."} for ecosystem project scoping).

    Returns:
        API response as a JSON dict
    """
    url = f"{_get_api_url()}{urllib.parse.quote(path, safe='/?&=%')}"
    headers = {"Content-Type": "application/json"}
    if PROJECT_DIR:
        # HTTP headers must be ASCII/latin-1; percent-encode the path so
        # non-ASCII characters (e.g. Chinese directory names) are safe.
        # The API side decodes with urllib.parse.unquote before path matching.
        headers["X-Project-Dir"] = urllib.parse.quote(PROJECT_DIR, safe="/:.-_\\")
    # Stage J: auto-inject session-resolved X-Project-Id (read once at startup
    # via _init_session_project, no recursion risk). Subordinate to extra_headers
    # so callers can still override (e.g. cross-project tools force a different id).
    if _session_project_id:
        headers.setdefault("X-Project-Id", _session_project_id)
    if extra_headers:
        headers.update(extra_headers)

    body_bytes = None
    if data is not None:
        body_bytes = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
        except Exception:
            pass
        recovery_info = get_http_recovery(e.code)
        # Upgrade category from business keywords if body carries more context
        business_category = get_business_recovery(error_body)
        result: dict[str, Any] = {
            "success": False,
            "error": f"HTTP {e.code}: {e.reason}",
            "detail": error_body,
            "_error_category": business_category or recovery_info.get("category", "unknown"),
            "_recovery": recovery_info.get("recovery", ""),
        }
        return result
    except urllib.error.URLError as e:
        reason_str = str(e.reason)
        recovery_info = get_connection_recovery(reason_str)
        return {
            "success": False,
            "error": f"无法连接到 AI Team OS API ({_get_api_url()}): {e.reason}",
            "hint": "请确保 FastAPI 服务已启动: aiteam serve",
            "_error_category": recovery_info.get("category", "api_unavailable"),
            "_recovery": recovery_info.get("recovery", ""),
        }
    except Exception as e:
        recovery_info = get_connection_recovery(str(e))
        return {
            "success": False,
            "error": f"请求失败: {e!s}",
            "_error_category": recovery_info.get("category", "unknown"),
            "_recovery": recovery_info.get("recovery", ""),
        }


# ============================================================
# Resolvers
# ============================================================


def _resolve_team_id(team_id: str) -> str:
    """If team_id is empty, automatically get the active team ID from context_resolve.

    NOTE: This calls _api_call to get context. The context_resolve MCP tool
    in tools/infra.py has the full implementation; this resolver uses a
    lightweight version to avoid circular imports.
    """
    if team_id:
        return team_id
    # Lightweight context resolution — just find the first active team
    try:
        teams_data = _api_call("GET", "/api/teams")
        active_teams = [t for t in teams_data.get("data", []) if t.get("status") == "active"]
        if active_teams:
            return active_teams[0]["id"]
    except Exception:
        pass
    return ""


def _resolve_project_id(project_id: str) -> str:
    """Resolve project_id: explicit param > session constant > empty.

    _session_project_id is set once at startup from cwd matching.
    No dynamic resolution = no recursion risk.
    """
    if project_id:
        return project_id
    return _session_project_id


# ============================================================
# Session init
# ============================================================


def _init_session_project() -> None:
    """Resolve project_id once from cwd at startup. No recursion possible."""
    global _session_project_id
    try:
        projects = _api_call("GET", "/api/projects")
        cwd = os.getcwd().replace("\\", "/").rstrip("/").lower()
        # Longest-prefix match — multiple projects can match via prefix
        # (e.g. C:/Users/TUF and C:/Users/TUF/Desktop/AI...); pick the most specific.
        best_p = None
        best_len = -1
        for p in projects.get("data", []):
            rp = (p.get("root_path") or "").replace("\\", "/").rstrip("/").lower()
            if rp and (cwd == rp or cwd.startswith(rp + "/")) and len(rp) > best_len:
                best_p = p
                best_len = len(rp)
        if best_p is not None:
            _session_project_id = best_p["id"]
            logger.info("Session project: %s (%s)", best_p.get("name"), best_p["id"][:8])
            return
        logger.info("No project match for cwd=%s", cwd)
    except Exception as e:
        logger.warning("Failed to resolve session project: %s", e)
