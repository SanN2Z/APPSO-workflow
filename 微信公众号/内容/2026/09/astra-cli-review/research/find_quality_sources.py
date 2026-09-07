from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import json
urls=[
'https://ceointerviews.ai/entity/5847-greg-brockman-openai/',
'https://thursdai.news/ep/astra',
'https://time.com/article/2026/08/26/openai-sam-altman-interview/',
'https://openai.com/index/gpt-6-astra/']
def run(url):
 try:
  raw=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read()
  s=BeautifulSoup(raw,'html.parser')
  links=[{'text':a.get_text(' ',strip=True)[:90],'url':a.get('href')} for a in s.select('a[href]') if any(x in a.get('href','') for x in ['youtu','x.com/','twitter.com/'])]
  imgs=[{'alt':i.get('alt'),'src':i.get('src')} for i in s.select('img')][:15]
  return dict(url=url,links=links[:30],images=imgs,og=[m.get('content') for m in s.select('meta[property="og:image"]')])
 except Exception as e:return dict(url=url,error=str(e))
with ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(run,urls):print(json.dumps(r,ensure_ascii=False),flush=True)
