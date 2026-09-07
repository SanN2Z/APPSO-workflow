from pathlib import Path
import av
import json
import hashlib
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
source = next(Path('C:/Users/22684/Videos/Captures').glob('APPSO Logo*12-06-10.mp4'))
out = root/'research/viewing/logo-recording'
out.mkdir(parents=True, exist_ok=True)
with av.open(str(source)) as c:
    duration = c.duration/1000000
    v = c.streams.video[0]
    receipt = dict(source_path=str(source),duration_seconds=duration,width=v.width,height=v.height,
                   bytes=source.stat().st_size,has_audio=bool(c.streams.audio),
                   sha256=hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),samples=[])
    times = iter([duration*i/12 for i in range(12)]+[max(0,duration-.3)])
    target = next(times)
    canvas = Image.new('RGB',(1440,1350),'white')
    draw = ImageDraw.Draw(canvas)
    index = 0
    for frame in c.decode(video=0):
        if frame.time < target:
            continue
        im = frame.to_image()
        im.save(out/f'frame-{index:02}.png')
        receipt['samples'].append(dict(seconds=frame.time,file=f'research/viewing/logo-recording/frame-{index:02}.png'))
        im.thumbnail((480,270))
        x,y = (index%3)*480,(index//3)*270
        canvas.paste(im,(x,y))
        draw.rectangle((x,y,x+65,y+18),fill='white')
        draw.text((x+3,y+3),f'{frame.time:.2f} s',fill='black')
        index += 1
        try:
            target = next(times)
        except StopIteration:
            break
canvas.save(out/'timeline.jpg',quality=90)
(root/'research/logo-recording-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
