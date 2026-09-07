from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,html,zipfile
from PIL import Image
root=Path(__file__).resolve().parents[1]
rows=[
 ('agi-time-interview.jpg','TIME 对 Greg Brockman 的 AGI 专访封面','https://www.youtube.com/watch?v=dnSpKF5pWNQ','TIME','采访官方封面原图，未经改动；不冒充发布会现场或本次 AGI 发言发生时的画面。',True),
 ('agi-fable-official-page.png','Anthropic 发布专题首页','https://www.anthropic.com/claude-fable-and-mythos-5-1','Anthropic','官网原生首页截图，含导航、标题、天空与月亮，以及 Made with Fable 5.1 标记。',True),
 ('agi-openai-x-full.png','OpenAI 发布 Astra 的完整 X 帖子','https://x.com/OpenAI/status/2095595741528125780','OpenAI / X','原生嵌入截图，完整保留账号、正文、视频封面、日期与互动栏；显示北京时间。图中的播放按钮属于静态截图。',True),
 ('agi-techrepublic-page.png','TechRepublic 报道标题与配图','https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/','TechRepublic / TechnologyAdvice；配图署名 OpenAI','原网页连续区域截图，保留标题与完整配图，避开广告留白；未改字、重排或拼接。备选，不与采访图堆叠。',False)]
draft=root/'draft.md'
text=draft.read_text(encoding='utf-8')
(root/'research/history/2026-09-05-before-quality-visuals.md').write_text(text,encoding='utf-8')
needle='最近也正好有机会多试一点。Fable 5.1 发布时，ClaudeDevs 宣布重置所有用户的 5 小时和每周用量。[ClaudeDevs 原帖](https://x.com/ClaudeDevs/status/2094856679250919746)'
assert text.count(needle)==1
text=text.replace(needle,needle+'\n\n![Anthropic 的 Fable 5.1 与 Mythos 5.1 官方发布专题](assets/external/agi-fable-official-page.png)\n\n*图源：[Anthropic 官网](https://www.anthropic.com/claude-fable-and-mythos-5-1)，页面右下角标注「Made with Fable 5.1」。*')
text=text.replace('![TechRepublic 报道标题中的 AGI 时代说法](assets/external/agi-media-headline.png)\n\n*图源：TechRepublic，2026 年 9 月 4 日报道标题。*','![Greg Brockman 接受 TIME 的 AGI 专访](assets/external/agi-time-interview.jpg)\n\n*图源：[TIME 对 Greg Brockman 的 AGI 专访](https://www.youtube.com/watch?v=dnSpKF5pWNQ)，官方视频封面。*')
needle='OpenAI 在这次介绍里，专门写到了一个改进：用户中途补充要求或改变方向，Astra 要能接着做原来的任务，保留之前的要求。[OpenAI 发布介绍](https://openai.com/index/gpt-6-astra/)'
assert text.count(needle)==1
text=text.replace(needle,needle+'\n\n![OpenAI 发布 Astra 的完整 X 原帖](assets/external/agi-openai-x-full.png)\n\n*图源：[OpenAI 发布原帖](https://x.com/OpenAI/status/2095595741528125780)。保留官方宣传原文，视频封面为静态截图。*')
draft.write_text(text,encoding='utf-8')
manifest=root/'asset-manifest.yml'
m=manifest.read_text(encoding='utf-8')
receipts=json.loads((root/'research/quality-visual-receipts.json').read_text(encoding='utf-8'))
old={r['file']:r for r in receipts}
records=[]; cards=[]
for name,title,url,owner,note,used in rows:
 rel='assets/external/'+name; path=root/rel
 width,height=Image.open(path).size
 rec=dict(file=rel,title=title,source_url=url,creator_or_rightsholder=owner,notes=note,used_in_draft=used,width=width,height=height,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),accessed_at=datetime.now(timezone.utc).isoformat())
 if rel in old:rec['source_metadata']=old[rel]['detail']
 records.append(rec)
 assert rel not in m
 m+=f'\n  - file: {rel}\n    used_in_draft: {str(used).lower()}\n    visual_route: source_original\n    source_original_kind: community_screenshot\n    original_pixels_preserved: true\n    source_type: public_web\n    source: {title}\n    source_url: {url}\n    creator_or_rightsholder: {owner}\n    obtained_on: "2026-09-05"\n    modifications: {note}\n    rights_status: pending\n    allowed_platforms: []\n    attribution: 图源：{owner}\n    notes: 原始出处与文件指纹见 research/quality-visual-receipts.json；转载权利待核。\n'
 cards.append(f'<figure><figcaption><b>{html.escape(title)}</b><p>{"已放入文章" if used else "备选"} · {width} × {height}</p></figcaption><a href="../{rel}" target="_blank"><img src="../{rel}" alt="{html.escape(title)}"></a><p>{html.escape(note)}</p><a href="{url}" target="_blank">查看原始出处</a> · <a href="../{rel}" download>下载图片</a></figure>')
manifest.write_text(m,encoding='utf-8')
(root/'research/quality-visual-receipts.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
gallery='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>APPSO 配图补充 · 4 张</title><style>body{margin:0;background:#f5f4f0;color:#202020;font:17px/1.7 system-ui}header{max-width:1200px;margin:40px auto;padding:0 24px}h1{font-size:30px}main{max-width:1200px;margin:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;padding:0 24px 48px}figure{margin:0;padding:24px;background:white;border-radius:12px}img{display:block;width:100%;height:auto}figcaption p{color:#777;margin-top:4px}a{color:#be2626}figure>p{font-size:14px;color:#555}@media(max-width:700px){main{grid-template-columns:1fr}}</style><header><h1>这次补充的 4 张配图</h1><p>采访人物图、官方专题页、完整 X 原帖和媒体报道。点击图片可看原尺寸。</p><a href="wechat-preview.html">打开文章预览</a></header><main>'+''.join(cards)+'</main></html>'
(root/'dist/visual-selection.html').write_text(gallery,encoding='utf-8')
with zipfile.ZipFile(root/'dist/quality-visuals.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name,*_ in rows:z.write(root/'assets/external'/name,name)
 z.writestr('sources.json',json.dumps(records,ensure_ascii=False,indent=2))
with (root/'sources.md').open('a',encoding='utf-8') as f:
 f.write('\n\n## FB027｜补充高质量原始配图\n\n')
 for _,title,url,owner,note,_ in rows:f.write(f'- [{title}]({url})，权利人：{owner}。{note}\n')
with (root/'retrospective.md').open('a',encoding='utf-8') as f:
 f.write('\n\n## FB027｜选图质量与上下文完整性\n\n2026-09-05，用户指出配图没有视觉表现力，要求再找 3—4 张，并明确偏好采访图、官网页面、完整 X 原帖和媒体报道截图。仅标题截图缺少人物、场景和来源上下文。本次收集并逐张查看 4 张原始素材；用 TIME 专访人物封面替换旧标题截图，在开头补 Anthropic 官网视觉，在末节补完整 OpenAI 原帖。TechRepublic 标题与配图作为备选，避免末节堆叠。正文判断与跑分单元保持不变。配套原图、出处、权利待核记录和选图页；case_only。\n')
check=root/'research/check_html_preview.py'
s=check.read_text(encoding='utf-8').replace("'TechRepublic 报道标题中的 AGI 时代说法'","'Greg Brockman 接受 TIME 的 AGI 专访', 'OpenAI 发布 Astra 的完整 X 原帖', 'Anthropic 的 Fable 5.1 与 Mythos 5.1 官方发布专题'")
check.write_text(s,encoding='utf-8')
print(json.dumps({'selected':len(rows),'used':sum(r[-1] for r in rows)},ensure_ascii=False))
