from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
root=Path(__file__).resolve().parents[1]
items=[('rollout','2096002992046796932'),('claude-reset','2094856679250919746'),('astra-reset','2096035437299237298'),('fallguys','2095616764793270705'),('city','2095595893991129444')]
def run(item):
 name,tid=item
 try:
  req=Request('https://cdn.syndication.twimg.com/tweet-result?id='+tid+'&lang=en&token=1',headers={'User-Agent':'Mozilla/5.0'})
  d=json.load(urlopen(req,timeout=25))
  author=d['user']['screen_name']
  r=dict(label=name,source_url='https://x.com/'+author+'/status/'+tid,author=author,text=d.get('text'),created_at=d.get('created_at'),mediaDetails=d.get('mediaDetails'),accessed_at=datetime.now(timezone.utc).isoformat())
  return r
 except Exception as e:return dict(label=name,error=str(e))
with ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(run,items))
(root/'research/opening-posts-20260905.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for r in rows: print(json.dumps({k:v for k,v in r.items() if k!='mediaDetails'},ensure_ascii=False))
