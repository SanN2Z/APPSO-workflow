from pathlib import Path

from playwright.sync_api import sync_playwright


PACKAGE = Path(__file__).resolve().parents[1]
OUTPUT = (
    PACKAGE
    / "research"
    / "source-assets"
    / "hn-comment-fame-promise-49409832-screenshot.png"
)
URL = "https://news.ycombinator.com/item?id=49409073"
COMMENT_ID = "49409832"


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 390, "height": 720},
        device_scale_factor=2,
        locale="en-US",
        color_scheme="light",
    )
    page = context.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    comment = page.locator(f"tr.comtr[id='{COMMENT_ID}']")
    comment.wait_for(state="visible", timeout=15000)
    comment.screenshot(path=str(OUTPUT))

    context.close()
    browser.close()
