"""Append source records without granting publication rights."""
import hashlib, json, re
from pathlib import Path
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
manifest = yaml.safe_load((ROOT/'asset-manifest.yml').read_text(encoding='utf-8'))
specs = [
 ('astra-full-reset-embed.png', 'https://x.com/thsottiaux/status/2096035437299237298', 'Tibo / @thsottiaux', 'x_screenshot', '全量开放后宣布向 Plus、Pro、Business 提供 banked reset'),
 ('astra-plus-business-live-embed.png', 'https://x.com/thsottiaux/status/2096002992046796932', 'Tibo / @thsottiaux', 'x_screenshot', '宣布 Plus 和 Business 也已完成开放'),
 ('reset-tracker.png', 'https://when.usagereset.at/', 'when.usagereset.at / Bettag Systems', 'community_screenshot', '第三方额度追踪站，含作者预测'),
 ('claude-reset-embed.png', 'https://x.com/ClaudeDevs/status/2094856679250919746', 'Anthropic / ClaudeDevs', 'official_original', 'Fable 5.1 发布重置官推'),
 ('astra-reset-embed.png', 'https://x.com/thsottiaux/status/2095651088502591861', 'Tibo / @thsottiaux', 'x_screenshot', '等待 Astra 期间的有条件重置补偿原帖'),
 ('astra-launch-embed.png', 'https://x.com/OpenAI/status/2095595741528125780', 'OpenAI', 'official_original', 'Astra 官方发布帖与视频封面'),
 ('skirano-3d-video-preview.jpg', 'https://x.com/skirano/status/2095595932335170031', 'Pietro Schirano / @skirano；输入设计权利人未核', 'x_screenshot', '图片转 3D 模型的原视频预览'),
 ('berman-simcity-video-preview.jpg', 'https://x.com/MatthewBerman/status/2095595893991129444', 'Matthew Berman / @MatthewBerman', 'x_screenshot', '连续运行 5 天仍未结束的模拟城市项目原视频预览'),
]
known = {x['file'] for x in manifest['assets']}
for name, url, owner, kind, desc in specs:
    file = 'assets/'+name
    if file in known:
        continue
    manifest['assets'].append(dict(file=file, used_in_draft=True, visual_route='source_original', source_original_kind=kind, original_pixels_preserved=True, source_type='official_material' if kind=='official_original' else 'social_media', source=desc, source_url=url, creator_or_rightsholder=owner, obtained_on='2026-09-05', modifications='原生公开网页截图，时区 Asia/Shanghai；无内容修改' if name.endswith('.png') else '无修改，下载原视频预览；不是帖子截图', rights_status='pending', allowed_platforms=[], attribution='图源：'+owner, notes='内部草稿引用候选；公开可见不等于取得转载权，发布前确认允许平台。截图无登录、无私人信息；不重绘官推。'))
draft = (ROOT/'draft.md').read_text(encoding='utf-8')
used = set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', draft))
receipts = []
for item in manifest['assets']:
    item['used_in_draft'] = item['file'] in used
    if item['file'] == 'assets/reset-tracker.png':
        item['modifications'] = '真实网页上半部区域截图；保留标题、工具名与预测信号，未改写内容；原页下部有排版重叠，未纳入截图'
    file = ROOT/item['file']
    with Image.open(file) as im:
        width, height = im.size
        im.verify()
    receipts.append(dict(file=item['file'],width=width,height=height,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
class Dumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
(ROOT/'asset-manifest.yml').write_text(yaml.dump(manifest, Dumper=Dumper, allow_unicode=True, sort_keys=False), encoding='utf-8')
(ROOT/'research/source-assets/goldweek-image-receipts.json').write_text(json.dumps(receipts, indent=2)+'\n', encoding='utf-8')
print(f'Images: {len(receipts)}; draft images: {len(used)}; rights remain pending.')
