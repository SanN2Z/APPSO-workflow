"""Create local publication candidates from user recordings, preserving source files."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import av
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/video'
OUT.mkdir(exist_ok=True)
CAPTURES = Path('C:/Users/22684/Videos/Captures')
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def metadata(path):
    with av.open(str(path)) as container:
        video = container.streams.video[0]
        return dict(duration_seconds=container.duration / 1000000,
                    width=video.width, height=video.height,
                    has_audio=bool(container.streams.audio), bytes=path.stat().st_size,
                    sha256=hashlib.file_digest(path.open('rb'), 'sha256').hexdigest())

def run(args):
    subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-nostdin', *args], check=True)

sources = {
    'ghost': next(CAPTURES.glob('小妖快跑*10-54-51.mp4')),
    'lune': next(CAPTURES.glob('月屿*10-17-44.mp4')),
}
receipt = {'sources': {}, 'outputs': [], 'notes': 'Local derivatives. Sources unchanged. No speed change, synthetic frames, overlays, or scene replacement. GIFs are silent selected excerpts; MP4s retain the complete recording and source audio.'}
for key, path in sources.items():
    receipt['sources'][key] = dict(path=str(path), **metadata(path))
    target = OUT / (key + '-full.mp4')
    if '--gifs-only' not in sys.argv:
        run(['-y', '-i', str(path), '-map', '0:v:0', '-map', '0:a?',
         '-vf', 'scale=1280:-2:flags=lanczos', '-c:v', 'libx264', '-preset', 'fast',
         '-crf', '21', '-pix_fmt', 'yuv420p', '-fps_mode', 'vfr', '-c:a', 'aac', '-b:a', '128k',
         '-movflags', '+faststart', '-map_metadata', '-1', str(target)])
    receipt['outputs'].append(dict(file='assets/video/'+target.name, source=key, kind='full_mp4', **metadata(target)))
    print('Created ' + target.name, flush=True)

clips = [('ghost-start', 'ghost', 0, 7), ('ghost-platforms', 'ghost', 50, 7),
         ('ghost-finish', 'ghost', 84, 9), ('lune-tide', 'lune', 7, 7),
         ('lune-sky', 'lune', 13, 8)]
for name, key, start, length in clips:
    target = OUT / (name + '.gif')
    filt = 'fps=10,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=bayer:bayer_scale=3'
    run(['-y', '-ss', str(start), '-t', str(length), '-i', str(sources[key]),
         '-filter_complex', filt, '-an', '-loop', '0', str(target)])
    receipt['outputs'].append(dict(file='assets/video/'+target.name, source=key, kind='excerpt_gif',
                                   start_seconds=start, excerpt_seconds=length, **metadata(target)))
    print('Created ' + target.name, flush=True)

for item in receipt['outputs']:
    run(['-i', str(ROOT / item['file']), '-f', 'null', '-'])
    item['full_decode_check'] = 'passed'
(ROOT / 'research/video-export-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt['outputs'], ensure_ascii=False), flush=True)
