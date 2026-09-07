from pathlib import Path
import json, yaml, hashlib, re
from PIL import Image

root=Path(__file__).resolve().parents[1]
manifest=root/'asset-manifest.yml'
raw=manifest.read_text(encoding='utf-8')
draft=(root/'draft.md').read_text(encoding='utf-8')
rows=json.loads((root/'research/visual-refresh-receipt.json').read_text(encoding='utf-8'))
byfile={r['file']:r for r in rows if r.get('file')}
toy=next(r for r in rows if r['name']=='claire-toy-computer')
new=[]
files=list((root/'assets/external').glob('*'))+list((root/'research/viewing').glob('claire-toy-*.png'))
for path in files:
    relative=path.relative_to(root).as_posix()
    if f'file: {relative}\n' in raw: continue
    data=byfile.get(relative)
    if 'claire-toy-' in path.name and path.suffix=='.png':
        data=toy
    if path.name=='cognition-fusion-failure.png':
        data=dict(author='Cognition',source_url='https://cognition.com/blog/devin-fusion')
    assert data,relative
    official=data['author'] in ['Anthropic','Cognition']
    with Image.open(path) as im: im.verify()
    new.append(dict(file=relative,used_in_draft=f']({relative})' in draft,visual_route='source_original',
                    source_original_kind='official_original' if official else 'community_screenshot',
                    original_pixels_preserved=True,source_type='official' if official else 'community',
                    source='官网案例原图' if official else 'X 作者公开演示原始媒体',
                    source_url=data['source_url'],creator_or_rightsholder=data['author'],obtained_on='2026-09-05',
                    modifications='官方原图或原生浏览器卡片截图，无改写' if official else ('视频原帧，无裁切或重绘；见视觉回执' if path.suffix=='.png' else '原始视频封面，无裁切或改写'),
                    rights_status='pending',allowed_platforms=[],attribution=f'图源：{data["author"]}',
                    notes='研究／草稿候选；公开来源不等于转载授权。'))
if new:
    raw+=''.join('  '+line+'\n' for line in yaml.safe_dump(new,allow_unicode=True,sort_keys=False,width=100000).splitlines())
manifest.write_text(raw,encoding='utf-8')
records=[]
for path in files:
    with Image.open(path) as im: size=im.size
    records.append(dict(file=path.relative_to(root).as_posix(),width=size[0],height=size[1],bytes=path.stat().st_size,
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(root/'research/visual-refresh-file-check.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Report uninterrupted public prose between images; links count as labels, not URL bytes.
body=re.sub(r'<!--.*?-->','',draft.split('---',2)[2],flags=re.S)
gaps=[]
for part in re.split(r'!\[[^\]]*\]\([^)]+\)',body):
    text=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',part)
    gaps.append(dict(characters=len(re.sub(r'\s','',text)),start=text.strip()[:75]))
print(json.dumps(dict(registered=len(new),largest_prose_gaps=sorted(gaps,key=lambda x:x['characters'],reverse=True)[:5]),ensure_ascii=False))
