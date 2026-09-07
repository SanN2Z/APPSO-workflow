from pathlib import Path
from playwright.sync_api import sync_playwright
import json, hashlib

root=Path(__file__).resolve().parents[1]
url='https://cognition.com/blog/devin-fusion'
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    page=browser.new_page(viewport={'width':1120,'height':780},device_scale_factor=1)
    page.goto(url,wait_until='domcontentloaded',timeout=45000)
    heading=page.get_by_text('Add a team selector to the search bar',exact=False).first
    heading.wait_for(timeout=15000)
    heading.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    path=root/'assets/external/cognition-fusion-failure.png'
    print(heading.evaluate('el=>[el.parentElement,el.parentElement.parentElement].map(n=>({tag:n.tagName,cls:n.className,text:n.innerText.slice(0,900)}))'))
    heading.locator('xpath=..').screenshot(path=str(path))
    (root/'research/fusion-image-receipt.json').write_text(json.dumps(dict(source_url=url,file=path.relative_to(root).as_posix(),
          sha256=hashlib.sha256(path.read_bytes()).hexdigest(),modifications='Native browser screenshot; no page edits'),indent=2)+'\n',encoding='utf-8')
    browser.close()
print('Captured original Cognition failure example')
