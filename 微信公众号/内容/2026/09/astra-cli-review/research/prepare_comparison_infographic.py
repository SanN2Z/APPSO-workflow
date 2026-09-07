from pathlib import Path
import json, shutil, yaml

root=Path(__file__).resolve().parents[1]
repo=root.parents[4]
plan=json.loads((repo/'APPSO-数字资产/04-模板/APPSO 生图计划模板.json').read_text(encoding='utf-8'))
plan['template_only']=False
plan['updated']='2026-09-05'
task=next(x for x in plan['tasks'] if x['id']=='infographic-001')
plan['tasks']=[task]
task['purpose']='用同一组实际任务比较 Astra 与 Fable 5.1 的画面和操作，呈现作者判断及未验证边界；不做综合跑分榜。'
task['final_stage']['preserve']=[
  '唯一主逻辑是两模型在三道创作任务中的可见差异。标题必须为「这几道题，我们怎么看」，副标题「Astra × Fable 5.1｜APPSO 实测观察」。',
  '用三行任务、两列模型呈现比较。列名精确为「Astra」「Fable 5.1」。不要胜负奖杯、打分条或虚构星级。',
  '第一行标题「唱片店」。Astra 单元格「信息醒目，页面明亮」；Fable 5.1 单元格「封面贴题，氛围更浓」。行下结论「封面更喜欢 Fable，小字偏暗」。',
  '第二行标题「自由审美」。Astra 单元格「月屿：海面、天色可调」；Fable 5.1 单元格「节气：留白好，日期重复」。行下结论「动态对比还缺 Fable 录屏」。',
  '第三行标题「小妖快跑」。Astra 单元格「对照画面待补」；Fable 5.1 单元格「画面更精美，方向疑似反转」。行下结论「画面评价来自作者试玩感受」。',
  '页脚精确文字「依据：本次截图、录屏与作者反馈」「非综合排名｜2026.09.05」「AI 辅助制图」。页脚左侧保留给定 APPSO 红底白字 Logo 的原始比例、字形和独立圆点，作为品牌署名；不要生成第二个额外 Logo。'
]
task['final_stage']['output_constraints'] += [
  '三行双列的轻量编辑比较图；可用小唱片、海浪与节气刻度、灯笼的小图标辅助识别，不画伪造游戏截图。',
  '在 1080×1440 画布上把主要中文文字控制为实际 36–46 px 等效大小，标题 64–76 px；字数少、留白充分，缩至 390 px 宽仍可读。',
  '不要将 Fable 的画面偏好泛化成更强编程能力；「待补」「疑似」必须清楚保留。'
]
task['final_stage']['output_constraints'] += [
  'CRITICAL REVISION: 此图严格为文字比较表，不得画任何唱片封面、商店外观、海面风景、网页界面、节气日期表或小妖角色。不能把本次实测没出现的画面画成两个模型的结果。六个比较单元格只放上面规定的文字，背景纯白。',
  '仅允许在最左边的任务名称旁加极小的抽象单色线性图标：唱片圆环、波浪线、灯笼轮廓。三种图标同一风格。没有图片占位符，没有卡片内插图，没有英文装饰词，没有虚构数字或日期。',
  '整图以大字、分组、留白和细线形成清楚的比较关系。除页脚标志外，不再使用第二个图像参考。'
]
(root/'research/image-generation-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
relative='research/source-assets/appsso-logo-red-background.png'
shutil.copyfile(root/'assets/appso-logo-input.png',root/relative)
manifest=root/'asset-manifest.yml'
raw=manifest.read_text(encoding='utf-8')
if f'file: {relative}\n' not in raw:
    entry=[dict(file=relative,used_in_draft=False,use='research_reference',visual_route='source_original',
                source_original_kind='official_original',original_pixels_preserved=True,source_type='user_provided',
                source='作者本轮提供的 APPSO Logo，与登记品牌原件 SHA256 一致',source_url='user_attachment://2026-09-05/appso-logo',
                creator_or_rightsholder='APPSO / 爱范儿',obtained_on='2026-09-05',modifications='原字节复制，无修改',
                rights_status='user_confirmed_derivative_use',allowed_platforms=['wechat'],
                notes='用户本轮明确要求使用所附 Logo 制作本篇 APPSO 信息图。授权限此公司稿的信息图。')]
    raw+=''.join('  '+line+'\n' for line in yaml.safe_dump(entry,allow_unicode=True,sort_keys=False,width=100000).splitlines())
    manifest.write_text(raw,encoding='utf-8')
print('Comparison infographic plan and authorized Logo reference prepared')
