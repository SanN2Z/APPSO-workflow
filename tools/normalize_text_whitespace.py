#!/usr/bin/env python3
"""Normalize whitespace only in files reported by git diff --check."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".py",
    ".ps1",
    ".cmd",
    ".csv",
    ".svg",
}


def diff_check(staged: bool) -> subprocess.CompletedProcess[str]:
    command = ["git", "diff"]
    if staged:
        command.append("--cached")
    command.append("--check")
    return subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8")


def issue_paths(output: str) -> list[Path]:
    paths: set[Path] = set()
    for line in output.splitlines():
        match = re.match(r"^(.+?):\d+: (?:trailing whitespace|new blank line at EOF)\.$", line)
        if match:
            paths.add(Path(match.group(1)))
    return sorted(paths, key=lambda path: str(path))


def normalize(text: str) -> str:
    lines = [line.rstrip(" \t") for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Inspect the staged diff.")
    parser.add_argument("--fix", action="store_true", help="Rewrite affected UTF-8 text files.")
    args = parser.parse_args()

    result = diff_check(args.staged)
    paths = issue_paths(result.stdout)
    unsupported = [path for path in paths if path.suffix.lower() not in TEXT_SUFFIXES]
    if unsupported:
        for path in unsupported:
            print(f"[skip] unsupported text type: {path}", file=sys.stderr)
        return 1

    if not paths:
        print("[pass] no whitespace issues")
        return 0
    if not args.fix:
        for path in paths:
            print(path)
        return 1

    changed = 0
    for path in paths:
        try:
            original = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            print(f"[fail] cannot read {path}: {exc}", file=sys.stderr)
            return 1
        updated = normalize(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
            print(f"[fixed] {path}")
    print(f"[pass] normalized {changed} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
