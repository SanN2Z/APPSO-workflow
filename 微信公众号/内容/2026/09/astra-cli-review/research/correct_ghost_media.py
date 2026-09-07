"""Author correction: 10:54 Astra; 12:03:11 and 12:03:51 Fable 5.1."""
from pathlib import Path
import av, copy, hashlib, imageio_ffmpeg, json, re, shutil, subprocess, yaml

root=Path(__file__).resolve().parents[1]
caps=Path(r'C:\Users\22684\Videos\Captures')
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
confirmation='作者最新明确更正：10-54-51 为 Astra；12-03-11 与 12-03-51 均为 Fable 5.1。覆盖此前相反归属。'
receipt={'confirmation':confirmation,'sources':[],'outputs':[]}
def run(args):
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-nostdin',*args],check=True)
def fingerprint(path):
    return dict(bytes=path.stat().st_size,sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest())
for stamp,label in [('12-03-11','intro'),('12-03-51','play')]:
    src=next(caps.glob(f'*小妖*{stamp}.mp4'))
    receipt['sources'].append(dict(file=str(src),model='Fable 5.1',**fingerprint(src)))
    target=root/f'assets/video/ghost-fable-{label}-full.mp4'
    if not target.is_file(): run(['-y','-i',str(src),'-map','0:v:0','-map','0:a?','-vf','scale=1280:-2:flags=lanczos',
         '-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(target)])
    receipt['outputs'].append(dict(file=target.relative_to(root).as_posix(),model='Fable 5.1',source=str(src),kind='complete_mp4',**fingerprint(target)))
    start,length=(0,6) if label=='intro' else (16,7)
    target=root/f'assets/feishu/ghost-fable-{label}.gif'
    for width,fps,colors in [(480,8,48),(420,6,32),(360,6,32),(360,5,24),(320,5,24)]:
        filt=f'fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors={colors}[p];[b][p]paletteuse=dither=bayer:bayer_scale=4'
        run(['-y','-ss',str(start),'-t',str(length),'-i',str(src),'-filter_complex',filt,'-an','-loop','0',str(target)])
        if target.stat().st_size<1000000:break
    assert target.stat().st_size<1000000
    receipt['outputs'].append(dict(file=target.relative_to(root).as_posix(),model='Fable 5.1',source=str(src),kind='excerpt_gif',
      start_seconds=start,excerpt_seconds=length,width=width,fps=fps,colors=colors,**fingerprint(target)))
    print(f'Exported Fable {label}',flush=True)
for item in receipt['outputs']:
    run(['-i',str(root/item['file']),'-f','null','-'])
    item['full_decode_check']='passed'
for src in (root/'research/viewing/missing-ghost').glob('*.png'):
    receipt['outputs'].append(dict(file=src.relative_to(root).as_posix(),model='Fable 5.1',kind='research_frame',
      source=str(next(caps.glob(f'*小妖*{src.name[:8]}.mp4'))),**fingerprint(src)))
# Patch machine-readable attribution; retain original media bytes and names.
for path in [root/'research/video-export-receipt.json',root/'research/feishu-gif-receipt.json']:
    data=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data,dict):
        data['sources']['ghost']['model']='Astra'
        data['sources']['ghost']['model_evidence']=confirmation
        entries=data['outputs']
    else:entries=data
    for row in entries:
        if row.get('source')=='ghost' or '/ghost-' in row.get('file',''):
            row['model']='Astra'
            row['model_evidence']=confirmation
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=root/'asset-manifest.yml'
raw=manifest.read_text(encoding='utf-8')
def fix(block):
    text=block.group(0)
    name=re.search(r'file: (.+)',text).group(1)
    if re.match(r'assets/(?:video/ghost-|feishu/ghost-|user-results/video-)',name) and 'ghost-fable-' not in name:
        text=re.sub(r'    model: .*\n','    model: Astra\n',text)
        text=re.sub(r'    model_identification: .*\n','',text)
        text=text.rstrip()+'\n    model_identification: '+confirmation+'\n'
    return text
raw=re.sub(r'  - file:.*?(?=  - file:|\Z)',fix,raw,flags=re.S)
known={a['file'] for a in yaml.safe_load(raw)['assets']}
for row in receipt['outputs']:
    if row['file'] in known:continue
    entry=dict(file=row['file'],used_in_draft=False,visual_route='source_original',source_original_kind='community_screenshot',
      original_pixels_preserved=row['kind']=='research_frame',source_type='user_provided',source='作者录屏，'+row['source'],
      source_url='local-user-material://2026-09-05/'+Path(row['file']).name,creator_or_rightsholder='作者提供；模型生成游戏中的素材权利待核',
      obtained_on='2026-09-05',modifications='原速节选或完整转码，原文件未改；精确时间及指纹见 research/ghost-correction-receipt.json',
      rights_status='pending',allowed_platforms=[],attribution='Fable 5.1 生成，作者实际录屏',model='Fable 5.1',model_identification=confirmation)
    if row['kind']=='research_frame':entry['use']='research_reference'
    raw+=''.join('  '+line+'\n' for line in yaml.safe_dump([entry],allow_unicode=True,sort_keys=False,width=100000).splitlines())
manifest.write_text(raw,encoding='utf-8')
(root/'research/ghost-correction-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# New infographic revision preserves both former receipts and assets.
planpath=root/'research/image-generation-plan.json'
plan=json.loads(planpath.read_text(encoding='utf-8'))
task=copy.deepcopy(next(t for t in plan['tasks'] if t['id']=='infographic-001'))
task['id']='infographic-003'
stage=task['final_stage']
stage['output']='assets/infographic-003-image2.png'
stage['receipt']='research/image-generation-runs/infographic-003-final-preflight.json'
stage['input_assets']=['assets/infographic-001-image2.png','research/source-assets/appsso-logo-red-background.png']
stage['preserve']=[s.replace('Astra 单元格「对照画面待补」','Astra 单元格「录屏已跑到终点」') for s in stage['preserve']]
stage['output_constraints']=[s.replace('「待补」「疑似」必须清楚保留','「疑似」必须清楚保留').replace('除页脚标志外，不再使用第二个图像参考。','保留第一张参考图的排版与第二张参考图的 Logo。') for s in stage['output_constraints']]
stage['output_constraints']+=['对第一张输入图做局部文字修订，三行表格、所有其他文字及图标布局均保留。唯一事实修改：第三行 Astra 一栏从「对照画面待补」改为「录屏已跑到终点」。不是重新设计，也不增加游戏画面。']
plan['tasks']=[t for t in plan['tasks'] if t['id']!=task['id']]+[task]
planpath.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Corrected source records, prepared updated infographic',flush=True)
