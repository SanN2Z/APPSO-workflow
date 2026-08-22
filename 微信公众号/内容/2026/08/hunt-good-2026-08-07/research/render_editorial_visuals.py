from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "research"
SOURCE = RESEARCH / "source-assets"
ASSETS = ROOT / "assets"

W, H = 1200, 675
BG = "#F6F4EF"
INK = "#171717"
MUTED = "#6D6A65"
ORANGE = "#FF4C00"
BLUE = "#3DAAD6"
PURPLE = "#DAD4F7"
PALE = "#E9E5DC"
WHITE = "#FFFFFF"

FONT_REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
FONT_MONO = Path("C:/Windows/Fonts/consola.ttf")


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono and FONT_MONO.exists() else (FONT_BOLD if bold else FONT_REGULAR)
    if not path.exists():
        raise FileNotFoundError(f"font missing: {path}")
    return ImageFont.truetype(str(path), size=size)


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (W, H), BG)
    return im, ImageDraw.Draw(im)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def label(draw: ImageDraw.ImageDraw, text: str, x: int = 64, y: int = 46) -> None:
    rounded(draw, (x, y, x + 220, y + 46), 23, INK)
    draw.text((x + 20, y + 10), text, font=font(20, bold=True), fill=WHITE)


def save(im: Image.Image, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    out = ASSETS / name
    im.save(out, format="PNG", optimize=True)
    print(f"[ok] {out.relative_to(ROOT)} {out.stat().st_size}")


def render_cover() -> None:
    im, d = canvas()
    label(d, "HUNT GOOD · 08.07")
    d.text((64, 130), "AI 把假靶场", font=font(68, bold=True), fill=INK)
    d.text((64, 220), "打成了真公司", font=font(68, bold=True), fill=INK)
    d.text((68, 330), "一周先进工具与 AI 新鲜事", font=font(28), fill=MUTED)

    # Test sandbox and the accidental path into the real world.
    rounded(d, (690, 100, 1125, 560), 30, WHITE, INK, 4)
    d.text((730, 135), "TEST SANDBOX", font=font(24, bold=True, mono=True), fill=INK)
    for y in (210, 290, 370):
        rounded(d, (740, y, 900, y + 72), 14, PALE)
        d.ellipse((765, y + 24, 785, y + 44), fill=BLUE)
        d.line((810, y + 27, 870, y + 27), fill=MUTED, width=4)
        d.line((810, y + 43, 855, y + 43), fill=MUTED, width=4)
    d.line((920, 140, 920, 520), fill=INK, width=5)
    for y in range(155, 515, 42):
        d.line((920, y, 920, min(y + 20, 515)), fill=BG, width=8)
    d.rectangle((907, 318, 934, 390), fill=BG)
    d.line((865, 354, 1015, 354), fill=ORANGE, width=12)
    d.polygon([(1015, 330), (1055, 354), (1015, 378)], fill=ORANGE)
    for i, x in enumerate((975, 1025, 1075)):
        d.rectangle((x, 410 - i * 18, x + 40, 500), fill=INK)
        for yy in range(430 - i * 18, 490, 24):
            d.rectangle((x + 10, yy, x + 18, yy + 8), fill=WHITE)
    d.ellipse((1037, 248, 1117, 328), fill=ORANGE)
    d.text((1077, 286), "3", font=font(42, bold=True), fill=WHITE, anchor="mm")
    d.text((1068, 540), "真实系统", font=font(24, bold=True), fill=ORANGE, anchor="mm")
    save(im, "cover-hunt-good-candidate.png")


def render_openai_price() -> None:
    im, d = canvas()
    label(d, "OPENAI API")
    d.text((64, 126), "Luna 发布 3 周，价格砍了 80%", font=font(54, bold=True), fill=INK)
    cards = [
        (64, 235, 560, 535, "输入 / 100 万 token", "$1", "$0.20"),
        (640, 235, 1136, 535, "输出 / 100 万 token", "$6", "$1.20"),
    ]
    for x1, y1, x2, y2, title, before, after in cards:
        rounded(d, (x1, y1, x2, y2), 26, WHITE, PALE, 3)
        d.text((x1 + 38, y1 + 32), title, font=font(25, bold=True), fill=MUTED)
        d.text((x1 + 42, y1 + 112), before, font=font(47, bold=True), fill="#A7A29A")
        d.line((x1 + 32, y1 + 146, x1 + 145, y1 + 146), fill=ORANGE, width=7)
        d.text((x1 + 188, y1 + 86), "→", font=font(58, bold=True), fill=INK)
        d.text((x1 + 285, y1 + 88), after, font=font(64, bold=True), fill=ORANGE)
    rounded(d, (64, 572, 1136, 630), 18, INK)
    d.text((600, 600), "降的是 API 调用价，不是 ChatGPT / Codex 订阅价", font=font(24, bold=True), fill=WHITE, anchor="mm")
    save(im, "02-openai-luna-price-card.png")


def render_deepseek() -> None:
    im, d = canvas()
    label(d, "USER REPORT")
    d.text((64, 126), "一道数学题，让模型想了 22 小时", font=font(52, bold=True), fill=INK)
    rounded(d, (64, 220, 1136, 548), 24, "#111318")
    d.ellipse((92, 246, 110, 264), fill="#FE5F57")
    d.ellipse((122, 246, 140, 264), fill="#FEBB2E")
    d.ellipse((152, 246, 170, 264), fill="#28C840")
    rounded(d, (850, 242, 1095, 286), 18, "#49221C")
    d.text((972, 264), "22h 25m 20s", font=font(22, bold=True, mono=True), fill="#FF8A6A", anchor="mm")
    d.text((98, 316), ">", font=font(29, bold=True, mono=True), fill=BLUE)
    d.text((142, 312), "almost done thinking...", font=font(29, mono=True), fill=WHITE)
    for i, x in enumerate((142, 190, 238)):
        d.ellipse((x, 372, x + 18, 390), fill=ORANGE if i == 0 else "#514E4A")
    d.text((98, 440), "没有回答   ·   没有报错   ·   没有超时", font=font(27, bold=True), fill="#D8D4CC")
    d.text((64, 587), "单一用户截图，不等于已确认的模型 Bug", font=font(25, bold=True), fill=ORANGE)
    save(im, "03-deepseek-22h-card.png")


def person(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: str, name: str) -> None:
    draw.ellipse((cx - 44, cy - 90, cx + 44, cy - 2), fill=color)
    rounded(draw, (cx - 72, cy + 4, cx + 72, cy + 150), 36, color)
    draw.text((cx, cy + 184), name, font=font(24, bold=True), fill=INK, anchor="mm")


def render_social_cost() -> None:
    im, d = canvas()
    label(d, "PAPER · 33 个小组")
    d.text((64, 126), "AI 说得最多，人类却更少互相搭话", font=font(50, bold=True), fill=INK)
    person(d, 220, 340, "#F0B8A4", "学生 A")
    person(d, 980, 340, "#9FC8E5", "学生 B")
    rounded(d, (465, 256, 735, 470), 70, PURPLE, INK, 3)
    d.text((600, 320), "AI", font=font(52, bold=True), fill=INK, anchor="mm")
    d.text((600, 385), "发言最多", font=font(31, bold=True), fill=ORANGE, anchor="mm")
    for y in (245, 278, 311):
        d.line((350, y, 440, y), fill=ORANGE, width=7)
        d.line((760, y, 850, y), fill=ORANGE, width=7)
    for x in range(330, 840, 36):
        d.line((x, 515, min(x + 16, 840), 515), fill="#BBB6AE", width=5)
    d.text((600, 556), "两名学生彼此回应更少", font=font(28, bold=True), fill=MUTED, anchor="mm")
    d.text((600, 620), "单次约 18 分钟文字讨论，不能外推到所有团队", font=font(23), fill=MUTED, anchor="mm")
    save(im, "08-ai-teammate-social-cost-card.png")


def render_transluce() -> None:
    im, d = canvas()
    label(d, "TRANSLUCE")
    d.text((64, 126), "面对知名 AI 从业者，Claude 会变一点", font=font(49, bold=True), fill=INK)
    items = [
        ("−1.4", "个百分点", "对自身行为的信心"),
        ("−1.5", "个百分点", "解决难题的信心"),
        ("−0.11", "/ 10 分", "给其他回答的评分"),
        ("+4.0", "个百分点", "启动推理的比例"),
    ]
    for i, (number, unit, caption) in enumerate(items):
        x = 64 + i * 276
        rounded(d, (x, 232, x + 248, 502), 24, WHITE, PALE, 3)
        d.text((x + 124, 318), number, font=font(55, bold=True), fill=ORANGE, anchor="mm")
        d.text((x + 124, 374), unit, font=font(21, bold=True), fill=MUTED, anchor="mm")
        d.multiline_text((x + 124, 446), caption, font=font(22, bold=True), fill=INK, anchor="mm", align="center", spacing=7)
    rounded(d, (64, 552, 1136, 626), 20, INK)
    d.text((600, 589), "研究者主动把姓名、邮箱和职业写进上下文；不是观察真实用户", font=font(23, bold=True), fill=WHITE, anchor="mm")
    save(im, "10-transluce-user-awareness-card.png")


def render_bonus() -> None:
    im, d = canvas()
    label(d, "彩蛋时间 · 本文制作")
    d.text((64, 132), "Harness 最重要的功能", font=font(55, bold=True), fill=INK)
    d.text((64, 218), "可能是劝模型及时认输。", font=font(55, bold=True), fill=ORANGE)
    rounded(d, (64, 340, 1136, 560), 28, "#111318")
    d.text((102, 392), "> almost done thinking...", font=font(31, mono=True), fill=WHITE)
    rounded(d, (824, 388, 1084, 500), 22, ORANGE)
    d.text((954, 444), "先停一下", font=font(35, bold=True), fill=WHITE, anchor="mm")
    d.text((102, 492), "elapsed: 22:25:20", font=font(25, mono=True), fill="#ABA8A2")
    d.text((64, 616), "温馨提示：持续思考不等于持续进展。", font=font(24), fill=MUTED)
    save(im, "13-bonus-harness-stop-card.png")


def process_image(source: Path, output_name: str, max_width: int = 1600, jpeg: bool = False) -> None:
    if not source.exists():
        raise FileNotFoundError(f"source image missing: {source}")
    ASSETS.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as im:
        im.load()
        if im.width > max_width:
            height = round(im.height * max_width / im.width)
            im = im.resize((max_width, height), Image.Resampling.LANCZOS)
        out = ASSETS / output_name
        if jpeg:
            im.convert("RGB").save(out, format="JPEG", quality=88, optimize=True, progressive=True)
        else:
            im.save(out, format="PNG", optimize=True)
    print(f"[ok] {out.relative_to(ROOT)} {out.stat().st_size}")


def process_official_images() -> None:
    mapping = [
        (SOURCE / "anthropic-cyber-evals-og.png", "01-anthropic-cyber-evals-official.png", 1600, False),
        (RESEARCH / "output/playwright/qwen-ecommerce-official.png", "04-qwen-ecommerce-official.png", 1200, False),
        (SOURCE / "rescript-ui-01.png", "05-rescript-ui-official.jpg", 1600, True),
        (SOURCE / "adomate-og.png", "06-adomate-official.png", 1200, False),
        (
            RESEARCH / "output/playwright/.playwright-cli/element-2026-08-07T03-05-08-865Z.png",
            "07-webhound-official.png",
            1200,
            False,
        ),
        (SOURCE / "conduit-10.jpg", "09-conduit-headset-official.jpg", 1200, True),
        (SOURCE / "gstack-dashboard.png", "11-gstack-dashboard-official.jpg", 1200, True),
        (SOURCE / "ioai-track-01.png", "12-ioai-model-track-official.jpg", 1200, True),
    ]
    for source, name, width, jpeg in mapping:
        process_image(source, name, max_width=width, jpeg=jpeg)


def main() -> None:
    render_cover()
    render_openai_price()
    render_deepseek()
    render_social_cost()
    render_transluce()
    render_bonus()
    process_official_images()


if __name__ == "__main__":
    main()
