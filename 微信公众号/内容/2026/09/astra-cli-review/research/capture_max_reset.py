from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
import json,hashlib
root=Path(__file__).resolve().parents[1]
tid='2095967323412930677'
data=json.load(urlopen(Request('https://cdn.syndication.twimg.com/tweet-result?id='+tid+'&lang=en&token=1',headers={'User-Agent':'Mozilla/5.0'}),timeout=25))
assert data['user']['screen_name']=='lydiahallie' and 'weekly limits' in data['text']
print(json.dumps({'text':data['text'],'created_at':data['created_at']},ensure_ascii=False),flush=True)
path=root/'assets/external/claude-max-weekend-reset.png'
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True)
 page=b.new_page(viewport={'width':550,'height':1000},device_scale_factor=2,locale='en-US',timezone_id='Asia/Shanghai')
 page.goto('https://platform.twitter.com/embed/Tweet.html?id='+tid+'&lang=en&cards=visible',wait_until='domcontentloaded',timeout=30000)
 page.get_by_text('We’ve just reset',exact=False).or_(page.get_by_text("We've just reset",exact=False)).first.wait_for(state='visible',timeout=15000)
 page.wait_for_function("document.images.length>0 && [...document.images].every(i=>i.complete&&i.naturalWidth>0)",timeout=15000)
 page.locator('article').first.screenshot(path=str(path))
 b.close()
r=dict(source_url='https://x.com/lydiahallie/status/'+tid,post=data,file=path.relative_to(root).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),accessed_at=datetime.now(timezone.utc).isoformat())
(root/'research/claude-max-weekend-reset.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('saved',r['file'])
