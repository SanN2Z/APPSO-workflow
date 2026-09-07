from pathlib import Path
import copy, json, shutil

root = Path(__file__).resolve().parents[1]
shutil.copyfile(Path(r'C:\Users\22684\.codex-company\generated_images\01a06eac-ee34-7ea1-b4e6-174267c72f61\exec-42bfbaa9-a4f3-40cc-9543-c71f58162e77.png'), root/'assets/infographic-001-image2.png')
path = root/'research/image-generation-plan.json'
plan = json.loads(path.read_text(encoding='utf-8'))
task = copy.deepcopy(plan['tasks'][0])
task['id'] = 'infographic-002'
task['purpose'] = '区分官方发布重点、独立机构评测与产品公司的自有评测，呈现 Astra 和 Fable 5.1 的不同结果。'
stage = task['final_stage']
stage['output'] = 'assets/infographic-002-image2.png'
stage['receipt'] = 'research/image-generation-runs/infographic-002-final-preflight.json'
stage['preserve'] = [
 '标题「官方怎么说，机构怎么测」，副标题「Astra × Fable 5.1」。全图仅一个核心逻辑：来源不同，考察的能力与条件不同。',
 '顶部区域标签「官方发布重点｜核对于 09.05」。下分左右两栏。左栏「OpenAI · Astra」，正文「操作电脑、专业交付」「强调视觉判断与模板适配」。右栏「Anthropic · Fable 5.1」，正文「编程、知识工作、长任务」「强调自检与降低缓存成本」。这些是厂商介绍，不是独立测评结论。',
 '中部第一块标签「Artificial Analysis｜独立评测 · 09.03」。副标题「Coding Agent Index」。左右并列显示「Astra 67」「Codex」以及「Fable 5.1 70」「Claude Code」。这一块只展示两个数字，不使用百分号。块底注释「模型与运行环境一起测，不能只归因于模型」。',
 '中部第二块标签「Cognition｜产品公司自测 · 09.03」。副标题「FrontierCode 1.1」。大字结果「Astra 高于 Fable 5.1」。块底注释「看工程质量与可合并性，采用自有评分」。不得编造分数，不要给此处画可量化长度的柱状图。',
 '底部观点区标签「APPSO 怎么看」，正文「榜单可供选题参考」「审美与操作，还得放进自己的项目试」。这个观点是本刊判断，不是任何机构的原话。',
 '页脚使用给定红底白字 APPSO Logo，保留原始比例、独立圆点与完整字形。注明「来源：OpenAI / Anthropic / Artificial Analysis / Cognition」「整理：2026.09.05 · AI 辅助制图」。不要画机构 Logo，名称用正常文字。'
]
stage['output_constraints'] = stage['output_constraints'][:4] + [
 '1080×1440 竖版，暖白底、白色分区、细灰线、少量品牌红。正文保持大字，减少装饰，适合公众号手机阅读。',
 '这是编辑整理图，不是官方截图；不得伪造网页、引用框截图、榜单页面或被测模型的作品。',
 '四个来源必须写清楚：两个官方、一家独立评测机构、一家产品公司自测。官方发布重点与外部测试结果在视觉上分组，不能合成综合冠军榜。',
 '67 与 70 仅属于 2026 年 9 月 3 日发布的 Coding Agent Index 结果。不要出现 Intelligence Index、v4.2、百分号、未提供的胜率、性能倍率或价格。',
 '所有上面指定中文、英文名称、数字、日期准确清楚。控制整图字数，取消多余装饰文字。'
]
plan['tasks'] = [x for x in plan['tasks'] if x['id'] != task['id']] + [task]
path.write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Saved approved practical comparison and prepared external comparison task')
