from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib
root=Path(__file__).resolve().parents[1]
out=root/'assets/external'
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True)
 for name,url,w in [
 ('agi-techrepublic-page.png','https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/',790)]:
  page=b.new_page(viewport={'width':w,'height':1600},device_scale_factor=2,locale='en-US',timezone_id='Asia/Shanghai')
  try:
   page.goto(url,wait_until='domcontentloaded',timeout=30000)
   if '-x-' in name:
    page.locator('article').first.wait_for(timeout=15000)
    page.wait_for_timeout(4000)
    print(json.dumps({'name':name,'images':page.locator('img').evaluate_all('(es)=>es.map(e=>({src:e.src,loaded:e.complete&&e.naturalWidth>0}))'),'videos':page.locator('video').count(),'frames':[f.url for f in page.frames]},ensure_ascii=False),flush=True)
    page.locator('article').first.screenshot(path=str(out/name))
   elif 'techrepublic' in name:
    h=page.locator('h1').first
    h.wait_for(timeout=15000)
    im=page.locator('img[alt*="OpenAI Launches"]').first
    im.scroll_into_view_if_needed()
    page.wait_for_function('(i)=>i.complete&&i.naturalWidth>0',arg=im.element_handle(),timeout=15000)
    h.scroll_into_view_if_needed()
    hr=h.bounding_box();ir=im.bounding_box()
    page.screenshot(path=str(out/name),clip={'x':max(0,hr['x']-12),'y':hr['y']-14,'width':min(w-hr['x'],max(hr['width'],ir['width'])+24),'height':ir['y']+ir['height']-hr['y']+42})
   else:
    page.locator('h1').first.wait_for(timeout=15000)
    page.wait_for_timeout(2000)
    print(json.dumps({'name':name,'title':page.title(),'images':page.locator('img').evaluate_all('(es)=>es.map(e=>({src:e.src,alt:e.alt,rect:e.getBoundingClientRect().toJSON()})).filter(e=>e.rect.width>250).slice(0,4)')},ensure_ascii=False),flush=True)
    page.screenshot(path=str(out/name))
   print('saved',name,flush=True)
  except Exception as e:print(name,repr(e),flush=True)
  page.close()
 b.close()
