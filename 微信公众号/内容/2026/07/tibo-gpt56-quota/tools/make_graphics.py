# -*- coding: utf-8 -*-
"""Build deterministic, phone-readable WeChat article graphics with Pillow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


ROOT = Path(__file__).resolve().parents[1]
PUBLISH_ASSETS = ROOT / "assets"
PUBLISH_ASSETS.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = Path("C:/Windows/Fonts/NotoSansSC-VF.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/simhei.ttf")
FONT_LATIN_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")

NAVY = "#07111F"
INK = "#111827"
MUTED = "#596579"
BLUE = "#3478F6"
CYAN = "#26C6DA"
PURPLE = "#7759F3"
ORANGE = "#FF7A3D"
RED = "#F04459"
CREAM = "#F8F6F1"
GRID = "#DFE4EC"
WHITE = "#FFFFFF"


def font(size: int, bold: bool = False, latin: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_LATIN_BOLD if latin and bold else FONT_BOLD if bold else FONT_REGULAR
    if not path.is_file():
        raise FileNotFoundError(f"[fail] font missing: {path}")
    return ImageFont.truetype(str(path), size=size)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"[fail] expected six-digit color, got: {value}")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    top_rgb = hex_rgb(top)
    bottom_rgb = hex_rgb(bottom)
    image = Image.new("RGB", size)
    pixels = image.load()
    for y in range(height):
        ratio = y / max(height - 1, 1)
        row = tuple(
            round(top_rgb[channel] * (1 - ratio) + bottom_rgb[channel] * ratio)
            for channel in range(3)
        )
        for x in range(width):
            pixels[x, y] = row
    return image


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    fnt: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for character in text:
        if character == "\n":
            lines.append(current)
            current = ""
            continue
        candidate = current + character
        candidate_width = draw.textbbox((0, 0), candidate, font=fnt)[2]
        if current and candidate_width > max_width:
            lines.append(current)
            current = character
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int = 12,
) -> int:
    x, y = xy
    line_height = draw.textbbox((0, 0), "国Ag", font=fnt)[3]
    for line in wrap_text(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height + line_gap
    return y


def draw_pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: str,
    text_fill: str,
    *,
    size: int = 28,
    padding_x: int = 24,
    padding_y: int = 12,
    outline: str | None = None,
) -> tuple[int, int, int, int]:
    x, y = xy
    fnt = font(size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=fnt)
    width = bbox[2] + padding_x * 2
    height = bbox[3] + padding_y * 2
    box = (x, y, x + width, y + height)
    rounded(draw, box, height // 2, fill, outline=outline, width=2)
    draw.text((x + padding_x, y + padding_y - 2), text, font=fnt, fill=text_fill)
    return box


def save(image: Image.Image, name: str) -> None:
    path = PUBLISH_ASSETS / name
    image.save(path, format="PNG", optimize=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"[fail] image was not written: {path}")
    print(f"[ok] {path.name} {image.width}x{image.height} {path.stat().st_size} bytes")


def make_cover_v2() -> None:
    image = gradient((1080, 608), "#06101F", "#201740")
    draw = ImageDraw.Draw(image)

    # Abstract progress rings suggest a task interrupted mid-run without using logos.
    draw.ellipse((760, -205, 1190, 225), outline="#4D4593", width=4)
    draw.ellipse((825, -140, 1125, 160), outline="#2D79C9", width=3)
    draw.ellipse((935, 12, 989, 66), fill=ORANGE)
    draw.ellipse((1004, 132, 1040, 168), fill=CYAN)

    draw_pill(draw, (54, 38), "AI 圈今日份", "#10243A", "#A8DEFF", size=24, outline="#2E5774")
    draw.text((54, 132), "AI 模型再聪明", font=font(64, bold=True), fill=WHITE)
    draw.text((54, 215), "用到一半没额度", font=font(64, bold=True), fill="#E5EBFF")
    draw.text((54, 298), "也白搭", font=font(86, bold=True), fill="#FFAE67")

    rounded(draw, (785, 238, 1026, 462), 30, "#101A2D", outline="#596989", width=2)
    draw.text((817, 270), "任务进度", font=font(28, bold=True), fill="#DCE7FF")
    rounded(draw, (817, 335, 994, 365), 15, "#344056")
    rounded(draw, (817, 335, 927, 365), 15, BLUE)
    draw.text((817, 392), "额度已用尽", font=font(31, bold=True), fill="#FF8390")

    draw.line((54, 510, 1026, 510), fill="#45516B", width=2)
    draw.text((54, 535), "新的胜负手：任务能不能从开始一直做到交付", font=font(27, bold=True), fill="#C1CBDE")
    save(image, "cover-v2.png")


def make_timeline_v2() -> None:
    image = Image.new("RGB", (1080, 1420), CREAM)
    draw = ImageDraw.Draw(image)

    draw.text((56, 48), "时间接近，只能说明先后", font=font(52, bold=True), fill=INK)
    draw.text((56, 118), "不能替 Anthropic 补写动机", font=font(52, bold=True), fill=RED)
    draw.text((58, 195), "按锁定事实卡保留“约一小时后”的降级口径", font=font(30), fill=MUTED)

    line_x = 112
    draw.line((line_x, 320, line_x, 850), fill="#AEB7C6", width=8)

    draw.ellipse((82, 320, 142, 380), fill=BLUE)
    rounded(draw, (176, 286, 1018, 486), 26, WHITE, outline="#B8D2FF", width=3)
    draw_pill(draw, (210, 320), "预定开播", "#EAF2FF", BLUE, size=27)
    draw.text((210, 394), "7 月 9 日 10:00 PT / 17:00 UTC", font=font(39, bold=True), fill=INK)
    draw.text((210, 447), "GPT-5.6 / ChatGPT Work 发布直播", font=font(30), fill=MUTED)

    draw_pill(draw, (176, 515), "约一小时后", "#EEE9FF", "#553BAF", size=30)
    draw.line((112, 551, 168, 551), fill=PURPLE, width=4)

    draw.ellipse((82, 616, 142, 676), fill=RED)
    rounded(draw, (176, 582, 1018, 812), 26, WHITE, outline="#FFC0C7", width=3)
    draw_pill(draw, (210, 616), "ClaudeDevs reset 公告截图", "#FFF0F2", RED, size=27)
    draw.text((210, 690), "7 月 10 日 03:01（截图本地时间）", font=font(37, bold=True), fill=INK)
    draw.text((210, 747), "若截图使用 JST（UTC+9），换算约为 18:01 UTC", font=font(29), fill=MUTED)

    notes = [
        ("时区假设", "截图未标时区；上述换算只在截图使用 JST（UTC+9）的假设下成立。", "#EEF4FF", BLUE),
        ("上线节奏", "官方说明为 24 小时渐进 rollout，不能把开播时刻写成“广泛上线”。", "#F1EEFF", PURPLE),
        ("因果边界", "时间接近不证明 Anthropic 因这场发布会临时决定重置额度。", "#FFF0EC", RED),
    ]
    y = 900
    for title, body, fill, color in notes:
        rounded(draw, (56, y, 1024, y + 138), 24, fill)
        draw.text((86, y + 27), title, font=font(31, bold=True), fill=color)
        draw_wrapped(draw, (258, y + 24), body, font(28), INK, 730, line_gap=5)
        y += 164

    save(image, "timeline-v2.png")


def make_usable_intelligence_v2() -> None:
    image = Image.new("RGB", (1080, 1500), "#F4F7FB")
    draw = ImageDraw.Draw(image)

    draw.text((56, 48), "聪明是上限，能用是产品能力", font=font(52, bold=True), fill=INK)
    draw.text((58, 120), "“峰值能力”单列；后四项合称“可用智能”", font=font(30), fill=MUTED)

    rounded(draw, (56, 205, 1024, 410), 30, NAVY)
    draw_pill(draw, (90, 238), "能力上限", "#17355C", "#A8D7FF", size=27)
    draw.text((90, 304), "峰值能力", font=font(54, bold=True), fill=WHITE)
    draw.text((398, 316), "模型在合适配置下，会不会做", font=font(34), fill="#D6E4F8")

    draw.line((540, 410, 540, 480), fill="#94A3B8", width=5)
    draw.polygon([(540, 490), (525, 465), (555, 465)], fill="#94A3B8")
    draw.text((56, 505), "四个产品化条件｜决定能力能否稳定进入日常工作", font=font(38, bold=True), fill=INK)

    conditions = [
        ("可获得性", "现在拿不拿得到、谁能用", BLUE, "#EAF2FF"),
        ("工作连续性", "任务能否从开始一直做到交付", ORANGE, "#FFF1E8"),
        ("成本可预测性", "开工前能否大致估算最终花费", RED, "#FFF0F2"),
        ("入口占有", "是否进入每天打开的工作台", PURPLE, "#F1EEFF"),
    ]
    positions = [(56, 600), (550, 600), (56, 865), (550, 865)]
    for index, ((title, body, color, fill), (x, y)) in enumerate(zip(conditions, positions), start=1):
        rounded(draw, (x, y, x + 474, y + 225), 28, WHITE, outline=color, width=4)
        draw.ellipse((x + 30, y + 30, x + 86, y + 86), fill=fill, outline=color, width=3)
        draw.text((x + 58, y + 40), str(index), font=font(24, bold=True), fill=color, anchor="ma")
        draw.text((x + 30, y + 108), title, font=font(40, bold=True), fill=INK)
        draw_wrapped(draw, (x + 30, y + 164), body, font(28), MUTED, 414, line_gap=6)

    rounded(draw, (56, 1162, 1024, 1438), 30, WHITE, outline="#CBD5E1", width=2)
    draw_pill(draw, (88, 1195), "编辑分析框架", "#FFF3E8", "#A84E1B", size=27)
    draw.text((88, 1270), "不是学术公式，也不把峰值能力塞进四条件", font=font(37, bold=True), fill=INK)
    draw.text((88, 1330), "本次额度 reset 主要落在“工作连续性”，也短暂影响可获得性。", font=font(29), fill=MUTED)
    draw.text((88, 1380), "四项一起回答：这份能力能不能稳定变成用户的日常产出？", font=font(29), fill=MUTED)
    save(image, "usable-intelligence-v2.png")


def make_api_pricing_v2() -> None:
    image = Image.new("RGB", (1080, 1500), WHITE)
    draw = ImageDraw.Draw(image)

    draw.text((56, 48), "四档公开单价，先看清口径", font=font(52, bold=True), fill=INK)
    draw.text((58, 120), "标准短上下文 API 价｜美元 / 每百万 token", font=font(31), fill=MUTED)

    draw.text((630, 210), "输入", font=font(31, bold=True), fill=MUTED, anchor="ma")
    draw.text((870, 210), "输出", font=font(31, bold=True), fill=MUTED, anchor="ma")
    draw.line((56, 258, 1024, 258), fill=GRID, width=3)

    models = [
        ("GPT-5.6 Luna", 1, 6, BLUE, "#EAF2FF"),
        ("GPT-5.6 Terra", 2.5, 15, "#4F6FE6", "#EEF0FF"),
        ("GPT-5.6 Sol", 5, 30, PURPLE, "#F1EEFF"),
        ("Claude Fable 5", 10, 50, ORANGE, "#FFF1E8"),
    ]
    row_y = 285
    for model, input_price, output_price, color, fill in models:
        rounded(draw, (56, row_y, 1024, row_y + 190), 28, "#FAFBFD", outline=GRID, width=2)
        draw.ellipse((90, row_y + 58, 146, row_y + 114), fill=color)
        draw.text((174, row_y + 55), model, font=font(36, bold=True), fill=INK)
        rounded(draw, (548, row_y + 42, 712, row_y + 142), 22, fill)
        rounded(draw, (788, row_y + 42, 972, row_y + 142), 22, fill)
        draw.text((630, row_y + 62), f"${input_price:g}", font=font(43, bold=True), fill=color, anchor="ma")
        draw.text((880, row_y + 62), f"${output_price:g}", font=font(43, bold=True), fill=color, anchor="ma")
        row_y += 215

    rounded(draw, (56, 1175, 1024, 1438), 30, "#F5F7FA")
    draw.text((88, 1210), "两个不能省的限定", font=font(35, bold=True), fill=INK)
    draw.text((88, 1274), "① 长上下文，以及缓存、Batch / Flex / Priority 等（如适用）另算。", font=font(29), fill=MUTED)
    draw.text((88, 1330), "② 单价 ≠ 完成任务的总成本。重试、工具调用、等待和验收都会改账单。", font=font(29), fill=MUTED)
    draw_pill(draw, (88, 1380), "只比较公开单价，不宣布总成本胜负", "#FFF0EC", "#A84025", size=25)
    save(image, "api-pricing-v2.png")


def make_benchmark_split_v2() -> None:
    image = Image.new("RGB", (1080, 1780), WHITE)
    draw = ImageDraw.Draw(image)

    draw.text((48, 42), "OpenAI 发布表：六项并不指向同一赢家", font=font(48, bold=True), fill=INK)
    draw.text((50, 112), "厂商汇总表｜每行只比较该行所列配置", font=font(30), fill=MUTED)
    draw_pill(draw, (50, 170), "GPT-5.6", "#EAF2FF", BLUE, size=25)
    draw_pill(draw, (256, 170), "Claude", "#FFF1E8", ORANGE, size=25)

    rows = [
        ("AA Intelligence Index v4.1", "Sol", 58.9, "Fable 5", 59.9),
        ("Terminal-Bench 2.1", "Sol Ultra", 91.9, "Mythos 5", 88.0),
        ("BrowseComp", "Sol Ultra", 92.2, "Mythos 5", 88.0),
        ("FrontierMath Tier 4", "Sol", 83.0, "Fable 5", 87.8),
        ("SWE-Bench Pro*", "Sol", 64.6, "Mythos 5", 80.3),
        ("HealthBench Professional（注）", "Sol", 60.5, "Fable 5", 60.9),
    ]
    y = 260
    for benchmark, gpt_config, gpt_score, claude_config, claude_score in rows:
        rounded(draw, (48, y, 1032, y + 185), 24, "#FAFBFD", outline=GRID, width=2)
        draw.text((78, y + 25), benchmark, font=font(34, bold=True), fill=INK)
        draw.text((78, y + 90), f"GPT  ·  {gpt_config}", font=font(29, bold=True), fill=BLUE)
        draw.text((690, y + 83), f"{gpt_score:g}", font=font(43, bold=True), fill=BLUE)
        draw.text((78, y + 137), f"Claude  ·  {claude_config}", font=font(29, bold=True), fill=ORANGE)
        draw.text((690, y + 130), f"{claude_score:g}", font=font(43, bold=True), fill=ORANGE)
        if gpt_score > claude_score:
            draw_pill(draw, (830, y + 88), "本行 GPT 较高", "#EAF2FF", BLUE, size=22)
        else:
            draw_pill(draw, (805, y + 88), "本行 Claude 较高", "#FFF1E8", ORANGE, size=22)
        y += 205

    rounded(draw, (48, 1508, 1032, 1720), 26, "#FFF4EA", outline="#FFD4B5", width=2)
    draw.text((76, 1536), "口径边界", font=font(30, bold=True), fill="#A64D1D")
    draw.text((242, 1536), "混合 Sol / Sol Ultra、Fable / Mythos 与不同 tool / effort；", font=font(27), fill=INK)
    draw.text((76, 1583), "不可合并、横向求和，不能据此推出“全面胜负”。", font=font(27, bold=True), fill=INK)
    draw.text((76, 1627), "* OpenAI 审计估计约 30% 任务可能有问题，建议谨慎审视。", font=font(25), fill=MUTED)
    draw.text((76, 1663), "注：该行官方 scoring 与 Anthropic system card 报告不可直接比较。", font=font(25), fill=MUTED)
    save(image, "benchmark-split-v2.png")


def make_swebench_warning_v2() -> None:
    image = gradient((1080, 1320), "#260A11", "#551625")
    draw = ImageDraw.Draw(image)

    draw_pill(draw, (56, 48), "OpenAI 对公开任务集的审计", "#4A1520", "#FFBEC5", size=26, outline="#9D4658")
    draw.text((56, 128), "SWE-Bench Pro", font=font(57, bold=True), fill=WHITE)
    draw.text((56, 205), "约 30% 任务可能有问题", font=font(55, bold=True), fill="#FFAFB8")
    draw.text((58, 280), "这是参赛厂商自查，不是外部独立审计", font=font(30), fill="#E9C8CE")

    rounded(draw, (56, 370, 1024, 626), 30, "#47121D", outline="#9D4658", width=3)
    draw.text((92, 408), "200 / 731", font=font(63, bold=True, latin=True), fill="#FFD0D5")
    draw.text((710, 419), "27.4%", font=font(54, bold=True, latin=True), fill="#FF99A5")
    draw.text((92, 504), "datapoint pipeline 标出的问题任务", font=font(34), fill=WHITE)
    draw.text((92, 557), "按分析流程识别，不等于人工逐项复核", font=font(27), fill="#E8BCC4")

    rounded(draw, (56, 664, 1024, 920), 30, "#47121D", outline="#9D4658", width=3)
    draw.text((92, 702), "249 / 731", font=font(63, bold=True, latin=True), fill="#FFD0D5")
    draw.text((710, 713), "34.1%", font=font(54, bold=True, latin=True), fill="#FF99A5")
    draw.text((92, 798), "人工标注活动标出的问题任务", font=font(34), fill=WHITE)
    draw.text((92, 851), "不要写成“独立人工标注”", font=font(27), fill="#E8BCC4")

    rounded(draw, (56, 978, 1024, 1248), 30, "#FFF0F2")
    draw.text((90, 1015), "该怎么读？", font=font(35, bold=True), fill="#9B2438")
    draw.text((90, 1080), "审计估计约 30% 任务有破损问题，并建议开发者谨慎审视结果。", font=font(30), fill=INK)
    draw.text((90, 1138), "它不会自动抹掉任一模型的原始分数；原文也没有说“撤回推荐”。", font=font(30), fill=INK)
    draw.text((90, 1196), "结论：保留分数，同时把题集缺陷写进限制。", font=font(30, bold=True), fill="#7F1D2D")
    save(image, "swebench-warning-v2.png")


def validate_inputs() -> None:
    required = [FONT_REGULAR, FONT_BOLD, FONT_LATIN_BOLD]
    missing = [path for path in required if not path.is_file()]
    if missing:
        joined = "\n".join(f"[fail] required input missing: {path}" for path in missing)
        raise FileNotFoundError(joined)
    if not PUBLISH_ASSETS.is_dir():
        raise NotADirectoryError(f"[fail] publish asset directory missing: {PUBLISH_ASSETS}")
    print(f"[ok] graphics inputs valid; publish_dir={PUBLISH_ASSETS}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate fonts and output directory without writing images",
    )
    args = parser.parse_args()

    validate_inputs()
    if args.check:
        return

    make_cover_v2()
    make_timeline_v2()
    make_usable_intelligence_v2()
    make_api_pricing_v2()
    make_benchmark_split_v2()
    make_swebench_warning_v2()


if __name__ == "__main__":
    main()
