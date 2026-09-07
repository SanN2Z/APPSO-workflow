from pathlib import Path
from PIL import Image
import json, re, shutil, hashlib

root = Path(__file__).resolve().parents[1]
target = root / 'assets/infographic-004-image2.png'
shutil.copyfile(Path(r'C:\Users\22684\.codex-company\generated_images\01a06eac-ee34-7ea1-b4e6-174267c72f61\exec-fdfdbbe4-2af5-4a2b-ab69-4025e67005ed.png'), target)
draft = root / 'draft.md'
text = draft.read_text(encoding='utf-8')
start = text.index('| 评测 | Astra | Fable 5.1 |')
end = text.index('\n\n这六项里', start)
text = text[:start] + '![APPSO 跑分对照：OpenAI 发布页中的 Astra 与 Fable 5.1 六项成绩](assets/infographic-004-image2.png)\n\n*APPSO 整理，AI 辅助制图。数据截至 2026 年 9 月 5 日。OpenAI 原页说明成绩取各推理强度下的最高值，研究环境与实际产品的工具、系统提示等可能不同。*' + text[end:]
text = text.replace('所以不算谁更省订阅。\n\n接下来再做活动页', '所以不算谁更省订阅。接下来再做活动页')
draft.write_text(text, encoding='utf-8')

receipt = 'research/image-generation-runs/infographic-004-final-preflight.json'
preflight = json.loads((root / receipt).read_text(encoding='utf-8'))
manifest = root / 'asset-manifest.yml'
raw = manifest.read_text(encoding='utf-8')
old = re.search(r'  - file: assets/infographic-003-image2.png\n.*?(?=  - file:|\Z)', raw, re.S).group(0)
new = old.replace('infographic-003', 'infographic-004')
new = new.replace('本文已核事实与作者实测反馈，经 APPSO 规范整理生成', 'https://openai.com/index/gpt-6-astra/')
new = re.sub(r'    input_assets: .*', '    input_assets: [research/source-assets/appsso-logo-red-background.png]', new)
new = re.sub(r'    invocation_prompt_sha256: .*', '    invocation_prompt_sha256: '+preflight['invocation_prompt_sha256'], new)
new = re.sub(r'    generation_constraints: .*', '    generation_constraints: 六项原始数据与版本逐项保留；前五项为百分比，末行为指数分；每行较高数字标红；标明厂商发布页数据与 AI 制图', new)
manifest.write_text(raw+new, encoding='utf-8')

with Image.open(target) as im:
    record = dict(file=target.relative_to(root).as_posix(), width=im.width, height=im.height,
                  bytes=target.stat().st_size, sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  preflight_receipt=receipt, review='12 个数字、5 行百分号、末行指数单位、6 项名称版本、模型列顺序、日期与来源逐项视觉核对通过；前四行 Astra 标红，末两行 Fable 标红。')
delivery = root / 'research/infographic-delivery.json'
data = json.loads(delivery.read_text(encoding='utf-8'))
data['assets'].append(record)
data['latest_correction'] = 'FB021：将正文六项跑分表替换为 APPSO 信息图；保留 AA 原图；结尾两段合并。'
delivery.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

check = root / 'research/check_html_preview.py'
code = check.read_text(encoding='utf-8')
code = code.replace("    assert table.count()==1\n    table.scroll_into_view_if_needed()\n    table.screenshot(path=str(dist/'preview-official-benchmark-table.png'))", "    assert table.count()==0\n    benchmark=page.locator('#phone-preview img[alt=\"APPSO 跑分对照：OpenAI 发布页中的 Astra 与 Fable 5.1 六项成绩\"]')\n    assert benchmark.count()==1\n    benchmark.scroll_into_view_if_needed()\n    benchmark.screenshot(path=str(dist/'preview-benchmark-infographic-mobile.png'))")
check.write_text(code, encoding='utf-8')
for name in ['retrospective.md', 'research/co-writing-log.md', 'research/visual-notes.md']:
    with (root/name).open('a',encoding='utf-8') as f:
        f.write('\n\n## FB021｜六项跑分信息图与结尾合段\n\n用户要求将六项表格做成信息图，并合并最后两段。按既有 APPSO 完整规范与 Logo 生成 infographic-004，替换正文表格；12 个数值、指标版本和单位逐项核对，较高值按行标红。保留两张 AA 原图。结尾仅去掉两段之间空行，句子与判断不改。本次 case_only，不增加 SOP。\n')
print(json.dumps(record, ensure_ascii=False))
