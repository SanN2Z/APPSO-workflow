from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def click_first(page, selectors):
    for frame in page.frames:
        for selector in selectors:
            locator = frame.locator(selector)
            if locator.count() and locator.first.is_visible():
                locator.first.click(timeout=3000)
                page.wait_for_timeout(1000)
                return True
    return False


def capture(url, output_name, dismiss_selectors):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1050},
            locale="en-US",
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        click_first(page, dismiss_selectors)

        heading = page.locator("h1").first
        heading.wait_for(state="visible", timeout=15000)
        heading.evaluate(
            "el => window.scrollTo(0, Math.max(0, el.getBoundingClientRect().top + "
            "window.scrollY - 130))"
        )
        page.wait_for_timeout(1500)
        page.screenshot(path=str(ASSETS / output_name), full_page=False)
        context.close()
        browser.close()


capture(
    "https://www.theguardian.com/technology/2026/aug/15/"
    "uk-ireland-booksellers-suspect-ai-companies-bulk-orders-data-acquisition",
    "source-002-guardian-booksellers.png",
    [
        "button:has-text('No, thank you')",
        "button:has-text('Reject all')",
        "button:has-text('Continue without accepting')",
    ],
)

capture(
    "https://www.theatlantic.com/technology/2026/08/"
    "ai-companies-buying-used-books-for-data/688167/",
    "source-003-atlantic-used-books.png",
    [
        "button[aria-label='Close']",
        "button:has-text('×')",
    ],
)
