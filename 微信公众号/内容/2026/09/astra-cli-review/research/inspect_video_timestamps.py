from pathlib import Path
import av
from PIL import Image, ImageDraw
root = Path(__file__).resolve().parents[1]
source = next(Path('C:/Users/22684/Videos/Captures').glob('月屿*10-17-44.mp4'))
canvas = Image.new('RGB', (1440,1350))
draw = ImageDraw.Draw(canvas)
times = iter(range(0,28,2))
target = next(times)
index = 0
with av.open(str(source)) as c:
    for frame in c.decode(video=0):
        if frame.time < target:
            continue
        im = frame.to_image()
        im.thumbnail((480,270))
        xy = ((index%3)*480, (index//3)*270)
        canvas.paste(im, xy)
        draw.rectangle((xy[0],xy[1],xy[0]+40,xy[1]+20),fill='white')
        draw.text((xy[0]+5,xy[1]+4),str(target),fill='black')
        index += 1
        try:
            target = next(times)
        except StopIteration:
            break
canvas.save(root/'research/viewing/lune-timeline.jpg',quality=90)
