from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import json, hashlib

root=Path(__file__).resolve().parents[1]
url='https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/'
path=root/'assets/external/agi-media-headline.png'
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1100,'height':800},device_scale_factor=1.5)
    page.goto(url,wait_until='domcontentloaded',timeout=30000)
    h=page.locator('h1').first
    h.wait_for(state='visible',timeout=15000)
    title=h.inner_text()
    assert 'AGI' in title and 'Astra' in title,title
    h.screenshot(path=str(path))
    browser.close()
record=dict(source_url=url,title=title,file=path.relative_to(root).as_posix(),accessed_at=datetime.now(timezone.utc).isoformat(),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),modifications='Native article h1 screenshot only; no text changes or reconstruction')
(root/'research/agi-headline-receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
