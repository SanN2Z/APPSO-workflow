from pathlib import Path
from urllib.request import Request, urlopen
import concurrent.futures
import hashlib
import json
from datetime import datetime, timezone

root=Path(__file__).resolve().parents[1]
out=root/'assets/external'
out.mkdir(exist_ok=True)
def get(url):
    return urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
def post(item):
    name,tid=item
    data=json.loads(get(f'https://cdn.syndication.twimg.com/tweet-result?id={tid}&lang=en&token=1'))
    author=data.get('user',{}).get('screen_name')
    if not author or not data.get('text'): raise ValueError(f'Empty post: {tid}')
    row=dict(name=name,id=tid,author=author,text=data.get('text'),created_at=data.get('created_at'),
             source_url=f'https://x.com/{author}/status/{tid}',accessed_at=datetime.now(timezone.utc).isoformat(),
             mediaDetails=data.get('mediaDetails',[]))
    media=row['mediaDetails']
    if media:
        url=media[0]['media_url_https']
        raw=get(url)
        path=out/f'{name}.jpg'
        path.write_bytes(raw)
        row.update(file=path.relative_to(root).as_posix(),download_url=url,sha256=hashlib.sha256(raw).hexdigest())
    return row
items=[('berman-fallguys','2095616764793270705'),('berman-city','2095595893991129444'),
       ('claire-toy-computer','2095625355231142079'),('riley-shooter','2095679352927056230')]
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for item,future in zip(items,[pool.submit(post,x) for x in items]):
        try:
            row=future.result(); rows.append(row)
            print(json.dumps({k:row.get(k) for k in ['name','author','text','file']},ensure_ascii=False),flush=True)
        except Exception as e:
            rows.append(dict(name=item[0],error=type(e).__name__))
            print(item[0],type(e).__name__,flush=True)
for name,url in [('anthropic-game-solo','https://www-cdn.anthropic.com/images/4zrzovbb/website/23c98f1d7ae720bfb39190d50e0706c03b177ad8-1999x1320.png'),
                 ('anthropic-game-iterated','https://www-cdn.anthropic.com/images/4zrzovbb/website/a8bef95425966495629095a5cb38bde4a8b13558-1999x997.png')]:
    raw=get(url); path=out/f'{name}.png'; path.write_bytes(raw)
    rows.append(dict(name=name,file=path.relative_to(root).as_posix(),download_url=url,
                     source_url='https://www.anthropic.com/engineering/harness-design-long-running-apps',
                     sha256=hashlib.sha256(raw).hexdigest(),author='Anthropic',accessed_at=datetime.now(timezone.utc).isoformat()))
(root/'research/visual-refresh-receipt.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
