from pathlib import Path
import hashlib, json
from PIL import Image

root = Path(__file__).resolve().parents[1]
manifest = root/'asset-manifest.yml'
raw = manifest.read_text(encoding='utf-8')
records=[]
for n in [1,2]:
    task=f'infographic-{n:03d}'
    file=f'assets/{task}-image2.png'
    receipt=f'research/image-generation-runs/{task}-final-preflight.json'
    invocation=json.loads((root/receipt).read_text(encoding='utf-8'))['invocation_prompt_sha256']
    if f'file: {file}\n' not in raw:
        raw+=f'''  - file: {file}
    used_in_draft: true
    visual_route: infographic
    source_type: ai_generated
    source: 本文已核事实与作者实测反馈，经 APPSO 规范整理生成
    creator_or_rightsholder: APPSO / 爱范儿
    obtained_on: "2026-09-05"
    modifications: Image2 依据完整登记规范与作者提供的 Logo 生成；未重绘实测作品
    rights_status: project_owned
    allowed_platforms: [wechat]
    attribution: APPSO 整理，AI 辅助制图
    generator: imagegen
    model: gpt-image-2
    generation_mode: referenced_edit
    prompt_ref: appsso-infographic-v1
    prompt_sha256: c8c191665a99da9af14f8ba84b0f7ef769cbadefe347f5d197635264b024c043
    generation_constraints: 完整规范与登记 Logo 输入；事实、厂商自报、第三方结果、作者判断和待验证项分开；不伪造作品
    input_assets: [research/source-assets/appsso-logo-red-background.png]
    generated_on: "2026-09-05"
    preflight_receipt: {receipt}
    invocation_prompt_sha256: {invocation}
    notes: 仅用于本篇 APPSO 公司稿；Logo 衍生使用由本轮用户明确授权。正文与图内均标注 AI。
'''
    elif f'preflight_receipt: {receipt}\n    invocation_prompt_sha256:' not in raw:
        raw=raw.replace(f'preflight_receipt: {receipt}\n',f'preflight_receipt: {receipt}\n    invocation_prompt_sha256: {invocation}\n')
    with Image.open(root/file) as im:
        im.verify()
    with Image.open(root/file) as im:
        records.append(dict(file=file,width=im.width,height=im.height,bytes=(root/file).stat().st_size,
          sha256=hashlib.file_digest((root/file).open('rb'),'sha256').hexdigest(),preflight_receipt=receipt))
raw=raw.replace('source_url: user_attachment://2026-09-05/appso-logo\n','source_url: user_attachment://2026-09-05/appso-logo\n    attribution: APPSO / 爱范儿，用户提供\n') if 'attribution: APPSO / 爱范儿，用户提供' not in raw else raw
manifest.write_text(raw,encoding='utf-8')
# An unused local first draft was rejected for invented illustrative model outputs.
# Keep the generation service's original; remove only our disposable package copy.
rejected=(root/'research/source-assets/comparison-infographic-r1.png').resolve()
assert rejected.is_relative_to(root.resolve())
if rejected.is_file(): rejected.unlink()
(root/'research/infographic-delivery.json').write_text(json.dumps(dict(assets=records,
  review='逐字检查通过；实测图未将画面偏好写成综合排名；机构图的 67/70、测试环境和自测标签与原文一致。',
  rejected_first_draft='第一版含非实测作品示意，未用于正文；改为文字比较。',
  original_rules_match_user_file=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
