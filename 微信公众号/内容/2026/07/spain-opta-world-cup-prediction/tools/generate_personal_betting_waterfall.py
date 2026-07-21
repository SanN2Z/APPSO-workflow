#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the mobile-first waterfall chart for the author's betting record.

The figure is an original editorial chart. It deliberately distinguishes the
profit relative to the initial 1,000-yuan plan from return on cumulative stake,
and preserves the evidence limitation supplied with the audited ledger.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WIDTH = 1080
HEIGHT = 1680

BG = "#F7F6F1"
WHITE = "#FFFFFF"
INK = "#152438"
TEXT = "#2F3A46"
MUTED = "#6F7882"
LIGHT = "#E4E1D8"
GRID = "#DDD9CF"
GAIN = "#138A7B"
GAIN_SOFT = "#E2F2EE"
LOSS = "#D85A53"
LOSS_SOFT = "#F8E9E6"
NOTE = "#FFF2C7"

PACKAGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PACKAGE_DIR / "assets" / "personal-world-cup-betting-waterfall.png"

LEDGER = [
    ("八强初始票", Decimal("-397")),
    ("西班牙临时加注及 0 球票", Decimal("420")),
    ("后追加比分票", Decimal("-100")),
    ("第一组平 / 负对冲", Decimal("179")),
    ("第二组平 / 负对冲", Decimal("145")),
    ("半决赛：西班牙", Decimal("104.5")),
    ("半决赛：阿根廷", Decimal("390")),
]

INITIAL_PLAN = Decimal("1000")
TOTAL_STAKED = Decimal("2720")
TOTAL_RETURN = Decimal("3461.5")
NET_PROFIT = Decimal("741.5")


def font_path(*candidates: str) -> str:
    """Return the first usable font path; fail loudly if none exists."""

    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)
    raise FileNotFoundError(f"No usable font found in: {candidates}")


REGULAR_FONT = font_path(
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyh.ttf",
    "C:/Windows/Fonts/simhei.ttf",
)
BOLD_FONT = font_path(
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyhbd.ttf",
    "C:/Windows/Fonts/simhei.ttf",
)


def fnt(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_FONT if bold else REGULAR_FONT, size=size)


def rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def right_text(
    draw: ImageDraw.ImageDraw,
    right: int,
    y: int,
    value: str,
    *,
    font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    box = draw.textbbox((0, 0), value, font=font)
    draw.text((right - (box[2] - box[0]), y), value, font=font, fill=fill)


def fmt_amount(value: Decimal, *, signed: bool = False) -> str:
    if value == value.to_integral_value():
        number = f"{abs(int(value)):,}"
    else:
        number = f"{abs(value):,.1f}"
    if not signed:
        return number
    return ("+" if value > 0 else "-") + number


def validate_numbers() -> list[Decimal]:
    """Check every supplied total before any pixels are written."""

    if sum((amount for _, amount in LEDGER), Decimal("0")) != NET_PROFIT:
        raise ValueError("Ledger deltas do not sum to the audited net profit")
    if TOTAL_RETURN - TOTAL_STAKED != NET_PROFIT:
        raise ValueError("Total return minus cumulative stake must equal net profit")

    cumulative: list[Decimal] = []
    running = Decimal("0")
    for _, amount in LEDGER:
        running += amount
        cumulative.append(running)
    if cumulative[-1] != NET_PROFIT:
        raise ValueError("Final cumulative value does not match net profit")
    return cumulative


def draw_header(draw: ImageDraw.ImageDraw) -> None:
    draw.text((72, 62), "个人实战样本 · 世界杯", font=fnt(24, True), fill=GAIN)
    draw.text((72, 113), "这 741.5 元，是怎么累出来的？", font=fnt(54, True), fill=INK)
    draw.text((73, 188), "7 个已审计盈亏节点 · 单位：元", font=fnt(27), fill=MUTED)


def draw_summary(draw: ImageDraw.ImageDraw) -> None:
    card_y1, card_y2 = 254, 384
    left = 72
    gap = 18
    card_width = 300
    cards = [
        ("累计下注", "2,720", TEXT),
        ("总回款", "3,461.5", TEXT),
        ("净利", "+741.5", GAIN),
    ]
    for index, (label, value, color) in enumerate(cards):
        x1 = left + index * (card_width + gap)
        x2 = x1 + card_width
        rounded_rect(draw, (x1, card_y1, x2, card_y2), radius=22, fill=WHITE, outline=LIGHT, width=2)
        draw.text((x1 + 24, card_y1 + 19), label, font=fnt(22), fill=MUTED)
        draw.text((x1 + 23, card_y1 + 58), value, font=fnt(36, True), fill=color)

    rounded_rect(draw, (72, 414, 1008, 516), radius=20, fill=NOTE)
    draw.text((98, 436), "74.2% = 净利 ÷ 1,000 元最初方案额度", font=fnt(25, True), fill=INK)
    draw.text(
        (98, 474),
        "不是标准 ROI；若按 2,720 元累计下注简单计算，约为 27.3%",
        font=fnt(22),
        fill=TEXT,
    )


def draw_waterfall(draw: ImageDraw.ImageDraw, cumulative: list[Decimal]) -> None:
    draw.text((72, 570), "每一步如何改变累计盈亏", font=fnt(31, True), fill=INK)

    label_left = 72
    chart_left = 408
    # Reserve a dedicated right-hand column for cumulative labels. This keeps
    # the final +741.5 label clear of the last gain bar on a phone screen.
    chart_right = 860
    chart_top = 650
    row_gap = 91
    baseline = Decimal("-450")
    ceiling = Decimal("800")

    def x_for(value: Decimal) -> int:
        proportion = float((value - baseline) / (ceiling - baseline))
        return int(chart_left + proportion * (chart_right - chart_left))

    zero_x = x_for(Decimal("0"))
    chart_bottom = chart_top + row_gap * (len(LEDGER) - 1) + 48
    draw.line((zero_x, chart_top - 25, zero_x, chart_bottom), fill="#B7B3A9", width=3)

    for tick in (Decimal("-400"), Decimal("0"), Decimal("400"), Decimal("800")):
        x = x_for(tick)
        if tick != 0:
            draw.line((x, chart_top - 25, x, chart_bottom), fill=GRID, width=2)
        label = fmt_amount(tick, signed=tick != 0)
        box = draw.textbbox((0, 0), label, font=fnt(19))
        draw.text((x - (box[2] - box[0]) / 2, chart_top - 58), label, font=fnt(19), fill=MUTED)

    previous = Decimal("0")
    previous_end_x: int | None = None
    for index, ((label, delta), current) in enumerate(zip(LEDGER, cumulative), start=1):
        y = chart_top + (index - 1) * row_gap
        start_x = x_for(previous)
        end_x = x_for(current)
        left, right = sorted((start_x, end_x))
        color = GAIN if delta > 0 else LOSS
        soft_color = GAIN_SOFT if delta > 0 else LOSS_SOFT

        if previous_end_x is not None:
            draw.line((previous_end_x, y - row_gap + 33, start_x, y + 2), fill="#B7B3A9", width=2)

        rounded_rect(draw, (left, y + 4, max(left + 8, right), y + 38), radius=13, fill=color)
        draw.ellipse((end_x - 7, y + 14, end_x + 7, y + 28), fill=WHITE, outline=color, width=4)

        rounded_rect(draw, (label_left, y - 5, 377, y + 46), radius=14, fill=soft_color)
        draw.text((label_left + 16, y + 7), f"{index:02d}", font=fnt(20, True), fill=color)
        draw.text((label_left + 58, y + 7), label, font=fnt(20, True), fill=TEXT)

        delta_label = fmt_amount(delta, signed=True)
        delta_font = fnt(21, True)
        delta_box = draw.textbbox((0, 0), delta_label, font=delta_font)
        delta_width = delta_box[2] - delta_box[0] + 22
        pill_center = (left + right) // 2
        pill_left = max(chart_left, min(pill_center - delta_width // 2, chart_right - delta_width))
        rounded_rect(draw, (pill_left, y + 46, pill_left + delta_width, y + 79), radius=12, fill=WHITE, outline=color, width=2)
        draw.text((pill_left + 11, y + 49), delta_label, font=delta_font, fill=color)

        current_text = f"累计 {fmt_amount(current, signed=True)}"
        right_text(draw, 1008, y + 7, current_text, font=fnt(20, True), fill=TEXT)

        previous = current
        previous_end_x = end_x


def draw_result_and_notes(draw: ImageDraw.ImageDraw) -> None:
    rounded_rect(draw, (72, 1321, 1008, 1433), radius=23, fill=INK)
    draw.text((102, 1350), "最终累计净利", font=fnt(26), fill="#DCE4EC")
    right_text(draw, 976, 1336, "+741.5 元", font=fnt(46, True), fill=WHITE)

    draw.line((72, 1483, 1008, 1483), fill=GRID, width=2)
    draw.text((72, 1512), "口径", font=fnt(21, True), fill=INK)
    draw.text(
        (138, 1512),
        "累计下注为全部实购金额；总回款含本金；净利 = 总回款 − 累计下注。",
        font=fnt(20),
        fill=MUTED,
    )
    draw.text((72, 1552), "核验边界", font=fnt(21, True), fill=INK)
    draw.text(
        (182, 1552),
        "数据来自本地实购记录；仓库未含票根 / 支付流水，无法独立复核。",
        font=fnt(20),
        fill=MUTED,
    )
    draw.text(
        (72, 1602),
        "单轮样本只能说明本轮结果，不代表可复制的长期收益。",
        font=fnt(19),
        fill="#8A8175",
    )


def main() -> None:
    cumulative = validate_numbers()
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(canvas)

    draw_header(draw)
    draw_summary(draw)
    draw_waterfall(draw, cumulative)
    draw_result_and_notes(draw)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT_PATH, format="PNG", optimize=True)

    initial_ratio = NET_PROFIT / INITIAL_PLAN * Decimal("100")
    turnover_ratio = NET_PROFIT / TOTAL_STAKED * Decimal("100")
    print(f"[ok] ledger sum: {NET_PROFIT}")
    print(f"[ok] initial-plan ratio: {initial_ratio:.2f}%")
    print(f"[ok] cumulative-stake ratio: {turnover_ratio:.2f}%")
    print(f"[ok] wrote {OUTPUT_PATH} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
