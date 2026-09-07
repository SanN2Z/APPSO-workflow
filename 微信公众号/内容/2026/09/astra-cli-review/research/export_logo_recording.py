from pathlib import Path
import subprocess
import hashlib
import json
import av
import imageio_ffmpeg
import shutil
import yaml

root = Path(__file__).resolve().parents[1]
receipt_path = root/'research/logo-recording-receipt.json'
receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
source = Path(receipt['source_path'])
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
out = root/'assets/video'

def run(args):
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-nostdin',*args],check=True)

def meta(path):
    with av.open(str(path)) as c:
        v = c.streams.video[0]
        return dict(bytes=path.stat().st_size,sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),
                    duration_seconds=c.duration/1000000,width=v.width,height=v.height,has_audio=bool(c.streams.audio))

target = out/'logo-astra-full.mp4'
run(['-y','-i',str(source),'-map','0:v:0','-map','0:a?','-c','copy','-map_metadata','-1','-movflags','+faststart',str(target)])
outputs = [dict(file='assets/video/'+target.name,kind='full_mp4',modifications='完整录屏无重编码封装；保留视频、原音与时间顺序，faststart',**meta(target))]
for name,start,length in [('logo-astra-start',2,8),('logo-astra-play',10,8)]:
    target = out/(name+'.gif')
    filt = 'fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=3'
    run(['-y','-ss',str(start),'-t',str(length),'-i',str(source),'-filter_complex',filt,'-an','-loop','0',str(target)])
    outputs.append(dict(file='assets/video/'+target.name,kind='excerpt_gif',start_seconds=start,excerpt_seconds=length,
                        modifications=f'原录屏 {start}–{start+length} 秒，原速无声节选；960×540，12 帧/秒，96 色；无裁切或场景替换',**meta(target)))
for item in outputs:
    run(['-i',str(root/item['file']),'-f','null','-'])
    item['full_decode_check'] = 'passed'
receipt.update(model='Astra',model_evidence='用户新回传的截图与录屏，匹配此前 Astra 独立项目 Play Lab 的页面和关卡；用户确认这项已做好',outputs=outputs)
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

attachment = Path('D:/xwechat_files/wxid_5vzb6bw6dt0d22_a349/temp/InputTemp/4f157bc1-509b-42e8-bd29-b34deb232ced.png')
screen = root/'assets/user-results/logo-astra-user.png'
shutil.copyfile(attachment,screen)
manifest_path = root/'asset-manifest.yml'
known = {x['file'] for x in yaml.safe_load(manifest_path.read_text(encoding='utf-8'))['assets']}
items = outputs+[dict(file='assets/user-results/'+screen.name,kind='user_screenshot',modifications='用户附件原字节复制',sha256=hashlib.file_digest(screen.open('rb'),'sha256').hexdigest())]
for item in items:
    if item['file'] in known:
        continue
    record = dict(file=item['file'],used_in_draft=item['kind']!='full_mp4',visual_route='source_original',source_original_kind='community_screenshot',
                  original_pixels_preserved=item['kind'] in ('full_mp4','user_screenshot'),source_type='user_provided',
                  source='用户 APPSO Logo 乐园实际截图与真人试玩录屏',source_url='local-user-material://2026-09-05/'+Path(item['file']).name,
                  creator_or_rightsholder='作者；APPSO / 爱范儿品牌元素',obtained_on='2026-09-05',modifications=item['modifications'],
                  rights_status='pending',allowed_platforms=[],model='Astra',attribution='Astra 生成游戏，作者实际试玩',
                  notes='已授权本地处理与入稿；不代表品牌公开改版或发布授权。模型生成游戏的真实运行记录，未用生图工具模拟画面。源与输出指纹见 research/logo-recording-receipt.json。')
    with manifest_path.open('a',encoding='utf-8') as f:
        f.write(''.join('  '+line+'\n' for line in yaml.safe_dump([record],allow_unicode=True,sort_keys=False).splitlines()))

with (root/'research/media-handoff.md').open('a',encoding='utf-8') as f:
    f.write('\n## 新增：Astra APPSO Logo 真人试玩\n\n完整录屏约 26 秒，原视频和原音不重编码。两张 GIF 分别展示开始游戏与继续操作；这段没有录到通关。\n\n')
    for item in outputs:
        f.write(f"- [{Path(item['file']).name}](../{item['file']})：{item['duration_seconds']:.1f} 秒，{item['bytes']/1000000:.2f} MB。\n")
print(json.dumps(outputs,ensure_ascii=False),flush=True)
