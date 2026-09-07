from pathlib import Path
import json
import hashlib
from urllib.request import Request, urlopen
import av

root=Path(__file__).resolve().parents[1]
def get(url):
    return urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read()
receipt=root/'research/visual-refresh-receipt.json'
rows=json.loads(receipt.read_text(encoding='utf-8'))
for name,key in [('anthropic-game-solo-play','79217dbfce3f31172eb7fd4deee5449023c9b2ac-1999x757'),
                 ('anthropic-game-full-play','f2953550e51957a0a49a3792a0df3bcfed0fde48-1994x1654')]:
    url=f'https://www-cdn.anthropic.com/images/4zrzovbb/website/{key}.png'
    path=root/f'assets/external/{name}.png'; path.write_bytes(get(url))
    rows.append(dict(name=name,file=path.relative_to(root).as_posix(),download_url=url,
                     source_url='https://www.anthropic.com/engineering/harness-design-long-running-apps',author='Anthropic',
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
toy=next(r for r in rows if r['name']=='claire-toy-computer')
variants=toy['mediaDetails'][0]['video_info']['variants']
v=min((x for x in variants if x.get('bitrate',0)>=800000 and x['content_type']=='video/mp4'),key=lambda x:x['bitrate'])
video=root/'research/source-assets/claire-toy.mp4'; video.write_bytes(get(v['url']))
with av.open(str(video)) as c:
    duration=c.duration/1000000
    targets=[5,10,15,20,30]
    todo=iter(t for t in targets if t<duration)
    target=next(todo,None)
    for frame in c.decode(video=0):
        if target is not None and frame.time>=target:
            frame.to_image().save(root/f'research/viewing/claire-toy-{target}.png')
            target=next(todo,None)
        if target is None: break
toy['video_download']=dict(url=v['url'],file=video.relative_to(root).as_posix(),duration=duration,sha256=hashlib.sha256(video.read_bytes()).hexdigest())
receipt.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'toy_duration':duration,'stills':targets}))
