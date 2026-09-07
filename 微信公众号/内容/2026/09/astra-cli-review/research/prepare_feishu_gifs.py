"""Prepare small, original-speed GIF derivatives for individual document upload."""
from pathlib import Path
import hashlib
import json
import subprocess
import av
import imageio_ffmpeg
import yaml

root = Path(__file__).resolve().parents[1]
out = root/'assets/feishu'
out.mkdir(exist_ok=True)
base = json.loads((root/'research/video-export-receipt.json').read_text(encoding='utf-8'))
logo = json.loads((root/'research/logo-recording-receipt.json').read_text(encoding='utf-8'))
sources = {k:Path(v['path']) for k,v in base['sources'].items()}
sources['logo'] = Path(logo['source_path'])
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
clips = [('logo-astra-play','logo',10,8,'Astra'),('lune-sky','lune',13,8,'Astra'),
         ('lune-tide','lune',7,6,'Astra'),('ghost-start','ghost',2,5,'Astra'),
         ('ghost-platforms','ghost',52,5,'Astra'),('ghost-finish','ghost',85,7,'Astra')]
records = []
for name,key,start,length,model in clips:
    path = out/(name+'.gif')
    for width,fps,colors in [(560,8,64),(480,8,48),(480,6,48),(420,6,32)]:
        filt = f'fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors={colors}[p];[b][p]paletteuse=dither=bayer:bayer_scale=4'
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-nostdin','-y','-ss',str(start),'-t',str(length),'-i',str(sources[key]),'-filter_complex',filt,'-an','-loop','0',str(path)],check=True)
        if path.stat().st_size < 1000000:
            break
    with av.open(str(path)) as c:
        frames = sum(1 for _ in c.decode(video=0))
    record = dict(file='assets/feishu/'+path.name,original_source_path=str(sources[key]),
                  derived_from='assets/video/'+path.name,model=model,start_seconds=start,excerpt_seconds=length,
                  width=width,fps=fps,colors=colors,bytes=path.stat().st_size,
                  sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),decoded_frames=frames,
                  modifications='原速节选、等比例缩小、降低帧率与色数；不插帧、不裁切、不改变玩法结果')
    assert frames>1 and record['bytes']<1000000
    records.append(record)
    print(json.dumps(record,ensure_ascii=False),flush=True)

(root/'research/feishu-gif-receipt.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest = root/'asset-manifest.yml'
known = {a['file'] for a in yaml.safe_load(manifest.read_text(encoding='utf-8'))['assets']}
with manifest.open('a',encoding='utf-8') as f:
    for r in records:
        if r['file'] in known: continue
        item = dict(file=r['file'],used_in_draft=True,visual_route='source_original',source_original_kind='community_screenshot',
                    original_pixels_preserved=False,source_type='user_provided',source='作者原始实测录屏的飞书轻量节选',
                    source_url='local-user-material://2026-09-05/'+Path(r['file']).name,
                    creator_or_rightsholder='作者；Logo 品牌元素归 APPSO / 爱范儿',obtained_on='2026-09-05',
                    modifications=f"原视频 {r['start_seconds']} 秒起，{r['excerpt_seconds']} 秒；宽 {r['width']}，{r['fps']} 帧/秒，{r['colors']} 色；"+r['modifications'],
                    rights_status='pending',allowed_platforms=[],model=r['model'],attribution='作者实际试玩，模型生成作品',
                    notes='本次授权减小体积以便飞书协作；小于 1 MB 是自定处理目标，不是飞书官方上限。未上传。较清晰的旧 GIF 与完整 MP4 保留，指纹和精确片段见 research/feishu-gif-receipt.json。')
        f.write(''.join('  '+line+'\n' for line in yaml.safe_dump([item],allow_unicode=True,sort_keys=False).splitlines()))
draft = root/'draft.md'
text = draft.read_text(encoding='utf-8')
for r in records:
    text = text.replace(']('+r['derived_from']+')',']('+r['file']+')')
draft.write_text(text,encoding='utf-8')
