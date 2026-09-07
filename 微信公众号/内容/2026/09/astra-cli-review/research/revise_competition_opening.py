from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'draft.md'
s=p.read_text(encoding='utf-8')
(root/'research/history/2026-09-05-before-competition-opening.md').write_text(s,encoding='utf-8')
s=s.replace('今天早上，GPT-6 Astra 全量开放了。Plus 和 Business 用户也都能用上了。','GPT-6 Astra 今天全量开放了。Plus 和 Business 用户也都能用上了。')
s=s.replace('这两天，X 上已经接连出现了一些惊艳的作品。有人做出糖豆人式的闯关游戏，有人搭起一座模拟城市，楼房、道路、河流铺满了画面。','看完 X 上那些演示，很难不想自己试试。糖豆人式的闯关游戏、铺满楼房和道路的模拟城市，已经有人用 Astra 做出来了。')
old='额度也有好消息。Anthropic 今天又给所有 Claude Max 用户重置了周额度。OpenAI 这边，Tibo 也宣布给 Plus、Pro 和 Business 用户再送一次可留存的完整重置机会，预计按原帖当地时间在当天结束前到账。[Claude Max 公告](https://x.com/lydiahallie/status/2095967323412930677)、[OpenAI 重置公告](https://x.com/thsottiaux/status/2096035437299237298)'
new='''Astra 这么热闹，A 社今天给所有 Claude Max 用户重置周额度，就很应景了。[Claude Max 公告](https://x.com/lydiahallie/status/2095967323412930677)

这架势，很有点「再不送点额度，大家就去隔壁了」的意思。

OpenAI 这边也在送。Tibo 宣布，Plus、Pro 和 Business 用户还会再拿到一次可留存的完整重置机会。[OpenAI 重置公告](https://x.com/thsottiaux/status/2096035437299237298)'''
assert old in s
s=s.replace(old,new)
s=s.replace('AI 玩家的「黄金周」又来了。','两家忙着抢用户，AI 玩家的「黄金周」又来了。')
original=p.read_text(encoding='utf-8')
assert s[s.index('## 先让 Logo 动起来'):]==original[original.index('## 先让 Logo 动起来'):]
p.write_text(s,encoding='utf-8')
note='''

## FB031｜竞争语气与事实边界

2026-09-05，用户指出新闻式开头无聊，要求写出两家竞争、Astra 吸引用户而 Anthropic 送额度留人的梗感。上一轮把用户提出的竞争判断过度处理成公告时间线，虽避免了错误因果，也丢掉了文章语气。

本轮开头改为「看演示想上手 → A 社重置很应景 → 再不送额度就去隔壁的旁白 → OpenAI 也送 → 黄金周与我们的体验」。用「这架势，很有点……的意思」明确为作者对竞争的解读，不虚构官方承认、不写成今日全量开放公告直接导致了更早的 Max 重置。保留账户范围和未来重置机会，不写到账已完成；具体到账时间移出开头。第一节及之后逐字保持。处置 case_only，本轮不新增 SOP。
'''
for f in ['retrospective.md','research/co-writing-log.md']:
 with (root/f).open('a',encoding='utf-8') as h:h.write(note)
print('opening tone revised; all sections unchanged')
