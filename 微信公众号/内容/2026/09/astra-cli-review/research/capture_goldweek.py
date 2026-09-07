"""Screenshot genuine public pages using a fresh browser; never reconstruct posts."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ('astra-full-reset-embed', 'https://platform.twitter.com/embed/Tweet.html?id=2096035437299237298&lang=en'),
    ('astra-plus-business-live-embed', 'https://platform.twitter.com/embed/Tweet.html?id=2096002992046796932&lang=en'),
    ('reset-tracker', 'https://when.usagereset.at/'),
    ('claude-reset-embed', 'https://platform.twitter.com/embed/Tweet.html?id=2094856679250919746&lang=en'),
    ('astra-reset-embed', 'https://platform.twitter.com/embed/Tweet.html?id=2095651088502591861&lang=en'),
    ('astra-launch-embed', 'https://platform.twitter.com/embed/Tweet.html?id=2095595741528125780&lang=en'),
]

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    for name, url in TARGETS:
        if len(sys.argv) > 1 and name != sys.argv[1]:
            continue
        page = browser.new_page(viewport={'width': 1120, 'height': 900}, device_scale_factor=1.5, timezone_id='Asia/Shanghai', locale='en-US')
        if name == 'reset-tracker':
            page.set_viewport_size({'width': 1920, 'height': 800})
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=25000)
            page.wait_for_timeout(2500)
            body = page.locator('body').inner_text()
            print(json.dumps({'name':name,'url':page.url,'text':body[:1800]}))
            if len(body.strip()) > 50 and 'Access Denied' not in body:
                element = page.locator('article')
                target = ROOT/'assets'/f'{name}.png'
                if name == 'reset-tracker':
                    page.screenshot(path=str(target), clip={'x': 360, 'y': 0, 'width': 1200, 'height': 430})
                elif element.count() == 1:
                    element.screenshot(path=str(target))
                else:
                    page.screenshot(path=str(target), full_page=True)
        except Exception as exc:
            print(name, type(exc).__name__, str(exc)[:180])
        page.close()
    browser.close()
