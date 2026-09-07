from pathlib import Path
import av, json
root=Path(__file__).resolve().parents[1]
out=root/'research/viewing/missing-ghost'
out.mkdir(exist_ok=True)
rows=[]
for src in Path(r'C:\Users\22684\Videos\Captures').glob('*2026-09-05 12-03*.mp4'):
    with av.open(str(src)) as container:
        duration=container.duration/av.time_base
        targets=[1,duration/2,max(1,duration-2)]
        k=0
        for frame in container.decode(video=0):
            if k<len(targets) and frame.time>=targets[k]:
                name=src.stem[-8:]+f'-{k}.png'
                frame.to_image().save(out/name)
                k+=1
            if k==len(targets):break
        rows.append(dict(file=src.name,duration=duration,frames=k))
print(json.dumps(rows,ensure_ascii=False))
