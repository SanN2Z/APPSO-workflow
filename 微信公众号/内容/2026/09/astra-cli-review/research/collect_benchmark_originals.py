from pathlib import Path
from urllib.request import Request,urlopen
from playwright.sync_api import sync_playwright
import json,re,hashlib

root=Path(__file__).resolve().parents[1]
out=root/'assets/external'
records=[]
aa='https://artificialanalysis.ai/articles/benchmarking-gpt-6-astra'
try:
    html=urlopen(Request(aa,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode()
    urls=list(dict.fromkeys(re.findall(r'https://cdn\.sanity\.io/images/[^\s"<>]+?\.png',html)))
    for i,url in enumerate(urls[:3]):
        data=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
        file=out/f'aa-astra-original-{i+1}.png'
        file.write_bytes(data)
        records.append(dict(file=file.relative_to(root).as_posix(),source_url=aa,media_url=url,kind='original_image',sha256=hashlib.sha256(data).hexdigest()))
    print(json.dumps({'aa_images':records},ensure_ascii=False),flush=True)
except Exception as e:print('AA fetch: '+str(e),flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1.5)
    for key,url in [('openai','https://openai.com/index/gpt-6-astra/'),('cognition','https://devin.ai/blog/gpt-6-astra')]:
        try:
            page.goto(url,wait_until='domcontentloaded',timeout=40000)
            page.wait_for_timeout(4000)
            print(json.dumps({'site':key,'title':page.title(),'head':page.locator('body').inner_text()[:250],
              'images':page.locator('img').evaluate_all('els=>els.map(e=>({alt:e.alt,src:e.currentSrc})).filter(e=>/bench|score|astra|frontier/i.test(e.alt+e.src)).slice(0,30)'),
              'charts':page.locator('svg').count(),'tables':page.locator('table').count()},ensure_ascii=False),flush=True)
            (root/f'research/{key}-benchmark-page.html').write_text(page.content(),encoding='utf-8')
            if key=='openai':
                tables=page.locator('table')
                for i in range(tables.count()):
                    table=tables.nth(i)
                    body=table.inner_text()
                    if any(s in body for s in ['DeepSWE','FrontierMath','Intelligence Index']):
                        table.scroll_into_view_if_needed()
                        file=out/f'openai-benchmark-table-{i}.png'
                        table.screenshot(path=str(file))
                        records.append(dict(file=file.relative_to(root).as_posix(),source_url=url,kind='browser_screenshot',text=body,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
            else:
                heading=page.get_by_text('FrontierCode 1.1 Extended Score',exact=True).first
                heading.wait_for(timeout=10000)
                print(heading.evaluate('el=>[el.parentElement,el.parentElement.parentElement].map(n=>({tag:n.tagName,cls:n.className,text:n.innerText.slice(0,1800)}))'),flush=True)
        except Exception as e:print(key+': '+str(e)[:300],flush=True)
    browser.close()
(root/'research/benchmark-originals-receipt.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
