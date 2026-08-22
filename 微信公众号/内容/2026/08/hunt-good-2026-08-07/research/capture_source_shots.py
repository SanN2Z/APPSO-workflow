#!/usr/bin/env python3
"""Capture primary-source screenshots for the Hunt Good 2026-08-07 package.

Every shot is a real page rendered in Chromium. Nothing here is synthesised:
if a target fails, it fails loudly and is recorded as missing so the editor
never mistakes an absent screenshot for a captured one.

Output: research/source-assets/v2/<name>.png
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "source-assets" / "v2"
OUT.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
)

X_POSTS = [
    ("x-anthropic-incidents", "https://x.com/AnthropicAI/status/2082965101083320543"),
    ("x-openai-price", "https://x.com/OpenAI/status/2082878168764207230"),
    ("x-openaidevs-fastmode", "https://x.com/OpenAIDevs/status/2082878473409085654"),
    ("x-qwen-38max", "https://x.com/Alibaba_Qwen/status/2084100707423289643"),
    ("x-liquidai-lfm25", "https://x.com/liquidai/status/2084640701669613906"),
    ("x-transluce-awareness", "https://x.com/TransluceAI/status/2085455114924638320"),
    ("x-naomi-conduit", "https://x.com/NaomiBashkansky/status/2085043839589617918"),
    ("x-edgecity-village", "https://x.com/JoinEdgeCity/status/2083246167073407316"),
]

# name, url, selector (None = viewport shot), scroll-to-text (optional)
PAGE_SHOTS = [
    ("anthropic-report-hero", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals", None, None),
    ("anthropic-report-incident2", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals", None, "PyPI"),
    ("anthropic-report-incident1", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals", None, "several hundred rows"),
    ("anthropic-report-incident3", "https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals", None, "9,000"),
    ("openai-hf-incident", "https://openai.com/index/hugging-face-model-evaluation-security-incident/", None, None),
    ("hf-incident-disclosure", "https://huggingface.co/blog/security-incident-july-2026", None, None),
    ("aisi-kimi-k3", "https://www.aisi.gov.uk/blog/preliminary-assessment-of-kimi-k3s-cyber-capabilities", None, None),
    ("aisi-kimi-sandbox", "https://www.aisi.gov.uk/blog/preliminary-assessment-of-kimi-k3s-cyber-capabilities", None, "sandbox"),
    ("techcrunch-anthropic", "https://techcrunch.com/2026/07/30/anthropic-says-its-own-ai-models-breached-three-companies-during-security-tests/", None, None),
    ("linuxdo-22h-post", "https://linux.do/t/topic/2713360", None, None),
    ("linuxdo-22h-replies", "https://linux.do/t/topic/2713360", None, None),
    ("hf-deepseek-card", "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731", None, None),
    ("qwen-blog-hero", "https://qwen.ai/blog?id=qwen3.8", None, None),
    ("qwen-blog-ecommerce", "https://qwen.ai/blog?id=qwen3.8", None, "E-Commerce"),
    ("ohmycli-repo", "https://github.com/qwen-code-dev-bot/oh-my-cli", None, None),
    ("ohmycli-commits", "https://github.com/qwen-code-dev-bot/oh-my-cli/commits/main/", None, None),
    ("ohmycli-issues", "https://github.com/qwen-code-dev-bot/oh-my-cli/issues?q=is%3Aissue", None, None),
    ("transluce-hero", "https://transluce.org/user-awareness", None, None),
    ("transluce-amanda", "https://transluce.org/user-awareness", None, "Askell"),
    ("transluce-hoax", "https://transluce.org/user-awareness", None, "hoax"),
    ("arxiv-teammate-abs", "https://arxiv.org/abs/2607.27179", None, None),
    ("rescript-hn", "https://news.ycombinator.com/item?id=49065779", None, None),
    ("rescript-gh", "https://github.com/wassgha/rescript", None, None),
    ("lfm-hf-blog", "https://huggingface.co/blog/LiquidAI/lfm2-5-2-6b", None, None),
    ("lfm-hf-bench", "https://huggingface.co/blog/LiquidAI/lfm2-5-2-6b", None, "tok/s"),
    ("gstack-repo", "https://github.com/pattern-ai-labs/gstack-joins-meeting", None, None),
    ("gstack-roles", "https://github.com/pattern-ai-labs/gstack-joins-meeting", None, "office-hours"),
    ("cosmos-village", "https://blog.cosmos-institute.org/p/we-gave-a-village-personal-ai-agents", None, None),
    ("cosmos-village-numbers", "https://blog.cosmos-institute.org/p/we-gave-a-village-personal-ai-agents", None, "11,593"),
    ("cnbc-muse-code", "https://www.cnbc.com/2026/08/05/meta-debuts-muse-code-to-take-on-anthropic-and-openai-.html", None, None),
    ("anthropic-sonnet-pricing", "https://www.anthropic.com/claude/sonnet", None, "introductory"),
]

failures: list[str] = []


def scroll_to_text(page, needle: str) -> bool:
    """Scroll the first element containing `needle` into the middle of the viewport."""
    found = page.evaluate(
        """(needle) => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let node;
            while ((node = walker.nextNode())) {
                if (node.textContent && node.textContent.includes(needle)) {
                    const el = node.parentElement;
                    if (!el) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width === 0 && r.height === 0) continue;
                    el.scrollIntoView({block: 'center'});
                    return true;
                }
            }
            return false;
        }""",
        needle,
    )
    if found:
        page.wait_for_timeout(900)
    return bool(found)


def capture_x(ctx) -> None:
    page = ctx.new_page()
    for name, url in X_POSTS:
        target = OUT / f"{name}.png"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Logged-out X renders posts as bare <article> elements, not
            # article[data-testid="tweet"]; fall back across both shapes.
            page.wait_for_selector("article", timeout=30000)
            page.wait_for_timeout(3500)
            tweet = page.locator('article[data-testid="tweet"]')
            node = tweet.first if tweet.count() else page.locator("article").first
            node.screenshot(path=str(target))
            print(f"[ok] {name}")
        except (PlaywrightError, TimeoutError) as exc:
            failures.append(f"{name}: {type(exc).__name__}: {str(exc)[:100]}")
            print(f"[fail] {name}: {type(exc).__name__}")
    page.close()


def capture_pages(ctx) -> None:
    page = ctx.new_page()
    for name, url, selector, needle in PAGE_SHOTS:
        target = OUT / f"{name}.png"
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
            if needle and not scroll_to_text(page, needle):
                failures.append(f"{name}: text '{needle}' not found on page")
                print(f"[fail] {name}: needle '{needle}' not found")
                continue
            if selector:
                page.locator(selector).first.screenshot(path=str(target))
            else:
                page.screenshot(path=str(target))
            print(f"[ok] {name}")
        except (PlaywrightError, TimeoutError) as exc:
            failures.append(f"{name}: {type(exc).__name__}: {str(exc)[:100]}")
            print(f"[fail] {name}: {type(exc).__name__}")
    page.close()


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 1400},
            device_scale_factor=2,
            user_agent=UA,
            locale="en-US",
        )
        capture_x(ctx)
        capture_pages(ctx)
        browser.close()

    print(f"\n[summary] captured into {OUT}")
    if failures:
        print(f"[summary] {len(failures)} failed:")
        for line in failures:
            print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
