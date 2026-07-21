#!/usr/bin/env python3
"""Create a structured retrospective.md in a content package."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"\'')
    return values


def build_record(package: Path, review_kind: str, today: dt.date) -> str:
    draft = package / "draft.md"
    if not draft.is_file():
        raise FileNotFoundError(f"missing draft.md: {package}")
    metadata = parse_frontmatter(draft.read_text(encoding="utf-8-sig"))
    next_review = today + dt.timedelta(days=7)
    title = metadata.get("title", package.name).replace('"', "'")
    platform = metadata.get("platform", "unknown")
    source_status = metadata.get("status", "unknown")
    return f'''---
schema_version: 1
content_id: "{package.name}"
title: "{title}"
platform: "{platform}"
source_status: "{source_status}"
review_kind: "{review_kind}"
review_status: "open"
created: {today.isoformat()}
updated: {today.isoformat()}
next_review_on: {next_review.isoformat()}
sop_promotions: 0
---

# 内容复盘：{title}

## 本轮结果

- 交付或发布日期：
- 最终版本或链接：
- 目标是否兑现：
- 可用数据与口径：

## 证据清单

- brief：`brief.md`
- 写作真源：`draft.md`
- 发布记录：`publish-record.md`
- 用户与编辑反馈：
- 初稿、交付稿、最终稿 diff：

## 反馈台账

| ID | 来源 / 日期 | 阶段 | 反馈或受限原路径 | 要求修改 | 读者 / 业务损失 | 根因 | 修复与版本 | 验证 | 分级 | 去向 |
|---|---|---|---|---|---|---|---|---|---|---|
| FB-001 |  |  |  |  |  |  |  |  | internal | watch |

## 因果复盘

```text
观察到的问题
→ 读者或流程损失
→ 根因机制
→ 实际修复
→ 验证证据
→ 适用范围与反例
```

## 经验分级

### 仅保留在本案例

- （待填写）

### 继续观察

- （待填写）

### SOP 候选

- （待填写）

## SOP 变更

| 规则 ID | 真源 SOP | 触发条件 | 动作 | 通过标准 | 来源案例 | 回归检查 | 结果 |
|---|---|---|---|---|---|---|---|

## 下一轮动作

- [ ] （待填写）

## 未解决问题

- （待填写）
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument(
        "--review-kind",
        choices=("post_publish", "delivery", "feedback", "weekly", "monthly"),
        default="post_publish",
    )
    parser.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    package = args.package.resolve()
    target = package / "retrospective.md"
    if target.exists():
        print(f"[skip] already exists: {target}")
        return 0

    try:
        record = build_record(package, args.review_kind, args.today)
    except (OSError, UnicodeError) as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(record)
        return 0

    target.write_text(record, encoding="utf-8", newline="\n")
    print(f"[created] {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
