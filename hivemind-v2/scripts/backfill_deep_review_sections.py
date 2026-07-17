"""K5 backfill — populate 5-section fields on existing deep_review rows.

Walks all EcosystemDeepReview rows with non-empty ``report_id`` and empty
``summary_md`` (i.e. created before the K5 hook parser shipped). For each
target row we load the linked report content from the OS API, parse the
5-section markdown via the same parser used by the live hook, and update
the row.

Two modes:

  --via api      (default)  POST /api/ecosystem/deep_reviews/{id}/backfill.
                            Requires the OS API to be running with the K5
                            backfill endpoint loaded.
  --via sqlite              Update the SQLite row directly. Used when the
                            API is not available (e.g. during a hot
                            restart). Also moves any dispatch prompt that
                            was historically stored in demo_log_excerpt
                            into the new dispatch_prompt column.

Run with ``python scripts/backfill_deep_review_sections.py`` while the OS
API is up. Idempotent.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request

# Allow ``import aiteam.*`` from src/ when running via repo root.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

from aiteam.hooks.deep_review_link import _build_link_payload  # noqa: E402

DEFAULT_API = "http://127.0.0.1:8000"
DEFAULT_DB = os.path.expanduser(
    "~/.claude/data/ai-team-os/aiteam.db"
)


# ---------------------------------------------------------------------------
# API mode
# ---------------------------------------------------------------------------


def _http_json(
    method: str, url: str, project_id: str, body: dict | None = None
) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "X-Project-Id": project_id,
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _via_api(api: str, project_id: str, dry_run: bool) -> int:
    rows = _http_json(
        "GET", f"{api}/api/ecosystem/deep_reviews?limit=100", project_id
    )["reviews"]
    targets = [
        r
        for r in rows
        if r.get("report_id") and not (r.get("summary_md") or "").strip()
    ]
    print(
        f"[api mode] discovered {len(rows)} rows ({len(targets)} need backfill)"
    )
    if not targets:
        return 0

    failed = 0
    for row in targets:
        try:
            report = _http_json(
                "GET",
                f"{api}/api/reports/{row['report_id']}",
                project_id,
            )
        except urllib.error.HTTPError as exc:
            print(f"  - {row['id'][:8]}: report fetch failed {exc.code}")
            failed += 1
            continue

        content = report.get("content") or ""
        if not content.strip():
            print(f"  - {row['id'][:8]}: empty content, skip")
            failed += 1
            continue

        payload = _build_link_payload(row["report_id"], content)
        keys = sorted(payload.keys())
        print(
            f"  - {row['id'][:8]} repo={row['repo_id'][:8]}: keys={keys}"
        )
        if dry_run:
            continue

        try:
            url = f"{api}/api/ecosystem/deep_reviews/{row['id']}/backfill"
            updated = _http_json("POST", url, project_id, payload)
        except urllib.error.HTTPError as exc:
            print(f"    ! HTTPError {exc.code}: {exc.reason}")
            failed += 1
            continue

        summary = (updated.get("summary_md") or "").strip()
        print(
            f"    ok summary_len={len(summary)} "
            f"demo_result={updated.get('demo_result')} "
            f"recommendation={updated.get('integration_recommendation')}"
        )
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# SQLite mode (used when the API isn't running yet)
# ---------------------------------------------------------------------------

_DISPATCH_PROMPT_MARKER = (
    "You are running as a deep-review sub-agent for the ecosystem-platform team."
)


def _via_sqlite(db_path: str, project_id: str, dry_run: bool) -> int:
    if not os.path.exists(db_path):
        print(f"DB not found: {db_path}")
        return 1
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    rows = list(
        con.execute(
            """
            SELECT d.id, d.repo_id, d.report_id, d.summary_md,
                   d.demo_log_excerpt, d.dispatch_prompt
            FROM ecosystem_deep_reviews d
            WHERE d.report_id IS NOT NULL AND d.report_id != ''
            """
        )
    )
    targets = [r for r in rows if not (r["summary_md"] or "").strip()]
    print(
        f"[sqlite mode] db={db_path}\n"
        f"  discovered {len(rows)} linked rows ({len(targets)} need backfill)"
    )
    if not targets:
        return 0

    failed = 0
    for row in targets:
        report_row = con.execute(
            "SELECT content FROM reports WHERE id = ?", (row["report_id"],)
        ).fetchone()
        if report_row is None or not (report_row["content"] or "").strip():
            print(f"  - {row['id'][:8]}: report missing or empty content")
            failed += 1
            continue

        content = report_row["content"]
        payload = _build_link_payload(row["report_id"], content)

        # Move stale dispatch prompt out of demo_log_excerpt.
        new_dispatch = row["dispatch_prompt"] or ""
        new_demo_log = row["demo_log_excerpt"] or ""
        if (
            not new_dispatch
            and _DISPATCH_PROMPT_MARKER in new_demo_log
        ):
            new_dispatch = new_demo_log
            new_demo_log = ""
        if "demo_log_excerpt" in payload:
            new_demo_log = payload["demo_log_excerpt"]

        learnings_md = payload.get("learnings_md", "")
        if "integration_md" in payload:
            sep = "\n\n" if learnings_md else ""
            learnings_md = (
                f"{learnings_md}{sep}## 5. 集成建议\n"
                f"{payload['integration_md'].strip()}"
            )

        update_fields = {
            "summary_md": payload.get("summary_md", ""),
            "architecture_md": payload.get("architecture_md", ""),
            "risks_md": payload.get("risks_md", ""),
            "learnings_md": learnings_md,
            "demo_log_excerpt": new_demo_log,
            "demo_result": payload.get("demo_result"),
            "integration_recommendation": payload.get(
                "integration_recommendation"
            ),
            "dispatch_prompt": new_dispatch,
        }

        print(
            f"  - {row['id'][:8]} repo={row['repo_id'][:8]}: "
            f"summary_len={len(update_fields['summary_md'])} "
            f"demo={update_fields['demo_result']} "
            f"rec={update_fields['integration_recommendation']}"
        )
        if dry_run:
            continue

        cols = ", ".join(f"{k} = ?" for k in update_fields)
        con.execute(
            f"UPDATE ecosystem_deep_reviews SET {cols} WHERE id = ?",
            tuple(update_fields.values()) + (row["id"],),
        )
        con.commit()
    con.close()
    return 1 if failed else 0


# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--via",
        choices=["api", "sqlite"],
        default="api",
        help="Backfill transport (default: api)",
    )
    parser.add_argument(
        "--api",
        default=os.environ.get("AITEAM_API_URL", DEFAULT_API),
        help="Base URL for the OS API (default: %(default)s)",
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB,
        help="Path to the OS SQLite DB (default: %(default)s)",
    )
    parser.add_argument(
        "--project-id",
        default="3aa58dc7-a771-4745-8fa6-efbd5819956a",
        help="Project scope for the X-Project-Id header (api mode only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without persisting.",
    )
    args = parser.parse_args()

    if args.via == "api":
        return _via_api(args.api, args.project_id, args.dry_run)
    return _via_sqlite(args.db, args.project_id, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
