from pathlib import Path

from playwright.sync_api import Page, sync_playwright


PACKAGE = Path(__file__).resolve().parents[1]
ASSETS = PACKAGE / "assets"


def dismiss_overlays(page: Page) -> None:
    selectors = [
        "button[aria-label='Dismiss']",
        "button[aria-label='Close']",
        "button.modal__dismiss",
        "button:has-text('×')",
    ]
    for selector in selectors:
        button = page.locator(selector).first
        if button.count() and button.is_visible():
            try:
                button.click(timeout=3000, force=True)
                page.wait_for_timeout(500)
            except Exception:
                pass
    page.add_style_tag(
        content="""
        .modal__overlay, .top-level-modal-container, .cta-modal,
        .contextual-sign-in-modal, .authwall-join-form, .top-nav,
        nav.top-nav {
          display: none !important;
        }
        body { overflow: auto !important; }
        """
    )


def open_public_post(page: Page, url: str) -> None:
    response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(4500)
    dismiss_overlays(page)
    print("public_post", response.status if response else "no-status", page.title())


def capture_discussion(
    page: Page,
    text_snippet: str,
    output_name: str,
    expected_reaction_text: str,
    excerpt_lines: int,
) -> None:
    needle = page.get_by_text(text_snippet, exact=False).first
    needle.wait_for(state="visible", timeout=20000)
    needle.evaluate(
        "(el, lines) => { el.style.display = '-webkit-box'; "
        "el.style.webkitBoxOrient = 'vertical'; "
        "el.style.webkitLineClamp = String(lines); "
        "el.style.overflow = 'hidden'; "
        "el.style.maxWidth = 'calc(100% - 22px)'; }",
        excerpt_lines,
    )
    comment_card = needle.locator(
        "xpath=ancestor::section[contains(@class, 'comment')][1]"
    )
    comment_card.wait_for(state="visible", timeout=5000)
    comment_card.evaluate(
        "el => { el.style.transform = 'translateX(38px)'; "
        "el.style.width = 'calc(100% - 76px)'; }"
    )
    comment_card.scroll_into_view_if_needed()
    page.wait_for_timeout(800)
    comment_card.screenshot(path=str(ASSETS / output_name))

    reaction = page.get_by_text(expected_reaction_text, exact=False)
    print(output_name, "reaction_label_found", reaction.count() > 0)


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 650, "height": 850},
        device_scale_factor=2,
        locale="en-US",
        color_scheme="light",
    )
    page = context.new_page()

    open_public_post(
        page,
        "https://www.linkedin.com/posts/claude_"
        "memory-on-claude-managed-agents-is-now-in-"
        "activity-7453187579774009345-rAbh",
    )
    capture_discussion(
        page,
        "This is good - but the memory or just",
        "community-linkedin-chat-cowork-handoff-101-reactions.png",
        "101 Reactions",
        2,
    )
    capture_discussion(
        page,
        "Memory is essential for the next stage of AI",
        "community-linkedin-memory-drift-7-reactions.png",
        "7 Reactions",
        2,
    )
    open_public_post(
        page,
        "https://www.linkedin.com/posts/ruben-hassid_"
        "how-to-import-your-entire-chatgpt-to-claude-"
        "activity-7438464104786190336-HFtU",
    )
    capture_discussion(
        page,
        "the surprising part was how patterns in your questions start showing up",
        "community-linkedin-history-as-mirror-10-reactions.png",
        "10 Reactions",
        3,
    )

    context.close()
    browser.close()
