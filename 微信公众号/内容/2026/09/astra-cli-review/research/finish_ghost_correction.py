from pathlib import Path
from PIL import Image
import hashlib,json,re,shutil,yaml
root=Path(__file__).resolve().parents[1]
target=root/'assets/infographic-003-image2.png'
shutil.copyfile(Path(r'C:\Users\22684\.codex-company\generated_images\01a06eac-ee34-7ea1-b4e6-174267c72f61\exec-5542b071-fb53-4b10-8c86-9c4bdf305e8d.png'),target)
manifest=root/'asset-manifest.yml'
raw=manifest.read_text(encoding='utf-8')
still='assets/user-results/ghost-fable-start.png'
shutil.copyfile(root/'research/viewing/missing-ghost/12-03-11-1.png',root/still)
if f'file: {still}\n' not in raw:
    block=re.search(r'  - file: research/viewing/missing-ghost/12-03-11-1.png\n.*?(?=  - file:|\Z)',raw,re.S).group(0)
    block=block.replace('research/viewing/missing-ghost/12-03-11-1.png',still)
    block=re.sub(r'    use: research_reference\n','',block)
    raw+=block
receipt='research/image-generation-runs/infographic-003-final-preflight.json'
preflight=json.loads((root/receipt).read_text(encoding='utf-8'))
if 'file: assets/infographic-003-image2.png\n' not in raw:
    old=re.search(r'  - file: assets/infographic-001-image2.png\n.*?(?=  - file:|\Z)',raw,re.S).group(0)
    new=old.replace('infographic-001','infographic-003')
    new=re.sub(r'    input_assets: .*', '    input_assets: [assets/infographic-001-image2.png, research/source-assets/appsso-logo-red-background.png]',new)
    new=re.sub(r'    invocation_prompt_sha256: .*','    invocation_prompt_sha256: '+preflight['invocation_prompt_sha256'],new)
    raw+=new
draft=(root/'draft.md').read_text(encoding='utf-8')
def usage(match):
    block=match.group(0)
    file=re.search(r'file: (.+)',block).group(1).strip()
    block=re.sub(r'used_in_draft: (true|false)','used_in_draft: '+str(f']({file})' in draft).lower(),block)
    if file=='assets/infographic-001-image2.png' and '    use:' not in block:
        block=block.rstrip()+'\n    use: research_reference\n'
    return block
manifest.write_text(re.sub(r'  - file:.*?(?=  - file:|\Z)',usage,raw,flags=re.S),encoding='utf-8')
with Image.open(target) as im:
    final=dict(file=target.relative_to(root).as_posix(),width=im.width,height=im.height,bytes=target.stat().st_size,
      sha256=hashlib.file_digest(target.open('rb'),'sha256').hexdigest(),preflight_receipt=receipt)
path=root/'research/infographic-delivery.json'
record=json.loads(path.read_text(encoding='utf-8'))
record['assets']=[x for x in record['assets'] if x['file']!=final['file']]+[final]
record['superseded_assets']=['assets/infographic-001-image2.png']
record['latest_correction']='作者按文件名更正模型归属。第三张图替换第一张，Astra 小妖改为录屏已跑到终点。'
path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Inspect actual GIF frames, not synthetic comparisons. These are preview artifacts.
for name in ['ghost-fable-intro','ghost-fable-play']:
    with Image.open(root/f'assets/feishu/{name}.gif') as im:
        for fraction,label in [(0.5,'middle'),(0.95,'end')]:
            im.seek(min(im.n_frames-1,int(im.n_frames*fraction)))
            im.convert('RGB').save(root/f'dist/{name}-{label}.png')
print(json.dumps(final,ensure_ascii=False))
