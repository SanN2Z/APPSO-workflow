from pathlib import Path
import json, copy

root = Path(__file__).resolve().parents[1]
path = root / 'research/image-generation-plan.json'
plan = json.loads(path.read_text(encoding='utf-8-sig'))
task = copy.deepcopy(plan['tasks'][1])
task['id'] = 'infographic-004'
task['purpose'] = '将正文六项已核 OpenAI 发布页跑分制作成 APPSO 信息图，保持各项指标单位与版本，不推导综合胜负。'
stage = task['final_stage']
stage['output'] = 'assets/infographic-004-image2.png'
stage['receipt'] = 'research/image-generation-runs/infographic-004-final-preflight.json'
stage['preserve'] = [
    '标题「Astra 与 Fable 5.1」；第二行「六项跑分对照」。副标题「OpenAI 发布页数据｜越高越好」。',
    '用六张横向白色卡片纵向排列。每张上面为中文指标与较小英文全名版本，下面为并列的 Astra 和 Fable 5.1 两个大数字。每行两列模型顺序固定，不得对调。可以在表头标两列模型名。',
    '第 1 行：终端任务；Terminal-Bench 4.0；Astra 57.9%；Fable 5.1 55.8%。',
    '第 2 行：软件工程；DeepSWE v1.1；Astra 74.1%；Fable 5.1 67.4%。',
    '第 3 行：科研工作流；Terminal-Bench Science 0.1；Astra 64.6%；Fable 5.1 52.6%。',
    '第 4 行：高难数学；FrontierMath Tier 4 (v2)；Astra 97.6%；Fable 5.1 87.8%。',
    '第 5 行：HLE（带工具）；Humanity’s Last Exam；Astra 57.2%；Fable 5.1 65.0%。',
    '第 6 行：AA 综合智能指数；Artificial Analysis v4.1.1；Astra 61.2；Fable 5.1 65.7。此行必须注明「指数分」，两个数字都不带百分号。',
    '页脚保留给定 APPSO Logo 原比例、完整字形与独立圆点；文字「APPSO 整理 · AI 辅助制图」「来源：OpenAI 发布页」「截至 2026.09.05」。'
]
stage['output_constraints'] = [
    '1080 x 1440 px vertical canvas with safe areas, typography floors, color ratios, footer rules from governed specification; warm white background and white cards.',
    'Use provided APPSO red-background white-wordmark proportionally as footer branding. No other logos.',
    'One comparison logic only. Twelve exact numbers and versions must remain legible at mobile width. No decorative illustrations or invented scores.',
    'Each row higher number in brand red, lower in dark neutral. Astra highlighted in first four rows, Fable 5.1 in last two rows. No aggregate winner.',
    'Use big number comparison cards without bars or axes. This avoids mixing index points and percentage scales. Keep English version labels secondary but readable.',
    'This is an APPSO editorial infographic based on vendor-reported results, not an official screenshot. Do not imply APPSO or independent institutions reproduced the scores.',
    'CRITICAL: Both model column HEADERS must be BLACK. In rows 5 and 6, 57.2% and 61.2 MUST BE BLACK, while 65.0% and 65.7 MUST BE RED. Red means higher within each row, never a fixed model identity. First four rows retain red Astra numbers and black Fable numbers. Check this before delivery.'
]
plan['tasks'] = [t for t in plan['tasks'] if t['id'] != task['id']] + [task]
path.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Prepared infographic-004; previous tasks preserved.')
