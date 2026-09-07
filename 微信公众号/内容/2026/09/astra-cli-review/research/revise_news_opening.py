from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[1]
p=root/'draft.md'
old=p.read_text(encoding='utf-8')
(root/'research/history/2026-09-05-before-news-opening.md').write_text(old,encoding='utf-8')
start=old.index('这次测 Astra，我把 APPSO 的 Logo 也发给了它。')
end=old.index('## 先让 Logo 动起来')
opening='''今天早上，GPT-6 Astra 全量开放的消息来了。Plus 和 Business 用户也都能用上了。[开放公告](https://x.com/thsottiaux/status/2096002992046796932)

这两天，X 上晒出的作品已经很热闹了。有人做出糖豆人式的闯关游戏，有人搭起一座模拟城市，楼房、道路、河流铺满了画面。[游戏原帖](https://x.com/MatthewBerman/status/2095616764793270705)、[城市原帖](https://x.com/MatthewBerman/status/2095595893991129444)

![Matthew Berman 用 Astra 制作的模拟城市原型](assets/external/berman-city.jpg)

*图源：Matthew Berman / X。作者展示的是仍在开发中的原型。*

额度也有好消息。Anthropic 今天又给所有 Claude Max 用户重置了周额度。OpenAI 这边，Tibo 也宣布给 Plus、Pro 和 Business 用户再送一次可留存的完整重置机会，预计按原帖当地时间在当天结束前到账。[Claude Max 公告](https://x.com/lydiahallie/status/2095967323412930677)、[OpenAI 重置公告](https://x.com/thsottiaux/status/2096035437299237298)

![Lydia Hallie 宣布再次重置 Claude Max 周额度的完整原帖](assets/external/claude-max-weekend-reset.png)

*图源：Lydia Hallie / X，截图显示北京时间。本轮重置针对 Claude Max 的周额度。*

AI 玩家的「黄金周」又来了。

我们也把 Astra 和 Fable 5.1 拉来试了一轮。开唱片店、做小游戏，顺手还把 APPSO 的 Logo 发给了 Astra。

'''
logo='''## 先让 Logo 动起来

第一道题，就是把 APPSO 这几个字母做成一款能玩的 3D 游戏。A 左下角那颗独立的白点变成小球，由玩家控制，穿过字母组成的关卡，最后滚进 O。

![本次测试使用的 APPSO Logo 原图](assets/appso-logo-input.png)

*本次测试的输入图：APPSO Logo。*

Fable 5.1 用同一张图、同一份要求。两边各有一个独立文件夹。

'''
tail=old[end:].removeprefix('## 先让 Logo 动起来\n\n')
new=old[:start]+opening+logo+tail
assert new[new.index('A 有斜面，'):]==old[old.index('A 有斜面，'):]
p.write_text(new,encoding='utf-8')
manifest=root/'asset-manifest.yml'
m=manifest.read_text(encoding='utf-8')
assert 'assets/external/claude-max-weekend-reset.png' not in m
m+='''
  - file: assets/external/claude-max-weekend-reset.png
    used_in_draft: true
    visual_route: source_original
    source_original_kind: community_screenshot
    original_pixels_preserved: true
    source_type: public_web
    source: Lydia Hallie 的 Claude Max 周额度再次重置公告
    source_url: https://x.com/lydiahallie/status/2095967323412930677
    creator_or_rightsholder: Lydia Hallie / Anthropic / X
    obtained_on: "2026-09-05"
    modifications: 原生 X 嵌入截图，保留账号、完整正文、日期和互动区；无重绘或改字，显示北京时间
    rights_status: pending
    allowed_platforms: []
    attribution: 图源：Lydia Hallie / X
    notes: 本轮仅说明 Max 周额度重置；不写成所有订阅或 5 小时额度重置，不声称由竞争对手逼迫；回执见 research/claude-max-weekend-reset.json。
'''
manifest.write_text(m,encoding='utf-8')
check=root/'research/check_html_preview.py'
s=check.read_text(encoding='utf-8').replace("'Anthropic 的 Fable 5.1 与 Mythos 5.1 官方发布专题'","'Lydia Hallie 宣布再次重置 Claude Max 周额度的完整原帖'")
check.write_text(s,encoding='utf-8')
# Keep the selection page accurate after moving its official-page candidate out of this opening.
gallery=root/'dist/visual-selection.html'
s=gallery.read_text(encoding='utf-8').replace('<b>Anthropic 发布专题首页</b><p>已放入文章','<b>Anthropic 发布专题首页</b><p>备选')
gallery.write_text(s,encoding='utf-8')
note='''

## FB030｜新闻进入，再转实测

2026-09-05，用户认为 Logo 开头吸引力不足，指定全量开放、网友作品、Anthropic 重置、APPSO 体验的顺序。仅重写首节前导语，将 Logo 输入和同题要求移入「先让 Logo 动起来」；从「A 有斜面」开始的主体逐字保留，跑分和 AGI 结尾不动。

重新核到另一轮 Max 周额度公告：Lydia 原帖为 2026-09-04 20:08 UTC，即北京时间 9 月 5 日 04:08；Astra Plus/Business 开放帖为 22:30 UTC，即北京时间 06:30；Tibo 新重置帖为 9 月 5 日 00:39 UTC，即北京时间 08:39。原先引用的 ClaudeDevs 9 月 1 日发布重置是不同事件。今日 Max 重置早于全量开放帖，官方理由是 Fable 5.1 和长周末，因此不写成被 Astra 全量开放逼出来。

开头复用模拟城市原图，注明仍在开发，补 Lydia 完整文字公告截图；原图在手机上主体明确，文字帖承担规则证据。上一版 Tibo 图与 Anthropic 官网图留在素材库，避免新闻开头连续堆三张公告或产品图。沿用用户已定路线，case_only；不新增 SOP。
'''
for file in ['retrospective.md','research/co-writing-log.md']:
 with (root/file).open('a',encoding='utf-8') as f:f.write(note)
with (root/'sources.md').open('a',encoding='utf-8') as f:
 f.write('\n\n## FB030｜开头更新\n\n今日 Max 周额度重置使用 [Lydia 原帖](https://x.com/lydiahallie/status/2095967323412930677)，与早前 ClaudeDevs 的全体用户重置分开。原文、UTC 时间及完整截图指纹见 research/claude-max-weekend-reset.json；其余开头原帖重新获取记录见 research/opening-posts-20260905.json。没有竞争导致重置的证据。\n')
brief=root/'brief.md'
s=brief.read_text(encoding='utf-8')
s=s.replace('# 写作合同｜Astra 上线这一周','# 写作合同｜Astra 上线这一周\n\n> 当前入口更新（FB030）：按用户要求从北京时间 9 月 5 日 Astra 全量开放消息进入，展示网友作品，接今日 Max 周额度与 OpenAI 重置，再转 APPSO 实测。Logo 输入移入第一节；下文早期合同保留历史。')
brief.write_text(s,encoding='utf-8')
print('opening rewritten; body from logo geometry onward unchanged')
