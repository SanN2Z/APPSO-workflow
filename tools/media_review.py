"""Build offline APPSO image or video review pages from a media manifest."""
from __future__ import annotations

import argparse
import html
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'APPSO-数字资产/04-模板/HTML'
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'}
VIDEO_SUFFIXES = {'.mp4', '.webm', '.mov', '.m4v'}


def build_review(manifest: Path, output: Path, make_zip: bool = False) -> dict:
    manifest = manifest.resolve()
    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
    kind = data.get('kind')
    if kind not in {'image', 'video'}:
        raise ValueError('kind must be image or video')
    items, process = data.get('items', []), data.get('process_images', [])
    if not isinstance(items, list) or not isinstance(process, list):
        raise ValueError('items and process_images must be lists')
    output = output.resolve()
    assets = output / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    emitted = []

    def save(value: str, stem: str, suffixes: set[str]) -> str:
        source = (manifest.parent / value).resolve()
        if source.suffix.lower() not in suffixes:
            raise ValueError(f'unsupported media type: {value}')
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = assets / (stem + source.suffix.lower())
        if source != destination:
            shutil.copyfile(source, destination)
        emitted.append(destination)
        return 'assets/' + destination.name

    def card(item: dict, index: int, media_kind: str, prefix: str) -> str:
        file = save(item['file'], f'{prefix}-{index:03d}', IMAGE_SUFFIXES if media_kind == 'image' else VIDEO_SUFFIXES)
        title = html.escape(str(item.get('title', f'作品 {index}')))
        caption = html.escape(str(item.get('caption', '')))
        if media_kind == 'image':
            media = f'<a href="{file}" target="_blank"><img loading="lazy" src="{file}" alt="{title}"></a>'
        else:
            poster = ''
            if item.get('poster'):
                poster = f' poster="{save(item["poster"], f"poster-{index:03d}", IMAGE_SUFFIXES)}"'
            media = f'<video controls playsinline preload="metadata"{poster} src="{file}"></video>'
        details = [label + '：' + str(item[key]) for key, label in [('model', '模型'), ('spec', '规格'), ('credits', '积分')] if key in item]
        meta = '<p class="meta">' + html.escape(' · '.join(details)) + '</p>' if details else ''
        return f'<section class="card {"movie" if media_kind == "video" else ""}">{media}<div class="text"><h2>{title}</h2><p class="caption">{caption}</p>{meta}<div class="links"><a href="{file}" target="_blank">查看原文件</a><a href="{file}" download>下载原文件</a></div></div></section>'

    cards = ''.join(card(item, i, kind, kind) for i, item in enumerate(items, 1))
    if not cards:
        cards = '<div class="empty">尚未加入作品。请在审阅清单的 items 中填写本次实际文件，再生成审阅页。</div>'
    process_html = ''
    if process:
        pictures = ''.join(card(item, i, 'image', 'process') for i, item in enumerate(process, 1))
        process_html = f'<section class="process"><h2>制作过程</h2><div class="grid">{pictures}</div></section>'
    template = (TEMPLATES / f'{kind}-review.html').read_text(encoding='utf-8')
    values = {
        'TITLE': html.escape(str(data.get('title', 'APPSO 作品审阅'))),
        'SUMMARY': html.escape(str(data.get('summary', ''))),
        'STYLE': (TEMPLATES / 'common.css').read_text(encoding='utf-8'),
        'CARDS': cards, 'PROCESS': process_html,
        'FOOTNOTE': html.escape(str(data.get('footnote', 'APPSO · 内部审阅'))),
    }
    for key, value in values.items():
        template = template.replace('{{' + key + '}}', value)
    page = output / 'index.html'
    page.write_text(template, encoding='utf-8')
    emitted.append(page)
    result = {'html': str(page), 'images_or_videos': len(items), 'process_images': len(process)}
    if make_zip:
        archive = output.parent / (output.name + '.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
            for file in emitted:
                bundle.write(file, file.relative_to(output).as_posix())
            bundle.writestr('阅读说明.txt', '完整解压后双击 index.html。保留 assets 文件夹，可离线查看和播放。\n')
        result['zip'] = str(archive)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--zip', action='store_true', dest='make_zip')
    args = parser.parse_args()
    try:
        result = build_review(args.manifest, args.output, args.make_zip)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'[fail] {error}\n')
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
