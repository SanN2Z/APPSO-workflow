from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
records=[]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    for name,url in [('every-astra-writing','https://every.to/vibe-check/gpt-6-astra-vibe-check'),
                     ('cognition-astra-engineering','https://devin.ai/blog/gpt-6-astra')]:
        page=browser.new_page(viewport={'width':1280,'height':1050},device_scale_factor=1)
        try:
            page.goto(url,wait_until='domcontentloaded',timeout=45000)
            page.wait_for_timeout(1800)
            heading=page.locator('h1').first
            heading.wait_for(timeout=12000)
            box=heading.bounding_box()
            page.evaluate('(y)=>window.scrollTo(0,y)',max(0,box['y']-80))
            page.wait_for_timeout(200)
            body=page.locator('body').inner_text()
            if 'GPT-6' not in body:
                raise ValueError('Expected title not present')
            path=root/'assets'/f'{name}.png'
            page.screenshot(path=str(path))
            records.append(dict(file='assets/'+path.name,source_url=url,accessed_at=datetime.now(timezone.utc).isoformat(),
                                sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),bytes=path.stat().st_size,
                                title=heading.inner_text(),visible_text=body[:5000]))
            print(name,'captured',flush=True)
        except Exception as e:
            records.append(dict(source_url=url,error_type=type(e).__name__))
            print(name,type(e).__name__,flush=True)
        page.close()
    browser.close()
(root/'research/external-followup-images.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
