from pathlib import Path
import re, json

root=Path(__file__).resolve().parents[1]
path=root/'draft.md'
before=path.read_text(encoding='utf-8')
snapshot=root/'research/history/2026-09-05-before-agi-ending.md'
if not snapshot.exists():snapshot.write_text(before,encoding='utf-8')
start=before.index('## 做出来之后，能不能接着改')
end=before.index('<!-- 编辑待办',start)
ending='''## 这就到 AGI 了吗？

这次发布，OpenAI 已经开始谈 AGI，也就是通用人工智能。总裁 Greg Brockman 表示，他个人认为已经到了这个阶段。TechRepublic 也把「AGI 时代」放进了报道标题。[相关报道](https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/)

![TechRepublic 报道标题中的 AGI 时代说法](assets/external/agi-media-headline.png)

*图源：TechRepublic，2026 年 9 月 4 日报道标题。*

我还不急着点头。做出这几个网页和小游戏，确实有惊喜，但这轮体验还撑不起那么大的结论。

画面喜欢哪一版、操作哪里不对，还是得我们自己上手判断。以后再加一关、换一个要求，它能不能接着做好，也要继续试。

OpenAI 在这次介绍里，专门写到了一个改进：用户中途补充要求或改变方向，Astra 要能接着做原来的任务，保留之前的要求。[OpenAI 发布介绍](https://openai.com/index/gpt-6-astra/)

这也是我想接着用下去的地方。初稿看过了，后面说一句「这关不好玩」，它能不能理解我的意思，改出让我愿意再玩一局的版本？

我对下一次更新的愿望倒是很具体：画面继续好看，修改时少让我来回解释。这样，做自己的小游戏，也能多留点时间给自己玩。

'''
after=before[:start]+ending+before[end:]
path.write_text(after,encoding='utf-8')

manifest=root/'asset-manifest.yml'
raw=manifest.read_text(encoding='utf-8')
if '  - file: assets/external/agi-media-headline.png\n' not in raw:
    raw+='''  - file: assets/external/agi-media-headline.png
    used_in_draft: true
    visual_route: source_original
    source_original_kind: community_screenshot
    original_pixels_preserved: true
    source_type: public_web
    source: TechRepublic 原始报道标题
    source_url: https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/
    creator_or_rightsholder: TechRepublic / TechnologyAdvice
    obtained_on: "2026-09-05"
    modifications: 原生网页 h1 元素截图；未改字、重绘或拼接
    rights_status: pending
    allowed_platforms: []
    attribution: 图源：TechRepublic，2026 年 9 月 4 日
    notes: 报道标题转述 Brockman 判断，不写成媒体独立认证 AGI；原始标题与指纹见 research/agi-headline-receipt.json。
'''
def usage(m):
    block=m.group(0)
    file=re.search(r'file: (.+)',block).group(1).strip()
    return re.sub(r'used_in_draft: (true|false)','used_in_draft: '+str(f']({file})' in after).lower(),block)
manifest.write_text(re.sub(r'  - file:.*?(?=  - file:|\Z)',usage,raw,flags=re.S),encoding='utf-8')

check=root/'research/check_html_preview.py'
code=check.read_text(encoding='utf-8')
code=code.replace("'Anshu 展示的 AFTERLIGHT 游戏场景',\n                           'Paul Solt 分享妻子对画面效果的反馈'", "'TechRepublic 报道标题中的 AGI 时代说法'")
check.write_text(code,encoding='utf-8')

note='''

## FB026｜重写整个末节，转向 AGI 宣传与普通用户体验

2026-09-05，用户先指出末节仍在罗列测试案例，要求整节重写且不做技术稿；随后提出以官方/媒体 AGI 叙事与自身趣味体验对照，持保留态度，也看到持续改进。以用户最新方向为本次局部合同。之前自行提出的个人小软件角度仅调研，未写入正文。

替换整个「做出来之后，能不能接着改」小节，撤下 Berman 模拟城市、Riley 射击、Anshu 概念图、Paul 妻子反馈四组案例与四张图；保留前文实测、作者锁定跑分引入及信息图。新末节只写 AGI 说法、本文不能据几次趣味测试下定论、官方正在改进接续需求的表现、作者对后续使用的普通期待。用真实媒体标题配图，不回到榜单、技术流程或案例清单。

链：看过自己的成品 → 接触官方 AGI 判断 → 作者暂不跟随下结论 → 看它能否持续接住修改 → 对下一次更新的具体期待。最强反例：人参与或一次失误均不能证明非 AGI；因此未作否定证明，也未把无错误或审美合作者意当作 AGI 定义。读者收益是区分好用、想继续用与已确认 AGI，不以术语或宏大展望结束。局部重写，前文主体不重开；case_only，正文待用户审阅。
'''
for name in ['retrospective.md','research/co-writing-log.md','research/differentiation.md']:
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
evidence='''# AGI 结尾证据与写作限制

核查：2026-09-05。

- TechRepublic，2026-09-04，https://www.techrepublic.com/article/news-openai-gpt-6-astra-agi-era-2026/ ：已读取原始全文，标题为 OpenAI Launches GPT-6 Astra as Brockman Says the ‘AGI Era’ Has Arrived。报道转述 OpenAI 总裁 Greg Brockman 的个人判断：For me personally, I do think we’re there；I think it’s not unreasonable to feel that we are now in the AGI era。正文仅概述 AGI 判断及媒体标题现象，不展开其跑分、安全或成本内容。该报道还有质疑，不能笼统指其为 AGI 背书。直接会议录像未取得，正文链接到报道，未声称亲历。
- OpenAI 原始发布页，https://openai.com/index/gpt-6-astra/ ：Astra is also better at staying oriented as a task evolves；新要求、改方向、支线问题不丢原目标。作为官方能力主张写入，不声称我们独立验证了相对前代的改进；没有把「保留需求」当作完整 AGI 定义。
- 已发上一篇的 3D/游戏/操作电脑内容不复述。本文自己的审美选择、试玩问题仍为原始证据，只支持体验范围，不用于证明或否定 AGI。
- 「这关不好玩」是作者设想的下一步要求，不是已提交提示词或已经成功的实验。下一次更新愿望为作者可审判断，不作产品发布承诺。
- Robin Sloan 的 2020/2025 软件随笔只在此次改向前调研，未用于正文。四组旧网友案例仍存档，used_in_draft=false。

来源截图回执：agi-headline-receipt.json。仅截原 h1 标题；非重绘图，权利仍 pending。

冷读：结尾讲对 AGI 说法的态度和持续使用期待；没有以失败推导 AGI 未到，没有要求 AGI 永不犯错，没有用「大家努力」替代具体进展，也没有再加测试案例。
'''
(root/'research/agi-ending-evidence.md').write_text(evidence,encoding='utf-8')
with (root/'sources.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## 当前末节｜FB026\n\nAGI 话题替换此前全部末节网友案例。当前原始报道、官方主张与作者判断边界见 [agi-ending-evidence.md](research/agi-ending-evidence.md)。FB024 及以前的结尾记录仅作历史，不代表当前正文。\n')
print(json.dumps({'ending_replaced':True,'article_images':len(re.findall(r'!\[',after)),'old_ending_cases_removed':True},ensure_ascii=False))
