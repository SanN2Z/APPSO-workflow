"""Download selected public originals; no accounts, cookies or API keys."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SPECS = [
    ('official-astra-launch-video-cover.jpg', 'https://pbs.twimg.com/amplify_video_thumb/2095595661559574528/img/Vmb2pgEFJ6fpCUTD.jpg', 'https://x.com/OpenAI/status/2095595741528125780', 'OpenAI', '官方发布视频封面，不是作者实测截图'),
    ('official-astra-hallucinations-figure6.png', 'https://deploymentsafety.openai.com/data/eval-sets/gpt-6-astra/assets/images/image7.png', 'https://deploymentsafety.openai.com/gpt-6-astra', 'OpenAI', '系统卡 Figure 6，用户标记高幻觉风险样本，非生产平均错误率'),
    ('arc-astra-two-harnesses.png', 'https://arcprize.org/media/images/blog/astra-arc-agi-3-leaderboard.png', 'https://arcprize.org/blog/astra', 'ARC Prize Foundation', '基准主办方原图；两种运行框架分开标注'),
    ('arc-astra-action-efficiency.png', 'https://arcprize.org/media/images/blog/astra-action-efficiency.png', 'https://arcprize.org/blog/astra', 'ARC Prize Foundation', '动作效率原图，不能解释为现实世界所有任务超过人类'),
]


def main():
    from PIL import Image
    import yaml
    (ROOT / 'assets').mkdir(exist_ok=True)
    receipt, assets = [], []
    for name, url, page, owner, caption in SPECS:
        target = ROOT / 'assets' / name
        if target.exists():
            raise SystemExit(f'Refusing to overwrite {name}')
        raw = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=35).read()
        target.write_bytes(raw)
        with Image.open(target) as im:
            size = im.size
            im.verify()
        digest = hashlib.sha256(raw).hexdigest()
        receipt.append(dict(file=f'assets/{name}', download_url=url, source_url=page, bytes=len(raw), width=size[0], height=size[1], sha256=digest, obtained_on='2026-09-05'))
        assets.append(dict(file=f'assets/{name}', used_in_draft=False, visual_route='source_original', source_original_kind='official_original', original_pixels_preserved=True, source_type='official_material', source=caption, source_url=page, download_url=url, creator_or_rightsholder=owner, obtained_on='2026-09-05', modifications='无修改，下载原始文件', rights_status='pending', allowed_platforms=[], attribution=f'图源：{owner}；{page}', notes='研究候选；发布前核对转载边界及允许平台'))
        print(name, size, len(raw), digest[:12])
    (ROOT / 'research/asset-download-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    class IndentedDumper(yaml.SafeDumper):
        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow, False)
    (ROOT / 'asset-manifest.yml').write_text(yaml.dump(dict(version=3, updated='2026-09-05', assets=assets), Dumper=IndentedDumper, allow_unicode=True, sort_keys=False), encoding='utf-8')


if __name__ == '__main__':
    main()
