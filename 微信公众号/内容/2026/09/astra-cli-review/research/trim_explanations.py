from pathlib import Path
import difflib, json, re

root = Path(__file__).resolve().parents[1]
path = root / 'draft.md'
before = path.read_text(encoding='utf-8')
history = root / 'research/history/2026-09-05-before-explanation-trim.md'
if not history.exists():
    history.write_text(before, encoding='utf-8')
deletions = [
    ('这张图里有不少现成的形状。', '后面已逐个列出 A、P、S、O 的形状。'),
    ('这样的细节放在这么干净的页面上，反而很显眼。', '前句已交代时间重复挤在一起，不再补反转收尾。'),
    ('画面已有城市，作者说项目还没做完。', '图注重复紧邻正文的项目状态；保留来源。'),
    ('这六项里，Astra 在终端、软件工程、科研工作流和高难数学上更高。Fable 5.1 则在带工具的 HLE 和 AA 综合智能指数上更高。\n\n', '六项信息图已逐行标红较高值，不再复述排名。'),
    ('这轮的游戏和网页，更多是在看成品是否合我的口味，以及操作能否跑通。', '重复前面实测的观察范围；保留分开看各榜单的判断及理由。'),
    ('后者分数更高，前者费用更低。', '紧邻跑分和价格已经给出，删除可以直接比较得到的结论。'),
    ('这套测试里，多花的钱没有换来同样明显的分数提升。', '前句已有两个档位的费用与接近的分数，不再总结。'),
    ('我们这轮也没有完整记录用量，所以不算谁更省订阅。', '正文没有比较订阅消耗；保留 API 成本不能换算订阅额度的必要限定。'),
    ('至于画面要不要重做，还是得自己点开玩一遍。', '泛化的段尾收束，前面已有实际试玩与作者具体选择。'),
]
after = before
for sentence, reason in deletions:
    assert after.count(sentence) == 1, sentence
    after = after.replace(sentence, '', 1)
after = after.replace('两者的指数都在 67 左右。\n\n这些是按 Token', '两者的指数都在 67 左右。这些是按 Token')
# User requested deletion only: the retained text must remain an ordered subsequence.
old = iter(re.sub(r'\s+', '', before))
assert all(any(x == ch for x in old) for ch in re.sub(r'\s+', '', after))
assert re.findall(r'!\[[^\]]*\]\([^)]*\)', before) == re.findall(r'!\[[^\]]*\]\([^)]*\)', after)
assert re.findall(r'https?://[^)\s]+', before) == re.findall(r'https?://[^)\s]+', after)
path.write_text(after, encoding='utf-8')
diff = ''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='before',tofile='after'))
(root/'research/explanation-trim.diff').write_text(diff,encoding='utf-8')
note = '\n\n## FB022｜全文删除多余解释，合并结尾两段\n\n2026-09-05，作者反馈结尾仍有 AI 味，要求全文仅删除重复解释、可自行推出的总结、刻意反转和段尾结论，不改判断、用词及顺序。\n\n'
note += '\n'.join('- 删除「'+s.strip()+'」：'+r for s,r in deletions)
note += '\n\n结尾合为一段，保留原有常规档位起稿、难题提高推理强度的选择。未新增词句或挪动段落；有序子序列检查、全部图片与链接保留检查通过。快照与逐句 diff 见 research/history/2026-09-05-before-explanation-trim.md 和 research/explanation-trim.diff。case_only，沿用既有删解释规则。\n'
for name in ['retrospective.md', 'research/co-writing-log.md']:
    with (root/name).open('a',encoding='utf-8') as f:
        f.write(note)
print(json.dumps({'deleted_locations':len(deletions),'removed_characters':len(before)-len(after),'deletion_only':True,'images_and_links_preserved':True},ensure_ascii=False))
print(after[after.index('更有意思的是 Astra 自己的档位差别。'):after.index('<!-- 编辑待办')].strip())
