"""只更新本目录的本地稿件索引；不修改稿件，不连接飞书。"""
from collections import Counter
from datetime import date
from pathlib import Path
import json
import yaml


def main():
    archive = Path(__file__).resolve().parent
    root = archive.parents[2]
    source = root / '微信公众号' / '内容'
    rows = []
    for path in sorted(source.rglob('draft.md')):
        content = path.read_text(encoding='utf-8-sig')
        metadata = {}
        note = ''
        if content.startswith('---'):
            try:
                parsed = yaml.safe_load(content.split('---', 2)[1])
                if not isinstance(parsed, dict):
                    raise ValueError('frontmatter is not a mapping')
                metadata = parsed
            except (ValueError, IndexError, yaml.YAMLError):
                note = 'frontmatter 无法解析，未改原稿'
        else:
            note = '无 frontmatter，标题暂用目录名'
        rows.append({
            'path': path.relative_to(root).as_posix(),
            'title': str(metadata.get('title') or path.parent.name),
            'status': str(metadata.get('status') or '未登记'),
            'published_url': str(metadata.get('published_url') or ''),
            'note': note,
        })
    counts = Counter(row['status'] for row in rows)
    lines = ['# 本地内容索引', '',
             f'更新：{date.today().isoformat()}。分级：internal。', '',
             f'扫描 `微信公众号/内容/` 下的 draft.md，共 {len(rows)} 份。状态直接读取 frontmatter，未重新验收，也未改变原稿。', '',
             '包含不同账号与选题，只用于找文件。与飞书目录可能重叠，不相加统计作品数量。标题按原文件保留。', '',
             '本次只索引 draft.md 的发布字段，未全量核读独立发布凭证；字段为空不等于未发表。', '',
             '| 原状态 | 数量 |', '|---|---|']
    lines += [f'| {state} | {count} |' for state, count in sorted(counts.items())]
    for month in sorted({row['path'].split('/')[3] for row in rows}, reverse=True):
        lines += ['', f'## {month} 月', '', '| 稿件 | 原状态 | 备注 |', '|---|---|---|']
        for row in rows:
            if row['path'].split('/')[3] != month:
                continue
            title = row['title'].replace('|', '\\|').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')
            note = row['note'] or ('已登记发布链接，未重新核查' if row['published_url'] else '发布链接未登记')
            lines.append(f"| [{title}](<../../../{row['path']}>) | {row['status']} | {note} |")
    (archive / '本地内容索引.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (archive / '本地索引快照.json').write_text(json.dumps({
        'checked_on': date.today().isoformat(), 'classification': 'internal',
        'scope': 'local draft.md metadata only', 'count': len(rows),
        'states': dict(counts), 'documents': rows,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'indexed': len(rows), 'states': dict(counts)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
