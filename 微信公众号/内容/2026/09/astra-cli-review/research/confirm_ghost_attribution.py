"""Apply the author's model identification to existing local evidence."""
raise SystemExit('Historical script superseded by correct_ghost_media.py after author filename correction. Do not apply the former attribution.')
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
confirmation = '作者于 2026-09-05 在会话中确认该小妖录屏来自 Fable；反馈画面比 Astra 精美一些，左右方向好像设反。审美为作者判断，方向问题尚未独立复现。'
path = root/'research/video-export-receipt.json'
receipt = json.loads(path.read_text(encoding='utf-8'))
receipt['sources']['ghost']['model'] = 'Fable 5.1'
receipt['sources']['ghost']['model_evidence'] = confirmation
for item in receipt['outputs']:
    if item['source']=='ghost':
        item['model'] = 'Fable 5.1'
path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

path = root/'asset-manifest.yml'
text = path.read_text(encoding='utf-8')
def patch(match):
    block = match.group(0)
    if re.search(r'file: assets/(?:video/ghost-|user-results/video-)',block):
        block = block.rstrip()+'\n    model: Fable 5.1\n    model_identification: '+confirmation+'\n'
    return block
text = re.sub(r'  - file:.*?(?=  - file:|\Z)',patch,text,flags=re.S)
path.write_text(text,encoding='utf-8')

path = root/'research/recording-evidence.md'
text = path.read_text(encoding='utf-8').replace('模型名不在视频中，已异步向作者询问，未凭视觉猜测。',confirmation)
text = text.replace('暂缺：小妖模型名、Logo 真人试玩及 Fable Logo 对照', '暂缺：Astra 小妖对照画面、Logo 真人试玩及 Fable Logo 对照')
text += '\n作者对 Fable 和 Astra 的画面比较可以按第一人称写进稿子；本编辑尚未拿到 Astra 小妖对照素材，不补造差异细节。录屏未显示同步按键，不能认定左右映射确实反转，或推断这是重来的原因。\n'
path.write_text(text,encoding='utf-8')

path = root/'research/media-handoff.md'
text = path.read_text(encoding='utf-8').replace('小妖快跑｜完整试玩','Fable 5.1 小妖快跑｜完整试玩')
text += '\n模型归属已确认：ghost 开头的 MP4 与 3 张 GIF 全部属于 Fable 5.1；lune 开头的文件属于 Astra。用户已反馈 Fable 小妖左右方向疑似反转，画面更精美；保留原始试玩，不修饰这些问题。\n'
path.write_text(text,encoding='utf-8')
for name, body in {
    'research/live-results.md': '\n## 作者确认小妖模型归属\n\n'+confirmation+'此前待确认状态在本条之后关闭。全部 ghost 素材归 Fable 5.1，Astra 小妖画面仍待补。\n',
    'research/co-writing-log.md': '\n## 小妖作者反馈｜局部更新\n\n作者确认既有录屏为 Fable，并补充左右方向疑似反转、画面比 Astra 精美一些。N4 增加第一人称审美判断，保留「好像」的不确定性；删除此前猜测操作不熟的句子，不把重来归因于未复现的按键问题。图注及素材记录同步归属，不修改游戏或视频。\n',
    'retrospective.md': '\n## FB010｜小妖模型确认与试玩反馈\n\n2026-09-05，来源：作者会话，阶段：draft，case_only。作者确认 10-54-51 小妖录屏为 Fable，反馈左右方向好像设反、画面比 Astra 更精美一些。修复：正文与 3 张 GIF 图注补全模型名，登记到视频清单与原始证据；主观判断按作者口吻保留，方向问题保留不确定性。没有修改被测代码或把反馈扩成整体能力排名。\n',
}.items():
    with (root/name).open('a',encoding='utf-8') as f:
        f.write(body)
print('Updated draft evidence and attribution; video bytes unchanged.')
