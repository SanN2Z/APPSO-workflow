#!/usr/bin/env python3
"""Audit published content packages and due retrospective records."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


SKIP_PARTS = {".git", "node_modules", "dist", "output", "临时素材", "模板"}


def parse_frontmatter(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
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


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS or part.startswith(".") for part in path.parts)


def audit(root: Path, today: dt.date) -> list[str]:
    findings: list[str] = []
    for draft in root.rglob("draft.md"):
        relative = draft.relative_to(root)
        if should_skip(relative):
            continue
        metadata = parse_frontmatter(draft)
        if metadata.get("status") != "published":
            continue
        package = draft.parent
        record = package / "retrospective.md"
        if not record.is_file():
            findings.append(f"missing retrospective: {package.relative_to(root)}")
            continue
        review = parse_frontmatter(record)
        review_status = review.get("review_status", "open")
        next_review_raw = review.get("next_review_on", "")
        if review_status == "closed" or not next_review_raw:
            continue
        try:
            next_review = dt.date.fromisoformat(next_review_raw)
        except ValueError:
            findings.append(f"invalid next_review_on in {record.relative_to(root)}: {next_review_raw}")
            continue
        if next_review <= today:
            findings.append(
                f"review due since {next_review.isoformat()}: {package.relative_to(root)}"
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        findings = audit(root, args.today)
    except RuntimeError as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        return 1

    if not findings:
        print("[pass] no overdue published-content retrospectives")
        return 0
    for finding in findings:
        print(f"[due] {finding}")
    return 0 if args.report_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
