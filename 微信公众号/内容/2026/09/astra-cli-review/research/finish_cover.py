from pathlib import Path
import copy
import json
import yaml

class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

pkg = Path(__file__).resolve().parents[1]
manifest_path = pkg / 'asset-manifest.yml'
manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8'))
receipt = json.loads((pkg / 'research/image-generation-runs/cover-001-final-preflight.json').read_text(encoding='utf-8'))
asset = {
    'file': 'assets/cover-gpt6-doodle-v01.png',
    'used_in_draft': False, 'used_as_cover': False, 'use': 'unused',
    'source_type': 'ai_generated', 'visual_route': 'clumsy_doodle',
    'source': '本项目 Image2 生成的 GPT-6 Astra 封面候选；不是官方图片。',
    'creator_or_rightsholder': '本项目 / AI-generated', 'obtained_on': '2026-09-05', 'generator': 'Codex built-in image_gen',
    'model': 'gpt-image-2', 'generation_mode': 'referenced_edit',
    'prompt_ref': receipt['prompt_ref'], 'prompt_sha256': receipt['prompt_sha256'],
    'preflight_receipt': receipt['receipt'],
    'rights_status': 'project_owned', 'derivative_rights_confirmed': True,
    'allowed_platforms': ['wechat'],
    'modifications': '将内部构图参考按 APPSO 笨拙涂鸦风格重绘。',
    'notes': 'AI 生成封面候选。第一版上下留白偏紧，继续调整裁切余量。',
}
if not any(a.get('file') == asset['file'] for a in manifest['assets']):
    manifest['assets'].append(asset)
manifest['assets'] = [asset if a.get('file') == asset['file'] else a for a in manifest['assets']]
manifest_path.write_text(yaml.dump(manifest, Dumper=IndentedDumper, allow_unicode=True, sort_keys=False, width=100000), encoding='utf-8')
plan_path = pkg / 'research/image-generation-plan.json'
plan = json.loads(plan_path.read_text(encoding='utf-8'))
task = copy.deepcopy(next(t for t in plan['tasks'] if t['id'] == 'cover-001'))
task['id'] = 'cover-002'
task['reference_strategy'] = 'provided_local'
task.pop('reference_stage', None)
stage = task['final_stage']
stage['input_assets'] = [asset['file']]
stage['output'] = 'assets/cover-gpt6-doodle-v02.png'
stage['receipt'] = 'research/image-generation-runs/cover-002-final-preflight.json'
stage['output_constraints'].append('本轮只调整构图安全边距：把参考图全部可见笔画作为一个整体缩小至原来的 80%，放在同样比例白色画布中央。最高红色笔画上方和电脑底座下方各保留至少画布高度 10% 的纯白空间。保留原来的相对位置、涂鸦质感、文字和颜色。数字仍远大于电脑，但不能贴边。')
if not any(t['id'] == task['id'] for t in plan['tasks']):
    plan['tasks'].append(task)
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Registered V01 and prepared margin revision.')
