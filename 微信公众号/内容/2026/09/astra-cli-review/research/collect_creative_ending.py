from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import json, hashlib

root=Path(__file__).resolve().parents[1]
def get(url):
    return urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read()
data=json.loads(get('https://cdn.syndication.twimg.com/tweet-result?id=2096008086901113339&lang=en&token=1'))
assert data['user']['screen_name']=='anshuc' and 'concept images' in data['text']
parent=data['parent']
url=parent['mediaDetails'][0]['media_url_https']
raw=get(url)
path=root/'assets/external/anshu-concept-game.jpg'
path.write_bytes(raw)
record=dict(accessed_at=datetime.now(timezone.utc).isoformat(),source_url='https://x.com/anshuc/status/2096008086901113339',post=data,
            file=path.relative_to(root).as_posix(),media_source_url='https://x.com/anshuc/status/'+parent['id_str'],download_url=url,
            sha256=hashlib.sha256(raw).hexdigest(),modifications='Original video poster bytes; no redraw or edits')
(root/'research/creative-ending-sources.json').write_text(json.dumps([record],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'author':data['user']['screen_name'],'text':data['text'],'file':record['file']},ensure_ascii=False))
