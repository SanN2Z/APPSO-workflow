from pathlib import Path
import json

pkg=Path(__file__).resolve().parents[1]
plan_path=pkg/'research/image-generation-plan.json'
plan=json.loads(plan_path.read_text(encoding='utf-8'))
task={
 'id':'cover-001','visual_type':'ai_editorial_creative','visual_route':'clumsy_doodle',
 'purpose':'GPT-6 Astra 公众号实测封面；只表达一个主体关系：巨大的数字 6 从很小的电脑显示器里挤出来，用体积反差表现新模型带来的强烈体验。不是新闻照片，不表示已达 AGI。',
 'reference_strategy':'generated_base',
 'reference_stage':{
  'mode':'text_to_image','prompt_ref':'package-structure-reference-v1',
  'output':'research/source-assets/cover-001-structure.png',
  'receipt':'research/image-generation-runs/cover-001-reference-preflight.json','present_to_user':False,
  'content_prompt':'Create an internal composition reference for a wide cover. One enormous numeral 6 rises out of a tiny desktop monitor. The 6 dominates the central-right area and the monitor is underneath it. Put the exact letters GPT- immediately to the left of the 6 so they read as GPT-6 together. Put the small exact label ASTRA underneath GPT-. No other words. Make the giant 6 red and all other marks black on white. Emphasize the enormous size difference, with a few short impact marks at the edge of the screen. This is only a layout input for a later redraw.',
  'output_constraints':['Wide landscape, aspect ratio 2.35:1, target 2350x1000 pixels.','Keep GPT-6 and the monitor inside the central 78% width and central 80% height.','Exactly one numeral 6, one computer monitor, the labels GPT- and ASTRA; no people, no extra objects.'],
  'avoid':['Real product logos, watermarks, extra labels, real interfaces, numerical performance claims, actual event photography']},
 'final_stage':{
  'mode':'referenced_edit','prompt_ref':'appsso-004','prompt_sha256':'6ba5e092a4f8d6fb2bd33602424ba4792715aa59f2bf5f916b90d8bb3f0bbd0a',
  'input_assets':['research/source-assets/cover-001-structure.png'],
  'output':'assets/cover-gpt6-doodle-v01.png',
  'receipt':'research/image-generation-runs/cover-001-final-preflight.json','present_to_user':True,
  'preserve':['本图只画：一个巨大的红色数字 6 从一台很小的电脑屏幕里挤出来；表现新模型带来的强烈体感，不表示 AGI 已实现。','保留一个数字 6、一台小电脑，以及左侧 GPT- 和 ASTRA 两组文字。GPT- 与数字 6 合起来读作 GPT-6。','参考图只决定主体关系与文字，最终线条、填色和轮廓全部服从固定笨拙涂鸦风格。'],
  'output_constraints':['横向 2.35:1，目标 2350×1000 像素；主要内容留在中央 78% 宽、80% 高的范围内。','纯白底、黑色粗鼠标线，数字 6 用大块红色胡乱填色；红色边缘允许出界、缺口和锯齿。','用很大的数字和很小的电脑制造强烈反差，数字占画面高度约 75%，字体和轮廓笨拙但 GPT-6 一眼可读。','少量短冲击线、歪斜边框和潦草涂抹即可；不要用细碎装饰填满留白。','只出现 GPT-6 和 ASTRA，不加宣传标语、跑分、日期或 AGI 判断。'],
  'avoid':['Gradients, glossy surfaces, cinematic lighting, realistic rendering, extra people, fake screenshots, additional logos, watermarks, illegible labels']}
}
assert not any(t['id']==task['id'] for t in plan['tasks']), 'Cover task already exists'
plan['tasks'].append(task)
plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Added cover-001')
