from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import json, hashlib

root=Path(__file__).resolve().parents[1]
tid='2096023238081908917'
source='https://x.com/PaulSolt/status/'+tid
data=json.load(urlopen(Request('https://cdn.syndication.twimg.com/tweet-result?id='+tid+'&lang=en&token=1',headers={'User-Agent':'Mozilla/5.0'}),timeout=25))
assert data['user']['screen_name']=='PaulSolt' and data['parent']['id_str']=='2095970470390530453'
path=root/'assets/external/paul-visual-feedback.png'
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':600,'height':900},device_scale_factor=2,timezone_id='Asia/Shanghai',locale='en-US')
    page.goto('https://platform.twitter.com/embed/Tweet.html?id='+tid+'&lang=en',wait_until='domcontentloaded',timeout=25000)
    page.get_by_text('My wife thinks',exact=False).wait_for(state='visible',timeout=18000)
    body=page.locator('body').inner_text()
    assert 'My wife thinks' in body, body[:200]
    quote=page.get_by_text('My wife thinks',exact=False)
    rect=quote.bounding_box()
    article=quote.locator('xpath=ancestor::article[1]').bounding_box()
    top=max(article['y'],rect['y']-75)
    page.screenshot(path=str(path),clip={'x':article['x'],'y':top,'width':article['width'],'height':article['y']+article['height']-top})
    browser.close()
record=dict(accessed_at=datetime.now(timezone.utc).isoformat(),source_url=source,post=data,
            file=path.relative_to(root).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            modifications='Native X embed reply screenshot, clipped to retain author, full reply and date; parent context in source receipt; no text edits or reconstruction')
receipt=root/'research/creative-ending-sources.json'
rows=json.loads(receipt.read_text(encoding='utf-8'))
rows=[r for r in rows if r['source_url']!=source]+[record]
receipt.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'text':data['text'],'file':record['file'],'screenshot_text':body},ensure_ascii=False))
