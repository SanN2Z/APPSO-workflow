#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the sourced Opta/LLM prediction timeline used in the article.

The chart is deliberately editorial rather than brand-mimicking: no Opta logo,
no copied layout, and no generative imagery. Run this file directly; it writes
the PNG to the package's assets directory.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


WIDTH = 1080
HEIGHT = 1900

INK = "#17202A"
TEXT = "#27313B"
MUTED = "#68727D"
LIGHT_MUTED = "#8A949E"
GRID = "#DDE2E7"
PANEL = "#F4F6F8"
WHITE = "#FFFFFF"
MAGENTA = "#D21870"
MAGENTA_SOFT = "#F9E8F0"

PACKAGE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PACKAGE_DIR / "assets" / "opta-spain-title-probability-timeline.png"

OPTA_POINTS = [
    {"date": "06.01", "stage": "赛前", "value": 16.1},
    {"date": "06.28", "stage": "小组赛后", "value": 13.5},
    {"date": "07.04", "stage": "16 强前", "value": 13.0},
    {"date": "07.08", "stage": "八强前", "value": 21.3},
    {"date": "07.12", "stage": "四强前", "value": 23.4},
    {"date": "07.19", "stage": "决赛前", "value": 59.5},
]

LLM_SNAPSHOTS = [
    {
        "date": "06.09",
        "source": "Tom's Guide",
        "detail": "ChatGPT · Gemini · Perplexity",
        "result": "西班牙  3 / 3",
    },
    {
        "date": "07.09",
        "source": "Tom's Guide",
        "detail": "ChatGPT、Perplexity 选法国；Gemini 选西班牙",
        "result": "法国 2　西班牙 1",
    },
    {
        "date": "07.14",
        "source": "Al Jazeera",
        "detail": "同题测试 9 个生成式 AI 模型",
        "result": "法国 5　阿根廷 4　西班牙 0",
    },
    {
        "date": "07.19",
        "source": "Financial Express",
        "detail": "Gemini 2:1（加时）；ChatGPT 1:0；Claude 2:1",
        "result": "西班牙  3 / 3",
    },
]


def font_path(*candidates: str) -> str:
    """Return the first available font path and fail loudly if none exist."""

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
LATIN_BOLD_FONT = font_path(
    "C:/Windows/Fonts/georgiab.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
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


def dashed_segment(
    draw: ImageDraw.ImageDraw,
    p1: tuple[float, float],
    p2: tuple[float, float],
    *,
    fill: str,
    width: int,
    dash: int = 18,
    gap: int = 11,
) -> None:
    """Draw one dashed line segment between two chart checkpoints."""

    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    ux = (x2 - x1) / length
    uy = (y2 - y1) / length
    cursor = 0.0
    while cursor < length:
        end = min(cursor + dash, length)
        draw.line(
            (
                x1 + ux * cursor,
                y1 + uy * cursor,
                x1 + ux * end,
                y1 + uy * end,
            ),
            fill=fill,
            width=width,
        )
        cursor += dash + gap


def centered_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text((x - (bbox[2] - bbox[0]) / 2, y), text, font=font, fill=fill)


def draw_title(draw: ImageDraw.ImageDraw) -> None:
    draw.text((72, 70), "从 16.1% 到 59.5%", font=fnt(67, True), fill=INK)
    draw.text((74, 158), "Opta 对西班牙夺冠率的 6 个公开节点", font=fnt(35, False), fill=TEXT)

    draw.line((74, 230, 1006, 230), fill=GRID, width=2)
    draw.text((74, 262), "OPTA 超级计算机", font=fnt(23, True), fill=MAGENTA)
    draw.text((314, 260), "每个节点均基于 25,000 次赛事模拟", font=fnt(24), fill=MUTED)


def draw_probability_chart(draw: ImageDraw.ImageDraw) -> None:
    left, right = 124, 968
    top, bottom = 360, 864
    max_value = 65.0

    for value in (0, 20, 40, 60):
        y = bottom - (value / max_value) * (bottom - top)
        draw.line((left, y, right, y), fill=GRID, width=2)
        label = f"{value}%"
        bbox = draw.textbbox((0, 0), label, font=fnt(22))
        draw.text((left - 18 - (bbox[2] - bbox[0]), y - 13), label, font=fnt(22), fill=LIGHT_MUTED)

    x_step = (right - left) / (len(OPTA_POINTS) - 1)
    coords: list[tuple[float, float]] = []
    for index, point in enumerate(OPTA_POINTS):
        x = left + index * x_step
        y = bottom - (point["value"] / max_value) * (bottom - top)
        coords.append((x, y))

    for start, end in zip(coords, coords[1:]):
        dashed_segment(draw, start, end, fill=MAGENTA, width=7)

    for index, ((x, y), point) in enumerate(zip(coords, OPTA_POINTS)):
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=WHITE, outline=MAGENTA, width=6)

        value_text = f"{point['value']:.1f}%"
        value_font = fnt(27, True)
        value_bbox = draw.textbbox((0, 0), value_text, font=value_font)
        pill_width = value_bbox[2] - value_bbox[0] + 28
        pill_height = 48

        # The last value sits above its point; the rest stay compact below/above
        # according to local slope so labels never collide with the line.
        if index == len(OPTA_POINTS) - 1:
            pill_y = y - 70
        elif index in (0, 3, 4):
            pill_y = y - 66
        else:
            pill_y = y + 22
        rounded_rect(
            draw,
            (int(x - pill_width / 2), int(pill_y), int(x + pill_width / 2), int(pill_y + pill_height)),
            radius=18,
            fill=MAGENTA if index == len(OPTA_POINTS) - 1 else WHITE,
            outline=MAGENTA,
            width=2,
        )
        centered_text(
            draw,
            (x, pill_y + 8),
            value_text,
            value_font,
            WHITE if index == len(OPTA_POINTS) - 1 else MAGENTA,
        )

        centered_text(draw, (x, 890), point["stage"], fnt(24, True), TEXT)
        centered_text(draw, (x, 929), point["date"], fnt(21), MUTED)

    # Explain the visually dominant jump without implying causal certainty.
    rounded_rect(draw, (704, 514, 960, 602), radius=16, fill=MAGENTA_SOFT)
    draw.text((727, 529), "进入决赛后", font=fnt(24, True), fill=MAGENTA)
    draw.text((727, 562), "+36.1 个百分点", font=fnt(25, True), fill=INK)

    draw.text(
        (74, 992),
        "公开留档节点；虚线仅辅助阅读，不代表连续实时变化。横轴按阶段等距。",
        font=fnt(22),
        fill=MUTED,
    )


def draw_llm_snapshots(draw: ImageDraw.ImageDraw) -> None:
    panel = (58, 1060, 1022, 1726)
    rounded_rect(draw, panel, radius=30, fill=PANEL)

    draw.text(
        (92, 1100),
        "媒体在不同阶段问 AI：「谁会夺冠？」",
        font=fnt(31, True),
        fill=INK,
    )

    timeline_x = 142
    row_top = 1175
    row_gap = 119
    draw.line(
        (timeline_x, row_top + 31, timeline_x, row_top + row_gap * 3 + 31),
        fill="#C7CDD3",
        width=4,
    )

    for index, snapshot in enumerate(LLM_SNAPSHOTS):
        y = row_top + index * row_gap
        draw.ellipse((timeline_x - 9, y + 22, timeline_x + 9, y + 40), fill=MAGENTA)
        draw.text((91, y + 53), snapshot["date"], font=fnt(20, True), fill=MUTED)

        rounded_rect(draw, (184, y, 984, y + 98), radius=18, fill=WHITE, outline="#E3E7EB", width=2)
        # Georgia's lowercase "l" has clear serifs, keeping "Al Jazeera"
        # visibly distinct from the misspelling "AI Jazeera" at phone size.
        source_font = (
            ImageFont.truetype(LATIN_BOLD_FONT, size=27)
            if snapshot["source"] == "Al Jazeera"
            else fnt(24, True)
        )
        draw.text((214, y + 16), snapshot["source"], font=source_font, fill=TEXT)
        draw.text((214, y + 55), snapshot["detail"], font=fnt(19), fill=MUTED)

        result_font = fnt(24, True)
        result_bbox = draw.textbbox((0, 0), snapshot["result"], font=result_font)
        result_width = result_bbox[2] - result_bbox[0] + 34
        result_left = 956 - result_width
        rounded_rect(
            draw,
            (result_left, y + 22, 956, y + 75),
            radius=18,
            fill=MAGENTA_SOFT if index == 0 else WHITE,
            outline=MAGENTA,
            width=2,
        )
        draw.text(
            (result_left + 17, y + 32),
            snapshot["result"],
            font=result_font,
            fill=MAGENTA if index == 0 else TEXT,
        )

    draw.text(
        (92, 1674),
        "不同媒体、提示词、模型版本与联网条件；仅记录公开回答。",
        font=fnt(20),
        fill=MUTED,
    )


def draw_footer(draw: ImageDraw.ImageDraw) -> None:
    draw.line((74, 1772, 1006, 1772), fill=GRID, width=2)
    draw.text(
        (74, 1801),
        "数据：Opta Analyst；媒体问答：Tom's Guide、Al Jazeera、Financial Express",
        font=fnt(21),
        fill=MUTED,
    )
    draw.text((74, 1841), "资料截至 2026.07.19｜Hunt Good", font=fnt(20), fill=LIGHT_MUTED)


def main() -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw_title(draw)
    draw_probability_chart(draw)
    draw_llm_snapshots(draw)
    draw_footer(draw)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT_PATH, format="PNG", optimize=True)
    print(f"[ok] wrote {OUTPUT_PATH} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
