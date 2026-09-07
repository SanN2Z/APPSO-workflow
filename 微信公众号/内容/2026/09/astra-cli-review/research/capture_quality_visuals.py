from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
import json,hashlib
root=Path(__file__).resolve().parents[1]
out=root/'assets/external'
records=[]
def record(name,url,kind,detail):
 path=out/name
 records.append(dict(file=path.relative_to(root).as_posix(),source_url=url,kind=kind,detail=detail,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),accessed_at=datetime.now(timezone.utc).isoformat()))
def get(url):return urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read()
try:
 url='https://www.youtube.com/watch?v=dnSpKF5pWNQ'
 meta=json.loads(get('https://www.youtube.com/oembed?url='+url+'&format=json'))
 assert meta['author_name']=='TIME',meta
 raw=get('https://i.ytimg.com/vi/dnSpKF5pWNQ/maxresdefault.jpg')
 (out/'agi-time-interview.jpg').write_bytes(raw)
 record('agi-time-interview.jpg',url,'interview_thumbnail',meta)
 print('TIME downloaded',flush=True)
except Exception as e: print('TIME',repr(e),flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True)
 for name,url in [
  ('agi-openai-page.png','https://openai.com/index/gpt-6-astra/'),
  ('agi-techrepublic-page.png','https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/'),
  ('agi-openai-x-full.png','https://platform.twitter.com/embed/Tweet.html?id=2095595741528125780&lang=en')]:
  page=browser.new_page(viewport={'width':760 if '-x-' in name else 1100,'height':1000},device_scale_factor=2,locale='en-US')
  try:
   page.goto(url,wait_until='domcontentloaded',timeout=30000)
   if '-x-' in name:
    article=page.locator('article').first
    article.wait_for(state='visible',timeout=20000)
    page.wait_for_function("[...document.images].filter(i=>i.width>100).every(i=>i.complete&&i.naturalWidth>0)",timeout=12000)
    article.screenshot(path=str(out/name))
    record(name,'https://x.com/OpenAI/status/2095595741528125780','full_native_post',article.inner_text())
   else:
    page.locator('h1').first.wait_for(state='visible',timeout=20000)
    page.wait_for_timeout(1800)
    page.screenshot(path=str(out/name))
    record(name,url,'native_page',dict(title=page.title(),headings=page.locator('h1').all_text_contents()))
    print(json.dumps({'name':name,'images':page.locator('img').evaluate_all('(els)=>els.map(i=>({src:i.currentSrc,alt:i.alt,rect:i.getBoundingClientRect().toJSON(),loaded:i.complete&&i.naturalWidth>0})).filter(i=>i.rect.width>250).slice(0,6)')},ensure_ascii=False),flush=True)
   print('captured',name,flush=True)
  except Exception as e:print(name,repr(e),flush=True)
  finally:page.close()
 browser.close()
(root/'research/quality-visual-receipts.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
