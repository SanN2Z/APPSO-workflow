"""Create a file-upload handoff without embedding image bytes in the clipboard text."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile
import yaml
from PIL import Image

root=Path(__file__).resolve().parents[1]
out=root/'dist/feishu-upload'
out.mkdir(parents=True,exist_ok=True)
raw=(root/'draft.md').read_text(encoding='utf-8')
_,front,body=raw.split('---',2)
title=yaml.safe_load(front)['title']
body=re.sub(r'<!--.*?-->','',body,flags=re.S).strip()
rows=[]
def image_ref(match):
    alt,relative=match.group(1),match.group(2)
    source=(root/relative).resolve()
    assert source.is_relative_to(root.resolve())
    index=len(rows)+1
    target=out/(f'{index:02d}-'+source.name)
    shutil.copyfile(source,target)
    with Image.open(target) as im:
        rows.append(dict(index=index,alt=alt,source=relative,file=target.name,bytes=target.stat().st_size,
                         width=im.width,height=im.height,frames=getattr(im,'n_frames',1),
                         sha256=hashlib.file_digest(target.open('rb'),'sha256').hexdigest()))
    return f'![{alt}]({target.name})'
md='# '+title+'\n\n'+re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',image_ref,body)+'\n'
# Remove only stale numbered images produced by this handoff script.
current_names={r['file'] for r in rows}
for stale in out.iterdir():
    if stale.is_file() and re.fullmatch(r'\d{2}-.+\.(?:png|jpe?g|gif|webp)',stale.name,re.I) and stale.name not in current_names:
        assert stale.resolve().is_relative_to(out.resolve())
        stale.unlink()
(out/'正文.md').write_text(md,encoding='utf-8')
by_name={r['file']:r for r in rows}
def placeholder(match):
    r=by_name[match.group(2)]
    return f"【配图 {r['index']:02d}：{r['alt']}｜文件 {r['file']}】"
plain=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',placeholder,md)
plain=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'\1（\2）',plain)
plain=re.sub(r'^#{1,6}\s+','',plain,flags=re.M)
plain=re.sub(r'^>\s?','',plain,flags=re.M)
plain=re.sub(r'^\*([^*\n]+)\*$','\1',plain,flags=re.M)
(out/'正文-先复制这份.txt').write_text(plain,encoding='utf-8')
notes=['# 飞书协作素材','',
       '先复制「正文-先复制这份.txt」里的文字。它没有嵌入图片数据，配图位置已按顺序编号。',
       '再从本文件夹逐张上传对应编号的图片或 GIF；不要从整篇 HTML 一次复制所有图片。',
       '「正文.md」保留标题、链接和相对图片路径，供已支持 Markdown 的导入工具使用；此处未验证飞书的 Markdown 导入能力。',
       f"{sum(r['frames']>1 for r in rows)} 张 GIF 均小于 1 MB。这是本次自定处理目标，不是飞书官方容量上限。缩小后小字和渐变会变粗，完整 MP4 与较清晰的旧 GIF 保留在内容包 assets/video。",
       'ZIP 仅用于打包传递，解压后按图号使用，不是已验证的一键飞书导入文件。',
       '标有「上下滑动：」的长图已在本地 HTML 中显示为滑动窗口；本文件包仍交付完整原图。公众号组件需另走 scroll-handoff，不能保证飞书支持同样的交互。',
       '此包尚未上传；当前登录凭据已过期。图像权利待核与文章草稿状态不因打包改变。','',
       '| 图号 | 文件 | 大小 |','|---|---|---:|']
for r in rows: notes.append(f"| {r['index']:02d} | {r['file']} | {r['bytes']/1000000:.2f} MB |")
(out/'上传说明.md').write_text('\n'.join(notes)+'\n',encoding='utf-8')
receipt=dict(source_draft_sha256=hashlib.file_digest((root/'draft.md').open('rb'),'sha256').hexdigest(),
             title=title,assets=rows,text_bytes=(out/'正文-先复制这份.txt').stat().st_size,external_write=False,
             clipboard_contains_image_bytes=False)
(out/'素材清单.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
archive=root/'dist/feishu-upload.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in [r['file'] for r in rows]+['正文.md','正文-先复制这份.txt','上传说明.md','素材清单.json']:
        z.write(out/name,arcname=name)

# Internal inspection only: compare representative frames at native light-GIF dimensions.
canvas=Image.new('RGB',(480,900),'white')
for i,name in enumerate(['lune-sky','ghost-platforms','ghost-finish']):
    im=Image.open(root/f'assets/feishu/{name}.gif')
    im.seek(im.n_frames//2)
    canvas.paste(im.convert('RGB'),(0,i*300))
canvas.save(root/'research/viewing/feishu-gif-check.jpg',quality=92)

# Refresh actual body usage flags without changing historical source/rights fields.
manifest=root/'asset-manifest.yml'
def used_flag(match):
    block=match.group(0)
    file=re.search(r'file: (.+)',block).group(1).strip()
    return re.sub(r'used_in_draft: (true|false)','used_in_draft: '+str(f']({file})' in raw).lower(),block)
manifest.write_text(re.sub(r'  - file:.*?(?=  - file:|\Z)',used_flag,manifest.read_text(encoding='utf-8'),flags=re.S),encoding='utf-8')
print(json.dumps({'text_bytes':receipt['text_bytes'],'asset_count':len(rows),'gif_count':sum(r['frames']>1 for r in rows),
                  'archive_bytes':archive.stat().st_size,'gif_bytes':{r['file']:r['bytes'] for r in rows if r['frames']>1}},ensure_ascii=False))
