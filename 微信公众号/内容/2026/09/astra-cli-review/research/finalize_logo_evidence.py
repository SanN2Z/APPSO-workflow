from pathlib import Path
import json
import re
import av

root = Path(__file__).resolve().parents[1]
receipt_path = root/'research/logo-recording-receipt.json'
receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
checks = []
for path in [Path(receipt['source_path']),root/'assets/video/logo-astra-full.mp4']:
    streams = []
    for kind in ['video','audio']:
        with av.open(str(path)) as c:
            selected = [s for s in c.streams if s.type==kind]
            if not selected:
                continue
            times = [float(f.pts*f.time_base) for f in c.decode(selected[0]) if f.pts is not None]
            streams.append(dict(kind=kind,decoded_frames=len(times),first_pts_seconds=times[0],last_pts_seconds=times[-1],
                                monotonic_pts=all(a<=b for a,b in zip(times,times[1:]))))
    checks.append(dict(file=path.name,streams=streams))
assert all(s['monotonic_pts'] for c in checks for s in c['streams'])
assert [s['decoded_frames'] for s in checks[0]['streams']]==[s['decoded_frames'] for s in checks[1]['streams']]
receipt['direct_decode_verification'] = checks
receipt['verification_notes'] = 'FFmpeg null muxer emitted repeated DTS warnings; separately decoded every video and audio frame with PyAV. Both source and remux have monotonic presentation timestamps and matching decoded frame counts. No decoding error.'
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

draft = (root/'draft.md').read_text(encoding='utf-8')
manifest = root/'asset-manifest.yml'
def flags(match):
    block = match.group(0)
    name = re.search(r'file: (.+)',block).group(1).strip()
    if 'logo-astra' in name:
        used = f']({name})' in draft
        block = re.sub(r'used_in_draft: (true|false)',f'used_in_draft: {str(used).lower()}',block)
    return block
manifest.write_text(re.sub(r'  - file:.*?(?=  - file:|\Z)',flags,manifest.read_text(encoding='utf-8'),flags=re.S),encoding='utf-8')

path = root/'research/recording-evidence.md'
text = path.read_text(encoding='utf-8').replace('暂缺：Astra 小妖对照画面、Logo 真人试玩及 Fable Logo 对照','暂缺：Astra 小妖对照画面、Fable Logo 对照')
text += '\n## 新增 Astra Logo 真人试玩\n\n作者回传 Play Lab 截图并指明 Captures 有新录屏。定位 APPSO Logo 乐园 · Play Lab 的 12-06-10 文件，约 26 秒；页面匹配 Astra 项目。点击开始后，进度从 A 到第一个 P，出现多次掉落重生和暂停面板，录制结束仍未通关。正文替换自动测试说明为这段真实操作，未写成真人通关或完整验收。\n'
path.write_text(text,encoding='utf-8')
for name,body in {
    'research/live-results.md':'\n## Astra Logo 已收到真人试玩\n\n作者新上传截图，12-06-10 的 26 秒录屏已读入。原速素材已导出；从 A 到第一个 P，途中掉落、重生和暂停，没有录到终点。覆盖此前缺真人试玩的状态，Fable Logo 仍缺。\n',
    'research/co-writing-log.md':'\n## N3 更新为作者真人试玩\n\n依作者新素材补入 Astra Logo 原图与实际录屏，撤下项目自动测试的公共叙述，保留内部记录。补写从 A 到第一个 P 与掉落提示，不扩展为真人通关。只更新 N3 和对应素材状态，不改变已确认 Fable 小妖归属。\n',
    'retrospective.md':'\n## FB011｜Logo 真人试玩接稿\n\n2026-09-05，作者提供实际截图并告知新录屏在 Captures。阶段 draft，case_only。按内容复盘技能记录：定位同名 Logo 视频，保留源，导出完整 MP4 与两张短 GIF；实际操作覆盖旧的「等待真人试玩」状态。没有录到通关，不拿自动通关图补成真人结果。原图来源、转码、权利登记；源与导出音视频逐帧解码核对通过。未修改被测项目或发布。\n',
}.items():
    with (root/name).open('a',encoding='utf-8') as f:
        f.write(body)
print(json.dumps(checks,ensure_ascii=False))
