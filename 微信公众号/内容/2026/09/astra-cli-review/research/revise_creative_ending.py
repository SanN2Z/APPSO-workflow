from pathlib import Path
import json, re

root=Path(__file__).resolve().parents[1]
path=root/'draft.md'
before=path.read_text(encoding='utf-8')
history=root/'research/history/2026-09-05-before-creative-ending.md'
if not history.exists(): history.write_text(before,encoding='utf-8')
start=before.index('## 跑分和费用，放在一起看')
end=before.index('<!-- 编辑待办',start)
ending='''回到跑分表现上，APPSO 特意整理了六个维度的指标，把 Astra 和 Fable 5.1 放在一起对比一下。

![APPSO 跑分对照：OpenAI 发布页中的 Astra 与 Fable 5.1 六项成绩](assets/infographic-004-image2.png)

*APPSO 整理，AI 辅助制图。[数据来自 OpenAI 发布页](https://openai.com/index/gpt-6-astra/)，截至 2026 年 9 月 5 日。各项取不同推理档位下的最高成绩，测试环境可能与实际产品不同。*

X 上的 Anshu 给 Astra 多安排了一步：先画概念图。

他分享的做法是把 Codex 接到 3D 软件 Blender，再让 Astra 用生图工具画出想要的美术风格。开发过程中，他要求它反复对照游戏截图和概念图，把画面往选定的风格上改。[Anshu 的做法](https://x.com/anshuc/status/2096008086901113339)

![Anshu 展示的 AFTERLIGHT 游戏场景](assets/external/anshu-concept-game.jpg)

*图源：@anshuc / X，游戏演示的原视频封面。*

下次做小妖这样的题，我想先看几版鬼门关的概念图。灯光和配色选好了，再让它搭关卡。

Paul Solt 也在对着概念图调像素风水面，折腾波浪和水上的闪光。随后，他在帖子下面更新了一条反馈。[水面效果原帖](https://x.com/PaulSolt/status/2095970470390530453)

![Paul Solt 分享妻子对画面效果的反馈](assets/external/paul-visual-feedback.png)

*图源：@PaulSolt / X，原帖截图。*

「我妻子觉得还得再好看一点……」

他接着写：「还得接着改。」[Paul 原帖，译文](https://x.com/PaulSolt/status/2096023238081908917)

'''
path.write_text(before[:start]+ending+before[end:],encoding='utf-8')

manifest=root/'asset-manifest.yml'
raw=manifest.read_text(encoding='utf-8')
records=json.loads((root/'research/creative-ending-sources.json').read_text(encoding='utf-8'))
for row in records:
    file=row['file']
    if f'  - file: {file}\n' in raw: continue
    author=row['post']['user']['name']+' / @'+row['post']['user']['screen_name']
    url=row.get('media_source_url',row['source_url'])
    raw+=f'''  - file: {file}
    used_in_draft: true
    visual_route: source_original
    source_original_kind: community_screenshot
    original_pixels_preserved: true
    source_type: public_web
    source: X 公开原帖及原生媒体
    source_url: {url}
    creator_or_rightsholder: {author}
    obtained_on: "2026-09-05"
    modifications: {row['modifications']}
    rights_status: pending
    allowed_platforms: []
    attribution: 图源：{author} / X
    notes: 原文与父帖上下文、素材指纹见 research/creative-ending-sources.json；不是 APPSO 亲测；转载权利待核。
'''
def update_usage(m):
    block=m.group(0)
    file=re.search(r'file: (.+)',block).group(1).strip()
    return re.sub(r'used_in_draft: (true|false)','used_in_draft: '+str(f']({file})' in before[:start]+ending+before[end:]).lower(),block)
manifest.write_text(re.sub(r'  - file:.*?(?=  - file:|\Z)',update_usage,raw,flags=re.S),encoding='utf-8')

check=root/'research/check_html_preview.py'
code=check.read_text(encoding='utf-8')
code=code.replace('Artificial Analysis 发布的综合智能与编程智能体排名原图','Anshu 展示的 AFTERLIGHT 游戏场景')
code=code.replace('Artificial Analysis 编程智能体得分与单任务 API 成本原图','Paul Solt 分享妻子对画面效果的反馈')
check.write_text(code,encoding='utf-8')

evidence='''# FB024｜从跑分转向审美怎么改

日期：2026-09-05。用户锁定引入句，只调整中英文空格：回到跑分表现上，APPSO 特意整理了六个维度的指标，把 Astra 和 Fable 5.1 放在一起对比一下。

本篇不再铺开性能、费用和档位分析。保留六项信息图及必要图源条件，移除两张 AA 图和 Cognition 段落。上一篇已经覆盖性能、3D 演示与接管电脑；本篇新增的是创作流程中选风格、对图修改以及真实使用者的审美反馈。

- Anshu：https://x.com/anshuc/status/2096008086901113339 。公开 X syndication 返回本人原文与父帖；明确先连 Codex 到 Blender MCP，贴游戏概念，用 image gen 生成目标风格概念图，要求游戏截图迭代接近概念图。原帖的 60fps 是要求，不作为实测成绩；本文不写 45 分钟、额度百分比或 AGI 宣称。父帖 2096008083826725132 的原视频封面可见 AFTERLIGHT、雨后院落和角色；只标演示封面，不说它是概念图，不声称 APPSO 试玩过。
- Paul Solt：https://x.com/PaulSolt/status/2096023238081908917 。公开 X 返回原文「My wife thinks it needs to look a little better… / More tweaking to do」，及父帖 2095970470390530453。父帖说正让像素风波浪、闪光匹配概念图。正文译文归属于 Paul 的转述，不把妻子的话伪装成采访。两条原帖未明确模型，正文不擅自称它为 Astra 生成结果。原生嵌入截图仅截回复作者、全文和日期，父帖上下文保存在 JSON。屏幕日期按北京时间，与 UTC 原时间分开。
- 作者下一轮先看概念图的意向：编辑提议，未声称本次已经测试；沿既有小妖题作具体延续。

核对与素材回执：creative-ending-sources.json。X 网页直接返回 403 时，通过 X 自己的公开 syndication 数据核对；镜像仅用于发现帖子 ID。Reddit 和其他搜索结果未进入正文。

局部冷读：正文仍从本人实测推进；新段的增量是具体图像参照流程。结尾落在真实反馈，没有再加「这说明」「未来」「不是而是」总结。保留普通词和原有段落，未动前文实测与模型归属。来源权利仍 pending，草稿状态不变。
'''
(root/'research/creative-ending-evidence.md').write_text(evidence,encoding='utf-8')
note='\n\n## FB024｜用户锁定跑分引入，结尾不再列性能\n\n用户反馈：上篇已写具体性能；本篇跑分仅保留用户引入句和信息图，要求其他信息增量、轻松对话感。局部合同：新结尾用 Anshu 的概念图参照流程和 Paul 的原帖反馈，接实测审美问题。删去 AA 图、费用和 Cognition 性能说明。原有实测、作者偏好、图序保留。新结尾的具体事实/图片与逐条限制见 research/creative-ending-evidence.md。用户句为 locked；新结尾待审，case_only。\n'
for name in ['retrospective.md','research/co-writing-log.md','research/differentiation.md']:
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
with (root/'sources.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## 当前结尾来源｜FB024\n\n用户撤下性能与费用展开，只保留六项信息图。新增 Anshu 概念图流程与 Paul 原帖反馈，原始链接、上下文和限制见 [creative-ending-evidence.md](research/creative-ending-evidence.md)。上文旧成本结尾记录仅作历史。\n')
print('Updated ending: user introduction + benchmark infographic + concept-art workflow and actual feedback. Prior sections retained.')
