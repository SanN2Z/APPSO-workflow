#!/usr/bin/env python3
"""Flag likely date-led news ledes in WeChat analytical drafts.

This is a narrow heuristic for PROJECT-WECHAT-OPENING-001. It does not judge
writing quality and supports an explicit semantic exception when time itself is
the article's causal pressure.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TIME_EXPR = (
    r"(?:"
    r"\d{4}\s*年(?:\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?)?"
    r"|\d{1,2}\s*月\s*\d{1,2}\s*日"
    r"|今天|昨日|昨天|今早|今晨|当日|当天|当地时间|北京时间"
    r"|近日|日前|本周|上周|同一天|刚刚"
    r")"
)

TIME_FIRST_RE = re.compile(rf"^{TIME_EXPR}(?:[，,：:\s]|$)")
SUBJECT_TIME_ACTION_RE = re.compile(
    rf"^[^。！？\n]{{1,36}}?(?:在|于)\s*{TIME_EXPR}[^。！？\n]{{0,20}}?"
    r"(?:发布|宣布|公告|表示|称|披露|报道|推出|上线)"
)

ANALYTICAL_TYPES = {"analytical", "analysis", "l2", "l3"}
DIRECT_NEWS_TYPES = {"quicknews", "status", "notice", "l1"}


@dataclass(frozen=True)
class OpeningResult:
    status: str
    reason: str
    paragraph: str


def first_prose_paragraph(markdown: str) -> str:
    """Return the first visible prose paragraph, skipping metadata and media."""

    text = re.sub(r"(?s)<!--.*?-->", "", markdown).lstrip("\ufeff")
    lines = text.splitlines()

    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                lines = lines[index + 1 :]
                break

    paragraph: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#") or line.startswith("![") or line == "---":
            continue
        if re.match(r"^\*?图[：:]", line):
            continue
        paragraph.append(line.lstrip("> "))

    return " ".join(paragraph).strip()


def evaluate_opening(
    markdown: str,
    *,
    content_type: str = "analytical",
    exception_reason: str = "",
) -> OpeningResult:
    """Evaluate one draft using the rule's narrow machine-detectable signals."""

    paragraph = first_prose_paragraph(markdown)
    normalized_type = content_type.strip().lower()

    if normalized_type in DIRECT_NEWS_TYPES:
        return OpeningResult("allow", "direct_news_exception", paragraph)
    if normalized_type not in ANALYTICAL_TYPES:
        return OpeningResult("allow", "out_of_scope", paragraph)
    if not paragraph:
        return OpeningResult("flag", "missing_first_prose_paragraph", paragraph)

    reason = ""
    if TIME_FIRST_RE.search(paragraph):
        reason = "time_marker_leads_first_prose_paragraph"
    elif SUBJECT_TIME_ACTION_RE.search(paragraph):
        reason = "subject_time_announcement_lede"

    if not reason:
        return OpeningResult("allow", "no_date_led_lede_detected", paragraph)
    if exception_reason.strip():
        return OpeningResult("allow", f"time_first_exception: {exception_reason.strip()}", paragraph)
    return OpeningResult("flag", reason, paragraph)


def _format_preview(paragraph: str, limit: int = 100) -> str:
    compact = re.sub(r"\s+", " ", paragraph)
    return compact if len(compact) <= limit else compact[: limit - 1] + "…"


def check_paths(
    paths: Iterable[Path],
    *,
    content_type: str,
    exception_reason: str,
) -> int:
    flagged = 0
    for path in paths:
        result = evaluate_opening(
            path.read_text(encoding="utf-8"),
            content_type=content_type,
            exception_reason=exception_reason,
        )
        if result.status == "flag":
            flagged += 1
        print(
            f"[{result.status}] {path}: {result.reason}; "
            f"first_paragraph={_format_preview(result.paragraph)!r}"
        )
    return 1 if flagged else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check WeChat analytical openings for date-led news ledes."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--content-type", default="analytical")
    parser.add_argument(
        "--allow-time-first",
        default="",
        metavar="REASON",
        help="Narrow exception when time itself is the causal pressure.",
    )
    args = parser.parse_args()
    return check_paths(
        args.paths,
        content_type=args.content_type,
        exception_reason=args.allow_time_first,
    )


if __name__ == "__main__":
    raise SystemExit(main())
