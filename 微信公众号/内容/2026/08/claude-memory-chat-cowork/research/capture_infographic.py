from pathlib import Path

from playwright.sync_api import sync_playwright


PACKAGE = Path(__file__).resolve().parents[1]
SOURCE = PACKAGE / "research" / "render-memory-map.html"
OUTPUT = PACKAGE / "assets" / "three-ai-memory-map.png"


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1080, "height": 1980},
        device_scale_factor=1,
        locale="zh-CN",
        color_scheme="light",
    )
    page = context.new_page()
    page.goto(SOURCE.as_uri(), wait_until="load")
    page.screenshot(path=str(OUTPUT), full_page=False)
    context.close()
    browser.close()
