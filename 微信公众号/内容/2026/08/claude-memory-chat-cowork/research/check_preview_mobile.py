from pathlib import Path

from playwright.sync_api import sync_playwright


PACKAGE = Path(__file__).resolve().parents[1]
PREVIEW = PACKAGE / "dist" / "wechat-preview.html"
OUTPUT_DIR = PACKAGE / "dist"

TARGETS = {
    "community-handoff": "网友希望 Chat 与 Cowork 直接接力",
    "community-drift": "记忆层更需要留意写进了什么",
    "community-mirror": "聊天历史也可能成为思考方式的镜子",
    "memory-map": "Claude、ChatGPT 与 Gemini 的记忆地图",
    "cache-doodle": "平台记忆是缓存，用户文件才是真源",
}


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 430, "height": 900},
        device_scale_factor=1,
        locale="zh-CN",
        color_scheme="light",
    )
    page.goto(PREVIEW.as_uri() + "?width=375", wait_until="load")
    page.wait_for_timeout(500)

    phone_width = page.locator("#phone-preview").evaluate(
        "el => Math.round(el.getBoundingClientRect().width)"
    )
    print("phone_width", phone_width)

    for key, alt in TARGETS.items():
        image = page.locator(f'img[alt="{alt}"]')
        image.wait_for(state="visible", timeout=5000)
        metrics = image.evaluate(
            "el => ({naturalWidth: el.naturalWidth, naturalHeight: el.naturalHeight, "
            "renderedWidth: Math.round(el.getBoundingClientRect().width), "
            "renderedHeight: Math.round(el.getBoundingClientRect().height)})"
        )
        image.screenshot(path=str(OUTPUT_DIR / f"mobile-check-{key}.png"))
        print(key, metrics)

    browser.close()
