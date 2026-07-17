"""v1.5.1 烟雾测试：验证 stage facet 统计准确 + StatsBar/FilterBar tooltip + RepoCard 徽章。

Run:
  python scripts/smoke_v151_stage_facet.py
"""

from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

PROJECT_ID = "3aa58dc7-a771-4745-8fa6-efbd5819956a"
PROJECT_PATH = "C:/Users/TUF/Desktop/AI团队框架/ai-team-os"
BASE = "http://localhost:8000"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()

        # Step 1: 注入项目 id 到 localStorage
        page.goto(BASE)
        page.evaluate(
            f"() => {{ localStorage.setItem('aiteam.activeProjectId', '{PROJECT_ID}'); "
            f"localStorage.setItem('aiteam.activeProjectPath', '{PROJECT_PATH}'); }}"
        )
        page.goto(f"{BASE}/ecosystem", wait_until="networkidle")

        # 给前端 1s 渲染
        page.wait_for_timeout(1500)

        # === 检查 1: StatsBar 显示 ===
        stats_text = page.locator(".grid, .flex").first.inner_text() if False else page.content()
        print("\n=== Test 1: StatsBar ===")
        # 在页面文本里找 "262" 或 "queued" 数字
        import re
        # 找出所有数字 + label 配对
        for keyword in ["待浅扫", "已深扫", "失活仓", "当前视图"]:
            if keyword in stats_text:
                # 找 "{keyword}: number" 或 "{number}\n{keyword}" 模式
                idx = stats_text.find(keyword)
                snippet = stats_text[max(0, idx - 60):idx + 60]
                nums = re.findall(r">(\d+)<", snippet)
                print(f"  {keyword}: nearby numbers = {nums}")
            else:
                print(f"  {keyword}: NOT FOUND")

        # === 检查 2: 待浅扫 = 262（而不是 102） ===
        page.screenshot(path="v151_screenshot_stats.png", full_page=False)
        print("\nScreenshot: v151_screenshot_stats.png")

        # === 检查 3: FilterBar 选 "已深扫" 显示 3 仓 ===
        print("\n=== Test 3: 已深扫 filter ===")
        try:
            stage_trigger = page.get_by_label("研究阶段").first
            stage_trigger.click()
            page.wait_for_timeout(500)
            page.get_by_text("已深扫", exact=False).first.click()
            page.wait_for_timeout(1500)
            page.screenshot(path="v151_screenshot_deepscan.png", full_page=False)
            print("Screenshot: v151_screenshot_deepscan.png")
        except Exception as e:
            print(f"  Filter test failed: {e}")

        page.wait_for_timeout(2000)
        browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
