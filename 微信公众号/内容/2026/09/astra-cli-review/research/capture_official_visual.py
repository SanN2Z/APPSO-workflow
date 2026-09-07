from pathlib import Path
from playwright.sync_api import sync_playwright
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
import json,hashlib
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=True)
 page=b.new_page(viewport={'width':1200,'height':850},device_scale_factor=2)
 url='https://www.anthropic.com/claude-fable-and-mythos-5-1'
 page.goto(url,wait_until='domcontentloaded',timeout=30000)
 page.locator('h1').first.wait_for(timeout=15000)
 page.wait_for_timeout(2500)
 page.screenshot(path=str(root/'assets/external/agi-fable-official-page.png'))
 print(json.dumps({'url':page.url,'title':page.title(),'h1':page.locator('h1').all_text_contents()},ensure_ascii=False))
 b.close()
