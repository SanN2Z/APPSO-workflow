from pathlib import Path
import json
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
draft = (ROOT/'draft.md').read_text(encoding='utf-8')
receipt = json.loads((ROOT/'research/video-export-receipt.json').read_text(encoding='utf-8'))
manifest = ROOT/'asset-manifest.yml'
old = yaml.safe_load(manifest.read_text(encoding='utf-8'))
known = {a['file'] for a in old['assets']}
new = []
paths = [a['file'] for a in receipt['outputs']]
paths += ['assets/user-results/'+p.name for p in (ROOT/'assets/user-results').glob('doc-*.png')]
paths += ['assets/user-results/logo-astra-opening.png','assets/user-results/logo-astra-automated-completion.png']
paths += ['assets/user-results/'+p.name for p in (ROOT/'assets/user-results').glob('video-*.png')]
paths += ['assets/user-results/'+p.name for p in (ROOT/'assets/user-results').glob('lune-*.jpg')]
for name in paths:
    if name in known:
        continue
    video = next((v for v in receipt['outputs'] if v['file']==name),None)
    is_logo = 'logo-astra' in name
    item = dict(file=name,used_in_draft=f']({name})' in draft,visual_route='source_original',
                source_original_kind='community_screenshot',original_pixels_preserved=video is None,
                source_type='user_provided',source='用户实际测评截图或屏幕录制；模型生成作品的原始运行画面',
                source_url='local-user-material://2026-09-05/'+Path(name).name,
                creator_or_rightsholder='作者；APPSO 品牌元素归 APPSO / 爱范儿' if is_logo else '作者提供；模型生成网页或游戏，内含素材权利待核',
                obtained_on='2026-09-05',modifications='原图字节复制',rights_status='pending',allowed_platforms=[],
                attribution='作者实际测评，画面中的作品由 AI 编写',
                notes='本次任务已授权本地处理与入稿；未执行公开发布。不是 AI 生成的模拟运行截图。临时下载凭据不保存。')
    if video:
        item['modifications'] = ('完整录屏缩至 1280×720，H.264/AAC，保留原音，未变速' if video['kind']=='full_mp4'
                                 else f"原视频 {video['start_seconds']} 秒起，截取 {video['excerpt_seconds']} 秒；640×360，10 帧/秒，64 色，无声循环；未变速")
        item['notes'] += ' 时间戳、源文件指纹及导出指纹见 research/video-export-receipt.json。'
    if is_logo:
        item['notes'] += ' 来自被测项目 artifacts；通关图为项目自动键盘测试，不能归为作者真人试玩。'
    if Path(name).name.startswith(('video-', 'lune-')) and video is None:
        item['modifications'] = '原视频抽帧，仅供内部选片；OpenCV 请求时间不是精确展示时间，以原视频 PTS 与导出清单为准'
        item['notes'] += ' 未用于正文，不作为独立截图任务成果。'
        item['original_pixels_preserved'] = name.endswith('.png')
    new.append(item)
with manifest.open('a',encoding='utf-8') as f:
    for item in new:
        f.write(''.join('  '+line+'\n' for line in yaml.safe_dump([item],allow_unicode=True,sort_keys=False).splitlines()))

labels = {'ghost-full.mp4':'小妖快跑｜完整试玩','lune-full.mp4':'月屿｜完整操作',
          'ghost-start.gif':'小妖起跑','ghost-platforms.gif':'八卦台路段','ghost-finish.gif':'到达终点',
          'lune-tide.gif':'月屿潮汐调节','lune-sky.gif':'月屿天色与沉浸模式'}
lines = ['# 视频与动图交接','',
         '两段原始录屏保留在作者的 Captures 文件夹，本地输出不覆盖原文件。MP4 保留完整时长和原音；GIF 为原速无声节选。',
         '', '正文已经插入 5 张 GIF。需要更清楚地看文字或连续试玩时，使用完整 MP4。所有输出均通过完整解码检查。', '',
         '| 素材 | 时长 | 大小 | 原录屏片段 |','|---|---:|---:|---|']
for item in receipt['outputs']:
    name = Path(item['file']).name
    excerpt = f"{item['start_seconds']}–{item['start_seconds']+item['excerpt_seconds']} 秒" if 'start_seconds' in item else '完整录屏'
    lines.append(f"| [{labels[name]}](../{item['file']}) | {item['duration_seconds']:.1f} 秒 | {item['bytes']/1000000:.2f} MB | {excerpt} |")
lines += ['', 'MP4：1280×720，H.264/AAC，支持边加载边播放。GIF：640×360，10 帧/秒，64 色。GIF 会损失渐变和小字细节，完整 MP4 可供对照。', '',
          '小妖片段保留起跑拥挤、屋檐遮挡和到达终点。未剪成一次无失误通关。月屿片段展示真实滑杆、天色与沉浸模式操作。', '',
          '本次只处理本地素材和文章草稿；未上传飞书或公众号。模型生成作品已在图注标明。公开使用的素材权利仍按 asset-manifest.yml 保留待核状态。']
(ROOT/'research/media-handoff.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Registered',len(new),'assets; wrote media handoff.')
