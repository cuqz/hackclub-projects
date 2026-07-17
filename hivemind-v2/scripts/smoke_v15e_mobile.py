"""v1.5.0-E mobile responsive screenshot — 375px viewport."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).resolve().parents[1] / "test-screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:5177"
PROJECT_ID = "3aa58dc7-a771-4745-8fa6-efbd5819956a"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 375, "height": 720})
        page = ctx.new_page()
        page.on("pageerror", lambda exc: print(f"[pageerror] {exc}", file=sys.stderr))

        page.goto(BASE, wait_until="domcontentloaded")
        page.evaluate(
            "(id) => localStorage.setItem('ai-team-os.activeProjectId', id)",
            PROJECT_ID,
        )

        page.goto(f"{BASE}/ecosystem", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        out = OUT_DIR / "v15e-05-mobile-list.png"
        page.screenshot(path=str(out), full_page=False)
        print(out)

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
