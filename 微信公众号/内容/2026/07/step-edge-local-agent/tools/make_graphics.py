# -*- coding: utf-8 -*-
"""Generate deterministic, project-owned graphics for the Step Edge article."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = Path("C:/Windows/Fonts/NotoSansSC-VF.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/simhei.ttf")

NAVY = "#07111F"
INK = "#121826"
MUTED = "#5F6B7A"
WHITE = "#FFFFFF"
CREAM = "#F6F7F2"
BLUE = "#3D7BFA"
CYAN = "#2CC7C9"
PURPLE = "#7B61FF"
ORANGE = "#FF8A4C"
GREEN = "#30B878"
RED = "#ED5565"
LINE = "#D7DEE8"


def get_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    if not path.is_file():
        raise FileNotFoundError(f"[fail] font missing: {path}")
    return ImageFont.truetype(str(path), size=size)


def rgb(value: str) -> tuple[int, int, int]:
    raw = value.lstrip("#")
    if len(raw) != 6:
        raise ValueError(f"[fail] invalid color: {value}")
    return tuple(int(raw[index : index + 2], 16) for index in (0, 2, 4))


def make_gradient(size: tuple[int, int], top: str, bottom: str) -> Image.Image:
    width, height = size
    top_rgb = rgb(top)
    bottom_rgb = rgb(bottom)
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(
            round(top_rgb[channel] * (1 - ratio) + bottom_rgb[channel] * ratio)
            for channel in range(3)
        )
        draw.line((0, y, width, y), fill=color)
    return image


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    *,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_chars(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        if char == "\n":
            lines.append(current)
            current = ""
            continue
        candidate = current + char
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    *,
    gap: int = 10,
) -> int:
    x, y = xy
    line_height = draw.textbbox((0, 0), "国Ag", font=font)[3]
    for line in wrap_chars(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height + gap
    return y


def pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: str,
    text_fill: str,
    *,
    size: int = 25,
) -> tuple[int, int, int, int]:
    x, y = xy
    font = get_font(size, bold=True)
    text_box = draw.textbbox((0, 0), text, font=font)
    width = text_box[2] + 42
    height = text_box[3] + 24
    box = (x, y, x + width, y + height)
    rounded(draw, box, height // 2, fill)
    draw.text((x + 21, y + 8), text, font=font, fill=text_fill)
    return box


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    color: str,
    width: int = 5,
) -> None:
    draw.line((*start, *end), fill=color, width=width)
    x, y = end
    if abs(end[1] - start[1]) >= abs(end[0] - start[0]):
        direction = 1 if end[1] > start[1] else -1
        points = [(x, y), (x - 13, y - 20 * direction), (x + 13, y - 20 * direction)]
    else:
        direction = 1 if end[0] > start[0] else -1
        points = [(x, y), (x - 20 * direction, y - 13), (x - 20 * direction, y + 13)]
    draw.polygon(points, fill=color)


def save(image: Image.Image, filename: str) -> None:
    path = ASSETS / filename
    image.save(path, format="PNG", optimize=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"[fail] image missing after save: {path}")
    print(f"[ok] {path.name} {image.width}x{image.height} {path.stat().st_size} bytes")


def make_cover() -> None:
    image = make_gradient((1080, 608), "#06111F", "#182449")
    draw = ImageDraw.Draw(image)

    pill(draw, (55, 42), "12 小时科技雷达", "#163353", "#A8D9FF", size=23)
    draw.text((55, 132), "AI 手机的下一仗", font=get_font(63, bold=True), fill=WHITE)
    draw.text((55, 220), "让 Agent", font=get_font(76, bold=True), fill="#DDE8FF")
    draw.text((55, 312), "留在本地", font=get_font(86, bold=True), fill="#68E3CE")
    draw.text((58, 512), "从云端聊天，走向本地执行", font=get_font(30, bold=True), fill="#BBC8DE")

    # Phone outline and local execution loop. No vendor logos or product screenshots.
    rounded(draw, (760, 64, 1010, 545), 45, "#0C172B", outline="#8296BE", width=4)
    rounded(draw, (786, 108, 984, 503), 30, "#101F36", outline="#2E4F74", width=2)
    rounded(draw, (845, 82, 925, 93), 6, "#8799B9")
    draw.ellipse((821, 168, 949, 296), outline=CYAN, width=7)
    draw.ellipse((843, 190, 927, 274), outline="#215B69", width=3)
    draw.text((885, 207), "本地", font=get_font(31, bold=True), fill=WHITE, anchor="ma")
    nodes = [
        (836, 342, "看", BLUE),
        (916, 342, "听", PURPLE),
        (836, 420, "点", ORANGE),
        (916, 420, "验", GREEN),
    ]
    for x, y, label, color in nodes:
        draw.ellipse((x - 30, y - 30, x + 30, y + 30), fill=color)
        draw.text((x, y - 2), label, font=get_font(26, bold=True), fill=WHITE, anchor="mm")

    draw.ellipse((972, 18, 1054, 78), fill="#233655", outline="#6C7E9E", width=2)
    draw.text((1013, 47), "云", font=get_font(24, bold=True), fill="#C5D3EA", anchor="mm")
    draw.line((982, 77, 948, 140), fill="#60789C", width=3)
    save(image, "cover.png")


def make_edge_cloud_loop() -> None:
    image = Image.new("RGB", (1080, 1480), CREAM)
    draw = ImageDraw.Draw(image)

    draw.text((56, 52), "端侧 Agent，不是云模型的缩小版", font=get_font(50, bold=True), fill=INK)
    draw.text((58, 123), "它先接住高频的小动作，再把难题交给云端", font=get_font(30), fill=MUTED)

    rounded(draw, (56, 210, 1024, 940), 34, WHITE, outline="#B9CDE7", width=3)
    pill(draw, (88, 244), "手机本地", "#E8F2FF", BLUE, size=28)
    draw.text((88, 318), "1 个底座 + N 个专用模型", font=get_font(43, bold=True), fill=INK)

    # Central base model.
    rounded(draw, (288, 420, 792, 600), 30, "#10213A")
    draw.text((540, 467), "Step Edge", font=get_font(47, bold=True), fill=WHITE, anchor="ma")
    draw.text((540, 533), "文本 + 视觉底座", font=get_font(31), fill="#BBD1EE", anchor="ma")

    cards = [
        (88, 670, 350, 844, "Audio", "听懂声音 / 识别语音", PURPLE, "#F1EEFF"),
        (409, 670, 671, 844, "GUI", "看懂界面 / 定位并操作", ORANGE, "#FFF0E7"),
        (730, 670, 992, 844, "Gen", "本地生成 / 编辑图片", GREEN, "#EAF8F1"),
    ]
    for x1, y1, x2, y2, title, body, color, fill in cards:
        rounded(draw, (x1, y1, x2, y2), 24, fill, outline=color, width=3)
        draw.text(((x1 + x2) // 2, y1 + 47), title, font=get_font(34, bold=True), fill=color, anchor="ma")
        draw_wrapped(draw, (x1 + 22, y1 + 91), body, get_font(25), INK, x2 - x1 - 44, gap=5)
        arrow(draw, ((x1 + x2) // 2, y1 - 4), ((x1 + x2) // 2, 618), color="#8BA0BA", width=3)

    rounded(draw, (105, 874, 975, 918), 22, "#EAF7F5")
    draw.text((540, 895), "简单 / 高频 / 隐私敏感 → 尽量在本地闭环", font=get_font(28, bold=True), fill="#197B70", anchor="mm")

    arrow(draw, (540, 940), (540, 1040), color="#8694A7", width=5)
    pill(draw, (434, 958), "按任务路由", "#EEF1F5", MUTED, size=24)

    rounded(draw, (56, 1040, 1024, 1245), 34, "#0B1528")
    pill(draw, (88, 1074), "云端", "#243B63", "#BFD5FF", size=28)
    draw.text((88, 1141), "复杂推理 / 长链任务 / 大上下文", font=get_font(41, bold=True), fill=WHITE)
    draw.text((88, 1196), "本地不是替代云端，而是减少每一步都上云", font=get_font(29), fill="#BDCAE0")

    rounded(draw, (56, 1295, 1024, 1418), 26, "#FFF0EC", outline="#FFC1B0", width=2)
    draw.text((88, 1322), "口径提醒", font=get_font(28, bold=True), fill=RED)
    draw_wrapped(
        draw,
        (246, 1318),
        "官方写的是“低至 100ms 本地 toolcall”；\n不是整条任务在 100ms 内完成。",
        get_font(25),
        INK,
        730,
        gap=5,
    )
    save(image, "edge-cloud-loop.png")


def make_four_checks() -> None:
    image = Image.new("RGB", (1080, 1500), "#F3F6FA")
    draw = ImageDraw.Draw(image)

    draw.text((56, 52), "下一款 AI 手机，先问这四件事", font=get_font(52, bold=True), fill=INK)
    draw.text((58, 126), "别只看模型分数，先看它能不能把活稳稳做完", font=get_font(30), fill=MUTED)

    checks = [
        ("01", "离线时还能做什么？", "断网后能否继续看屏幕、听语音、调用本地工具，而不只是弹出“网络错误”。", BLUE, "#EAF2FF"),
        ("02", "能否跨应用完成闭环？", "不仅会告诉你点哪里，还能在授权后执行、读取结果，并接着完成下一步。", PURPLE, "#F1EEFF"),
        ("03", "出错能否确认和撤销？", "发送、付款、删除之前要能看见动作；点错后要能叫停、回滚或人工接管。", ORANGE, "#FFF0E7"),
        ("04", "真实设备扛得住吗？", "兼容机型、功耗、发热、内存、稳定性和云端回退，缺一项都可能让演示失真。", GREEN, "#EAF8F1"),
    ]
    y = 230
    for number, title, body, color, fill in checks:
        rounded(draw, (56, y, 1024, y + 260), 30, WHITE, outline=color, width=3)
        rounded(draw, (88, y + 42, 210, y + 164), 28, fill)
        draw.text((149, y + 102), number, font=get_font(39, bold=True), fill=color, anchor="mm")
        draw.text((246, y + 48), title, font=get_font(40, bold=True), fill=INK)
        draw_wrapped(draw, (246, y + 116), body, get_font(29), MUTED, 714, gap=8)
        y += 285

    rounded(draw, (56, 1388, 1024, 1450), 28, "#101C31")
    draw.text((540, 1418), "四问都答得上，才有资格从“会聊”走向“会办事”", font=get_font(28, bold=True), fill=WHITE, anchor="mm")
    save(image, "ai-phone-four-checks.png")


def main() -> None:
    make_cover()
    make_edge_cloud_loop()
    make_four_checks()
    expected = ["cover.png", "edge-cloud-loop.png", "ai-phone-four-checks.png"]
    missing = [name for name in expected if not (ASSETS / name).is_file()]
    if missing:
        raise RuntimeError(f"[fail] expected assets not generated: {missing}")
    print("[ok] all graphics generated")


if __name__ == "__main__":
    main()
