"""Smoke runner: generate a real weekly summary from the live 188-repo DB.

Usage:
    python tools_run_weekly_summary.py [--summary weekly|by_tag|top_n|health]
                                       [--tag NAME] [--n N] [--sort KEY]

Reads from ~/.claude/data/ai-team-os/aiteam.db (live archive) and prints
the markdown to stdout. No DB writes, no report_save.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows so markdown emojis don't trip cp936/GBK.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

from aiteam.services.ecosystem_summarizer import EcosystemSummarizer
from aiteam.storage.connection import close_db
from aiteam.storage.repository import StorageRepository


async def _run(args: argparse.Namespace) -> None:
    db_path = Path.home() / ".claude" / "data" / "ai-team-os" / "aiteam.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"
    repo = StorageRepository(db_url=db_url)
    summarizer = EcosystemSummarizer(repo)

    try:
        if args.summary == "weekly":
            md = await summarizer.weekly_summary(window_days=args.window)
        elif args.summary == "by_tag":
            md = await summarizer.by_tag_summary(
                args.tag, include_archived=args.include_archived
            )
        elif args.summary == "top_n":
            md = await summarizer.top_n_summary(
                category=args.category, n=args.n, sort=args.sort
            )
        else:
            md = await summarizer.health_summary()
    finally:
        await close_db()

    print(md)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        choices=("weekly", "by_tag", "top_n", "health"),
        default="weekly",
    )
    parser.add_argument("--tag", default="")
    parser.add_argument("--include-archived", action="store_true")
    parser.add_argument("--category", default="")
    parser.add_argument("--n", type=int, default=10)
    parser.add_argument("--sort", default="stars")
    parser.add_argument("--window", type=int, default=7)
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(_run(_parse_args()))
