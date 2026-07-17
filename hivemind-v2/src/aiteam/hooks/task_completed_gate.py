#!/usr/bin/env python3
"""CC TaskCompleted hook gate — blocks completion if task has no memo or no result.

Fires when CC's TaskUpdate(status=completed) is used. Checks the OS task wall
to ensure the task has recorded progress (memo) and a result before allowing
completion. Silently passes when API is unreachable.
Uses stdlib only (no aiteam package dependency).
"""

import json
import os
import sys
import urllib.request

_PORT_FILE = os.path.join(os.path.expanduser("~"), ".claude", "data", "ai-team-os", "api_port.txt")
_API_TIMEOUT = 2


def _get_api_url() -> str:
    env_url = os.environ.get("AITEAM_API_URL")
    if env_url:
        return env_url
    try:
        port = int(open(_PORT_FILE).read().strip())
        return f"http://localhost:{port}"
    except (FileNotFoundError, ValueError):
        return "http://localhost:8000"


def _fetch_task(task_id: str) -> dict:
    api_url = _get_api_url()
    url = f"{api_url}/api/tasks/{task_id}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _check_task(task_id: str, task_subject: str) -> None:
    """Check task memo and result. Exits with code 2 if validation fails."""
    resp = _fetch_task(task_id)

    task_data = resp.get("data") or resp
    if isinstance(task_data, dict) and "data" in task_data:
        task_data = task_data["data"]

    result = task_data.get("result") or ""
    config = task_data.get("config") or {}
    memos = config.get("memo") or []

    has_result = bool(result and str(result).strip())
    has_memo = bool(memos)

    if has_result and has_memo:
        sys.exit(0)

    missing_parts = []
    if not has_memo:
        missing_parts.append("memo空")
    if not has_result:
        missing_parts.append("无结果")

    reason = "/".join(missing_parts)
    sys.stderr.write(
        f"[OS BLOCK] 任务 {task_subject} 未记录进展（{reason}），禁止标记完成。"
        "请先 task_memo_add 或 task_update result=...\n"
    )
    sys.exit(2)


def main() -> None:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        # Invalid JSON — silent pass, don't block CC
        sys.exit(0)

    task_id = payload.get("task_id", "").strip()
    task_subject = payload.get("task_subject", "").strip() or task_id

    if not task_id:
        sys.exit(0)

    try:
        _check_task(task_id, task_subject)
    except SystemExit:
        raise
    except Exception:
        # API unreachable or any other error — silent pass
        sys.exit(0)


if __name__ == "__main__":
    main()
