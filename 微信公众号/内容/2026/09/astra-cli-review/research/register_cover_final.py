from pathlib import Path
import copy
import json
import yaml
from PIL import Image

class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

pkg = Path(__file__).resolve().parents[1]
path = pkg / 'asset-manifest.yml'
manifest = yaml.safe_load(path.read_text(encoding='utf-8'))
asset = copy.deepcopy(next(a for a in manifest['assets'] if a.get('file') == 'assets/cover-gpt6-doodle-v01.png'))
asset.update(file='assets/cover-gpt6-doodle-v02.png',
    preflight_receipt='research/image-generation-runs/cover-002-final-preflight.json',
    modifications='以第一版为参考调整构图留白，保持黑白红笨拙涂鸦。',
    attribution='APPSO · AI 生成封面',
    notes='本次交付候选；不是官网截图。保留 GPT-6、ASTRA 和巨大数字与电脑的比例反差。未绑定发布封面。')
if not any(a.get('file') == asset['file'] for a in manifest['assets']):
    manifest['assets'].append(asset)
for item in manifest['assets']:
    if not str(item.get('preflight_receipt', '')).startswith('research/image-generation-runs/cover-'):
        continue
    receipt = json.loads((pkg / item['preflight_receipt']).read_text(encoding='utf-8'))
    for key in ('prompt_sha256', 'invocation_prompt_sha256', 'input_assets'):
        item[key] = receipt[key]
    item['generated_on'] = '2026-09-05'
    item['visual_route'] = 'clumsy_doodle'
    item.setdefault('attribution', '本项目 AI 生成图')
    item['generation_constraints'] = '一个巨大红色数字 6 与小电脑；GPT-6 和 ASTRA 文字；黑白红横向构图；不含跑分或 AGI 断言。'
path.write_text(yaml.dump(manifest, Dumper=IndentedDumper, allow_unicode=True, sort_keys=False, width=100000), encoding='utf-8')
im = Image.open(pkg / asset['file'])
record = {'file':asset['file'], 'size':list(im.size), 'bytes':(pkg / asset['file']).stat().st_size,
    'ai_generated':True, 'visual_review':'GPT-6 / ASTRA 可读；主体完整；黑白红涂鸦；没有虚构跑分或新闻画面。',
    'crop_review':'横图原生比例约 2.35:1；上下已增加留白。方形裁切需另选裁切区域。',
    'selection':'candidate_not_bound', 'official_reference':'https://openai.com/index/gpt-6-astra/'}
(pkg / 'research/cover-delivery.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
