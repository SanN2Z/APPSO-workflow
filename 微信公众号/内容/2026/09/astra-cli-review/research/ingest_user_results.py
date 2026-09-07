"""Read user material locally; never persist temporary download credentials."""
import concurrent.futures
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/user-results'
OUT.mkdir(parents=True, exist_ok=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def document(path):
    from PIL import Image
    content = path.read_text(encoding='utf-8-sig')
    rows, owner = [], 'unknown'
    for line in content.splitlines():
        if line.strip().rstrip(':：') in ['Astra', 'Fable']:
            owner = line.strip().rstrip(':：')
        for url in re.findall(r'!\[[^\]]*\]\((https://[^)]+)\)', line):
            rows.append((len(rows)+1, owner, url))
    def fetch(item):
        index, model, url = item
        name = f'doc-{index:02d}-{model.lower()}.png'
        target = OUT/name
        result = dict(index=index, model_label=model, source='user-provided-document/image-'+str(index), file='assets/user-results/'+name)
        try:
            raw = urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=35).read()
            import io
            with Image.open(io.BytesIO(raw)) as im:
                result.update(width=im.width,height=im.height,format=im.format)
                im.verify()
            target.write_bytes(raw)
            result.update(status='downloaded',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        except HTTPError as exc:
            result.update(status='http-error',http_status=exc.code)
        except Exception as exc:
            result.update(status='failed',error_type=type(exc).__name__)
        print(json.dumps(result,ensure_ascii=False))
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(fetch,rows))
    receipt=dict(accessed_at=datetime.now(timezone.utc).isoformat(), document_sha256=digest(path),images=results,notes='Download query credentials intentionally omitted. Model labels copied from document, not inferred from visuals.')
    (ROOT/'research/user-document-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 用户测评文档（去除临时下载凭据的素材索引）','']
    for r in results:
        lines.extend([f"## 图片 {r['index']}｜文档标签 {r['model_label']}", f"状态：{r['status']}"])
        if r['status']=='downloaded':
            lines.append(f"![文档图片 {r['index']}](../{r['file']})")
        lines.append('')
    (ROOT/'research/user-document-sanitized.md').write_text('\n'.join(lines),encoding='utf-8')

def video(path):
    import cv2
    cap=cv2.VideoCapture(str(path))
    fps=cap.get(cv2.CAP_PROP_FPS)
    count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration=count/fps
    record=dict(source_path=str(path),bytes=path.stat().st_size,sha256=digest(path),fps=fps,frames=count,duration_seconds=duration,width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),samples=[])
    for seconds in sorted(set([0.0]+[round(duration*i/12,2) for i in range(1,12)]+[max(0,duration-1)])):
        cap.set(cv2.CAP_PROP_POS_MSEC,seconds*1000)
        ok,frame=cap.read()
        if not ok: continue
        name=f'video-{int(seconds*1000):07d}ms.png'
        target=OUT/name
        ok,raw=cv2.imencode('.png',frame)
        if not ok: continue
        target.write_bytes(raw.tobytes())
        record['samples'].append(dict(requested_seconds=seconds,file='assets/user-results/'+name,sha256=digest(target)))
    cap.release()
    (ROOT/'research/user-video-receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k!='source_path'},ensure_ascii=False))

if __name__=='__main__':
    mode=sys.argv[1]
    (document if mode=='document' else video)(Path(sys.argv[2]))
