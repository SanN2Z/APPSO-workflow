from pathlib import Path
import json
import yaml

root = Path(__file__).resolve().parents[1]
draft = root/'draft.md'
old = draft.read_text(encoding='utf-8')
history = root/'research/history/before-external-ending.md'
if not history.exists(): history.write_text(old,encoding='utf-8')
with (root/'research/co-writing-log.md').open('a',encoding='utf-8') as f:
    f.write('''\n## 作者要求补外部材料与有信息量的结尾\n\n- 用户反馈：原稿缺结尾，外部资料少；要求补信息增量。保留现有实测顺序和作者判断，不重写成海外演示汇总。\n- E1（ai_candidate）：在自由审美之后补 Every 写作测试的公开自述；没有本人的写作样本，不冒充作者实测，不延伸付费正文。\n- E2（ai_candidate）：游戏后用 Berman 的 5 天长任务与 Cognition 的工程交付评价补充完整开发的成本和验收口径；Cognition 明确为集成方自有评测。\n- E3（human_first 候选）：保留用户对 Fable 左右方向的疑问，把下一轮要求写成可复制的最小修改委托，保护已有画面、核对控制、录制真实操作。结尾停在具体任务，不另补宏观总结。\n- 作者将归档位置与常规操作交给助手，默认自媒体运营下每篇单独文档；MCP 尚未连入当前会话，不创建不存在的链接。\n''')
outside = '''## 写作这边，也有人交了作业

Every 的作者 Katie Parrott 分享了一件事：她让 Astra 用一条提示词写了那篇测评的初稿。把稿子发给联合创始人 Dan Shipper 后，对方以为是她自己写的。[Every 原文](https://every.to/vibe-check/gpt-6-astra-vibe-check)

![Every 对 Astra 写作体验的公开介绍](assets/every-astra-writing.png)

*图源：Every，公开页面截图。*

Every 在导语里肯定了 Astra 的写作、软件操作和视觉设计。不过，他们仍然认为 Fable 更懂得怎么把一个产品做出来。

这部分我们还没有做单独的写作实测。网页里几句有气氛的文案，和一篇能交稿的文章，要看的东西不一样。

'''
text = old.replace('## 再做一款「阴间糖豆人」',outside+'## 再做一款「阴间糖豆人」')
text = text.replace('下一轮先核对方向控制，再调整镜头。\n\n','')
ending = '''## 做出来之后，能不能接着改

前面提到的 Matthew Berman，还用 Astra 做了一个模拟城市项目。他在 X 上说，自己开了 `/goal`，让它连续跑了 5 天，发演示时仍然没有做完。他拿到过提前测试权限，这也不是发布后才开始跑的任务。[项目原帖](https://x.com/MatthewBerman/status/2095595893991129444)、[提前测试说明](https://x.com/MatthewBerman/status/2095595892464333065)

Cognition 的测试看的是另一件事：写出的代码，能不能达到维护者愿意合并进项目的标准。除了功能，它还检查测试质量、修改范围，以及是否符合原项目的规范。[FrontierCode 方法介绍](https://cognition.com/frontiercode)

这家把 Astra 接入 Devin 的公司称，在自有的 FrontierCode 1.1 工程评测中，Astra 的成绩超过了 Fable 5.1。用它执行测试时，测试覆盖、报告和录屏证据也有改善。这是 Cognition 在自家环境下的结果。[Cognition 测评](https://devin.ai/blog/gpt-6-astra)

接下来，我想把已经做好的小妖游戏留住，继续给 Fable 发一轮修改要求：

> 先核对左右控制是否符合屏幕方向。如果确实反了，只修这一处。保留角色、灯光、材质和关卡布局。改完后分别测试左移、右移、跳跃和掉落重生，再录一段实际操作。暂时不要加新功能。

这一轮要看的是，它能不能听懂这次修改，把操作修好，同时保住已经做得不错的画面。
'''
insert = text.index('<!-- 编辑待办：')
text = text[:insert]+ending+'\n'+text[insert:]
draft.write_text(text,encoding='utf-8')

manifest = root/'asset-manifest.yml'
data = yaml.safe_load(manifest.read_text(encoding='utf-8'))
if 'assets/every-astra-writing.png' not in {a['file'] for a in data['assets']}:
    item = dict(file='assets/every-astra-writing.png',used_in_draft=True,visual_route='source_original',source_original_kind='community_screenshot',
                original_pixels_preserved=True,source_type='third_party_review',source='Every 测评公开标题、署名和导语',
                source_url='https://every.to/vibe-check/gpt-6-astra-vibe-check',creator_or_rightsholder='Every / Katie Parrott',
                obtained_on='2026-09-05',modifications='独立浏览器原生截图；不登录，不读取付费正文，不改写页面内容',
                rights_status='pending',allowed_platforms=[],attribution='图源：Every',notes='仅公开导语；正文中的经历是测评作者自述，不是本稿作者测试。截图指纹见 external-followup-images.json。')
    with manifest.open('a',encoding='utf-8') as f:
        f.write(''.join('  '+line+'\n' for line in yaml.safe_dump([item],allow_unicode=True,sort_keys=False).splitlines()))

(root/'research/ending-evidence.md').write_text('''# 外部补充与结尾事实映射

核查日：2026-09-05。本轮正文仍以现有实测为主，不复用公司上一篇的正文或翻译。

- Every，https://every.to/vibe-check/gpt-6-astra-vibe-check ：公开标题、署名、9 月 3 日日期、导语均已重新打开，并用独立浏览器截图。Katie Parrott 自述初稿由 Astra 单提示完成，Dan Shipper 以为由她所写。只引述这段经历及公开的产品判断；没有读付费完整测评。文章使用正常归属，不声称自身写作实测通过。
- Berman 模拟城市，https://x.com/MatthewBerman/status/2095595893991129444 ：此前同日公开 syndication 回执含原帖全文：使用 /goal，连续 5 天，发布演示时尚未完成。当前直接 web 打开 403；原始回执仍在 research/source-assets/goldweek-post-receipts.json，访问 2026-09-05T01:26:51Z。其总帖 2095595892464333065 明确提前访问。不能把 5 天写成 Astra 普遍开发用时，也不能误写为发布后才开始。
- Cognition 方法，https://cognition.com/frontiercode ：本轮重新读取，评价是否可合并，覆盖功能正确性、测试质量、修改范围、代码风格、项目规范。未拿单个网页截图推断代码工程质量。
- Cognition Astra 测评，https://devin.ai/blog/gpt-6-astra ：9 月 3 日公布，本轮重新读取。自有 FrontierCode 1.1 成绩 Astra 超过 Fable 5.1；内部测试评测报告更全面、报告更清楚、视频证据更友好。正文明确是商业集成方自有环境。没有误把原文相对 Fable 5 的 64% 成本差说成相对 Fable 5.1。
- 结尾中的「只修方向、保留画面」为本稿下一轮委托候选，不是已经执行的测试；Fable 方向问题继续保留「如果确实反了」条件。

来源公开可访问不等于转载许可，新增图仍 pending。正文更换为轻量 GIF，但原速、模型归属与源视频保留。
''',encoding='utf-8')
with (root/'sources.md').open('a',encoding='utf-8') as f:
    f.write('\n## 本轮外部内容与结尾增补\n\nEvery 与 Cognition 重新读取；Berman 5 天长任务保留同日一手回执及提前访问上下文。精确支持范围见 [ending-evidence.md](research/ending-evidence.md)。\n')
print('Added external writing example and engineering follow-up ending.')
