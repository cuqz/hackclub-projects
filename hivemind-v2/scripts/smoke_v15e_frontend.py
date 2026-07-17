"""v1.5.0-E frontend smoke screenshots.

Captures the four key screens introduced in v1.5.0-E so the user can review:
  1. Ecosystem list page (stage badges + active/all/deleted tabs)
  2. Ecosystem research page (candidate filtering)
  3. Ecosystem detail page (research timeline tab)
  4. Project detail page (Ecosystem settings tab)

Usage:
  python scripts/smoke_v15e_frontend.py --base http://localhost:5177
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

OUT_DIR = Path(__file__).resolve().parents[1] / "test-screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# AI Team OS project id (where ecosystem data lives)
DEFAULT_PROJECT_ID = "3aa58dc7-a771-4745-8fa6-efbd5819956a"


def _set_project(page: Page, project_id: str) -> None:
    """Inject project id into localStorage so ProjectContext picks it up."""
    page.evaluate(
        "(id) => { localStorage.setItem('ai-team-os.activeProjectId', id); "
        "localStorage.setItem('ai-team-os.activeProjectName', 'AI Team OS'); }",
        project_id,
    )


def shot(page: Page, name: str, full: bool = False) -> None:
    path = OUT_DIR / name
    page.screenshot(path=str(path), full_page=full)
    print(f"  -> {path}")


def run(base: str, project_id: str) -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        page.on("pageerror", lambda exc: print(f"[pageerror] {exc}", file=sys.stderr))
        console_errors: list[str] = []
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error"
            else None,
        )

        # Open root once to install localStorage on the right origin
        page.goto(base, wait_until="domcontentloaded")
        _set_project(page, project_id)

        print("[1/4] /ecosystem (list page with tabs + stage badges)")
        page.goto(f"{base}/ecosystem", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        shot(page, "v15e-01-ecosystem-list.png")  # viewport-only to see header tabs clearly
        # 也保存完整页面以便看所有卡片
        shot(page, "v15e-01b-ecosystem-list-full.png", full=True)

        print("[2/4] /ecosystem/research (candidate filter)")
        page.goto(f"{base}/ecosystem/research", wait_until="domcontentloaded")
        page.wait_for_timeout(1200)
        # Type a research goal + add a tag
        page.fill("#research-goal", "升级记忆系统：对比生态主流方案")
        tag_input = page.locator("#tag-input")
        tag_input.fill("memory")
        tag_input.press("Enter")
        tag_input.fill("agent")
        tag_input.press("Enter")
        page.wait_for_timeout(2000)
        shot(page, "v15e-02-research-page.png")

        print("[3/4] /ecosystem/:repoId (detail with research timeline tab)")
        # Pull a repo id from API directly
        first_repo_id = page.evaluate(
            """
            async (pid) => {
              const r = await fetch('/api/ecosystem/profiles?limit=1', { headers: { 'X-Project-Id': pid }});
              const d = await r.json();
              return d.profiles?.[0]?.id ?? null;
            }
            """,
            project_id,
        )
        if not first_repo_id:
            print("  -> no repo id available, skipping detail screenshot")
        else:
            page.goto(f"{base}/ecosystem/{first_repo_id}", wait_until="domcontentloaded")
            page.wait_for_timeout(2200)
            # Click 研究历程 tab
            try:
                page.get_by_role("tab", name="研究历程").click(timeout=3000)
                page.wait_for_timeout(800)
            except Exception as e:
                print(f"  warn: could not click 研究历程 tab ({e})")
            shot(page, "v15e-03-detail-research-timeline.png")

        print("[4/4] /projects/:projectId (Ecosystem settings tab)")
        page.goto(f"{base}/projects/{project_id}", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        try:
            page.get_by_role("tab", name="Ecosystem 设置").click(timeout=3000)
            page.wait_for_timeout(1500)
        except Exception as e:
            print(f"  warn: could not click Ecosystem 设置 tab ({e})")
        shot(page, "v15e-04-project-ecosystem-settings.png")

        if console_errors:
            print("\nConsole errors collected:")
            for line in console_errors[:20]:
                print(f"  - {line}")

        browser.close()
    print("\nDone.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:5177")
    parser.add_argument("--project", default=DEFAULT_PROJECT_ID)
    args = parser.parse_args()
    return run(args.base.rstrip("/"), args.project)


if __name__ == "__main__":
    sys.exit(main())
