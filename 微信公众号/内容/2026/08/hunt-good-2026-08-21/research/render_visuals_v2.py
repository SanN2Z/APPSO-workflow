from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ROOT / "research" / "source-assets"
REPO_ROOT = Path(__file__).resolve().parents[6]
APPSO_LOGO = (
    REPO_ROOT
    / "APPSO-数字资产"
    / "01-栏目与品牌"
    / "品牌视觉"
    / "原始资料"
    / "APPSO Logo 红底白字.png"
)

W, H = 1200, 720
BG = "#F6F2E9"
PAPER = "#FFFFFF"
INK = "#111111"
MUTED = "#6B665F"
LINE = "#DCD5C9"
RED = "#EC1700"
ORANGE = "#FC7C0A"
BLUE = "#356DF3"
TEAL = "#159D87"
PURPLE = "#7657D8"
YELLOW = "#FFD35A"
PALE_RED = "#FFE7E1"
PALE_ORANGE = "#FFF0DC"
PALE_BLUE = "#E9F0FF"
PALE_TEAL = "#E5F5F1"

FONT_REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")

FINAL_VISUALS = [
    "00-cover-v2.png",
    "01-stripe-openrouter-official.png",
    "02-amazon-prime-air-official.jpg",
    "03-pa-data-center-commonwealth.jpg",
    "04-google-marvell-v2.png",
    "05-cursor-origin-official-v2.png",
    "05b-cursor-origin-apps-official.png",
    "06-chatgpt-teens-official.png",
    "07-openai-zdr-v2.png",
    "08-gemini-37-flash-official.png",
    "09-openmotion-official.png",
    "10-kitbitz-official.webp",
    "11-chatgpt-ads-method-v2.png",
    "11b-chatgpt-ads-income-paper.png",
    "12-model-hypnosis-paper-fig1.png",
    "13-agent-coordination-paper-fig1.png",
    "13b-agent-coordination-paper-fig8.png",
    "14-cuda-island-author.jpg",
    "15-egg-v2.png",
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    if not path.is_file():
        raise FileNotFoundError(f"font missing: {path}")
    return ImageFont.truetype(str(path), size=size)


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    size = start
    while size > minimum:
        candidate = font(size, bold)
        if text_width(draw, text, candidate) <= max_width:
            return candidate
        size -= 1
    return font(minimum, bold)


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        trial = current + ch
        if not current or text_width(draw, trial, fnt) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    fnt: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int = 8,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_lines(draw, text, fnt, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y


def paste_logo(image: Image.Image, xy: tuple[int, int], height: int = 28) -> tuple[int, int]:
    if not APPSO_LOGO.is_file():
        raise FileNotFoundError(f"APPSO logo missing: {APPSO_LOGO}")
    with Image.open(APPSO_LOGO) as source:
        logo = source.convert("RGB")
        width = round(logo.width * height / logo.height)
        logo = logo.resize((width, height), Image.Resampling.LANCZOS)
    image.paste(logo, xy)
    return width, height


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, width: int = 5) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2 - 16, y2), fill=color, width=width)
    draw.polygon([(x2, y2), (x2 - 21, y2 - 12), (x2 - 21, y2 + 12)], fill=color)


def pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: str, text_fill: str = PAPER, size: int = 18) -> tuple[int, int]:
    x, y = xy
    fnt = font(size, True)
    box = draw.textbbox((0, 0), text, font=fnt)
    width = box[2] - box[0] + 30
    height = box[3] - box[1] + 18
    rounded(draw, (x, y, x + width, y + height), height // 2, fill)
    draw.text((x + 15, y + 9 - box[1]), text, font=fnt, fill=text_fill)
    return width, height


def editorial_base(section: str, index: str, title: str, deck: str, accent: str, source: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, W, 12), fill=accent)
    label = f"HUNT FOR {section.upper()}  ·  {index}"
    pill(draw, (52, 34), label, INK, PAPER, 16)
    title_font = fit_font(draw, title, 1096, 48, 38, True)
    draw.text((52, 96), title, font=title_font, fill=INK)
    deck_font = fit_font(draw, deck, 1096, 25, 21, False)
    draw.text((54, 158), deck, font=deck_font, fill=MUTED)
    draw.line((52, 668, 1148, 668), fill=LINE, width=2)
    paste_logo(image, (52, 682), 25)
    source_font = font(15)
    sw = text_width(draw, source, source_font)
    draw.text((1148 - sw, 685), source, font=source_font, fill=MUTED)
    return image, draw


def stat_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], number: str, label: str, accent: str, note: str = "") -> None:
    x1, y1, x2, y2 = box
    rounded(draw, box, 22, PAPER, LINE, 2)
    draw.rectangle((x1, y1, x1 + 8, y2), fill=accent)
    draw.text((x1 + 26, y1 + 18), number, font=font(34, True), fill=accent)
    draw.text((x1 + 28, y1 + 64), label, font=font(20, True), fill=INK)
    if note:
        draw.text((x1 + 28, y1 + 96), note, font=font(15), fill=MUTED)


def render_cover() -> None:
    image = Image.new("RGB", (W, H), "#F3EEE5")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 18, H), fill=RED)
    pill(draw, (58, 42), "HUNT GOOD · 2026.08.21", INK, PAPER, 17)
    paste_logo(image, (1040, 42), 28)
    draw.text((58, 126), "AI 开始争夺", font=font(66, True), fill=INK)
    draw.text((58, 208), "中间那一层", font=font(66, True), fill=RED)
    draw_wrapped(
        draw,
        "模型怎么被选择、代码住在哪里、芯片订单怎么结算，最后都落到电力与地方政治。",
        (62, 318),
        font(24),
        MUTED,
        520,
        10,
        3,
    )

    # A denser editorial stack replaces the previous node-and-circle illustration.
    x1, x2 = 650, 1145
    rounded(draw, (x1, 76, x2, 610), 30, INK)
    for gy in range(118, 590, 44):
        draw.line((x1 + 26, gy, x2 - 26, gy), fill="#282828", width=1)
    layers = [
        (112, "ROUTE", "OpenRouter", PURPLE),
        (214, "REPO", "Cursor Origin", BLUE),
        (316, "CHIP", "Google × Marvell", ORANGE),
        (418, "POWER", "Data centers", TEAL),
        (520, "VOTE", "Local politics", RED),
    ]
    for i, (y, code, name, accent) in enumerate(layers):
        left = x1 + 42 + i * 12
        right = x2 - 42 - (4 - i) * 10
        rounded(draw, (left, y, right, y + 74), 18, "#FAF7F0")
        draw.rectangle((left, y, left + 10, y + 74), fill=accent)
        draw.text((left + 30, y + 18), code, font=font(24, True), fill=INK)
        name_font = fit_font(draw, name, right - left - 210, 20, 16, False)
        nw = text_width(draw, name, name_font)
        draw.text((right - nw - 24, y + 22), name, font=name_font, fill=MUTED)
    draw.line((632, 610, 1148, 610), fill=RED, width=7)
    draw.text((62, 617), "7 NEWS  ·  3 TOOLS  ·  3 INSIGHTS  ·  1 FUN", font=font(19, True), fill=INK)
    image.save(ASSETS / "00-cover-v2.png", "PNG", optimize=True)


def render_wechat_cover() -> None:
    width, height = 1920, 818
    image = Image.new("RGB", (width, height), "#F3EEE5")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 22, height), fill=RED)
    pill(draw, (82, 66), "HUNT GOOD · 08.21", INK, PAPER, 22)
    draw.text((82, 180), "AI 开始争夺", font=font(94, True), fill=INK)
    draw.text((82, 300), "中间那一层", font=font(94, True), fill=RED)
    draw.text((88, 452), "路由 · 仓库 · 芯片 · 电力 · 选票", font=font(34, True), fill=MUTED)
    draw.text((88, 616), "7 NEWS   3 TOOLS   3 INSIGHTS   1 FUN", font=font(25, True), fill=INK)
    paste_logo(image, (82, 706), 34)
    x1, x2 = 1150, 1840
    rounded(draw, (x1, 72, x2, 742), 36, INK)
    rows = [
        (130, "01", "MODEL ROUTING", PURPLE),
        (246, "02", "CODE HOSTING", BLUE),
        (362, "03", "CUSTOM SILICON", ORANGE),
        (478, "04", "POWER & WATER", TEAL),
        (594, "05", "LOCAL POLITICS", RED),
    ]
    for i, (y, n, label, accent) in enumerate(rows):
        left = x1 + 48 + i * 16
        right = x2 - 48 - (4 - i) * 12
        rounded(draw, (left, y, right, y + 76), 18, "#FBF7EF")
        draw.rectangle((left, y, left + 10, y + 76), fill=accent)
        draw.text((left + 32, y + 19), n, font=font(24, True), fill=accent)
        draw.text((left + 102, y + 21), label, font=font(23, True), fill=INK)
    image.save(ASSETS / "00-cover-wechat-v2.png", "PNG", optimize=True)


def render_marvell() -> None:
    image, draw = editorial_base(
        "News",
        "04",
        "Google 没投 122 亿美元，它拿到的是订单解锁券",
        "采购越多，权证解锁越多；两个大数字不能混成一笔钱",
        ORANGE,
        "来源：Marvell 8-K；金额按条款乘算",
    )

    # Main mechanism: a three-step route with two clearly separated monetary meanings.
    rounded(draw, (52, 205, 1148, 466), 24, PAPER, LINE, 2)
    steps = [
        (78, 242, 328, 400, "01", "Google 下单", "Marvell 确认\n合格芯片收入", INK),
        (404, 242, 664, 400, "02", "每 $500M", "解锁 1 批\n绩效权证", ORANGE),
        (750, 242, 1118, 400, "03", "最多 240 批", "最晚延续到\nMarvell FY2033", PURPLE),
    ]
    for x1, y1, x2, y2, idx, heading, body, accent in steps:
        rounded(draw, (x1, y1, x2, y2), 20, "#FAF8F3", LINE, 2)
        draw.text((x1 + 20, y1 + 18), idx, font=font(17, True), fill=accent)
        draw.text((x1 + 20, y1 + 48), heading, font=font(28, True), fill=INK)
        draw.multiline_text((x1 + 20, y1 + 92), body, font=font(18), fill=MUTED, spacing=5)
    arrow(draw, (328, 321), (390, 321), ORANGE, 6)
    arrow(draw, (664, 321), (736, 321), ORANGE, 6)
    draw.text((82, 422), "另有约 136 万股：协议首年按季度解锁", font=font(18, True), fill=TEAL)

    stat_card(draw, (52, 490, 398, 636), "$120B", "若 240 批全部解锁", RED, "$500M × 240；是合格收入门槛")
    stat_card(draw, (427, 490, 773, 636), "58.97M", "最多可买入的股数", PURPLE, "含首年解锁与绩效解锁部分")
    stat_card(draw, (802, 490, 1148, 636), "≈ $12.18B", "全部行权的潜在对价", ORANGE, "$206.58 × 58.97M；不是当前投资")
    image.save(ASSETS / "04-google-marvell-v2.png", "PNG", optimize=True)


def render_zdr() -> None:
    image, draw = editorial_base(
        "News",
        "07",
        "两种存法，一种结果：看见风险，不看见原文",
        "Private Safety Processing 想把跨对话安全与零数据保留放在同一条链上",
        TEAL,
        "来源：OpenAI；方案仍处早期客户测试",
    )

    # Two storage paths feed the same automated detector.
    rounded(draw, (52, 205, 410, 490), 24, PAPER, LINE, 2)
    draw.text((78, 232), "内容存在哪里？", font=font(24, True), fill=INK)
    rounded(draw, (78, 282, 384, 360), 16, PALE_TEAL)
    draw.text((96, 296), "A  客户基础设施", font=font(21, True), fill=TEAL)
    draw.text((96, 330), "ZDR 部署：原文留在客户控制范围", font=font(15), fill=MUTED)
    rounded(draw, (78, 382, 384, 466), 16, PALE_BLUE)
    draw.text((96, 396), "B  OpenAI 存储", font=font(21, True), fill=BLUE)
    draw.text((96, 430), "内容加密；密钥仍由客户持有", font=font(15), fill=MUTED)

    rounded(draw, (488, 246, 792, 454), 26, INK)
    draw.text((520, 276), "自动系统", font=font(24, True), fill=PAPER)
    draw.text((520, 320), "跨相关交互", font=font(30, True), fill=YELLOW)
    draw.text((520, 362), "识别行为模式", font=font(30, True), fill=PAPER)
    draw.text((520, 412), "不是逐条人工看原文", font=font(16), fill="#CFC9BF")
    arrow(draw, (410, 350), (474, 350), TEAL, 6)

    rounded(draw, (870, 246, 1148, 454), 26, PALE_RED, RED, 3)
    draw.text((900, 274), "OpenAI 收到", font=font(21, True), fill=INK)
    draw.text((900, 320), "有限风险信号", font=font(31, True), fill=RED)
    draw.text((900, 371), "活动类型，而非提示词／回答", font=font(15), fill=MUTED)
    draw.text((900, 411), "员工没有客户密钥", font=font(16, True), fill=INK)
    arrow(draw, (792, 350), (856, 350), RED, 6)

    rounded(draw, (52, 518, 1148, 636), 22, "#171717")
    draw.text((82, 542), "客户仍可用自有系统调查告警，并选择是否提交材料申诉", font=font(23, True), fill=PAPER)
    draw.text((82, 587), "待回答：模式检测范围、误报处理、客户审计方式与技术白皮书细节", font=font(18), fill="#CFC9BF")
    image.save(ASSETS / "07-openai-zdr-v2.png", "PNG", optimize=True)


def render_ads_method() -> None:
    image, draw = editorial_base(
        "Insights",
        "01",
        "ChatGPT 广告审计：91 个帐号，先走完 5 步",
        "研究者注入的是地点代理信号，不是从平台拿到的真实用户标签",
        PURPLE,
        "来源：arXiv:2608.05008；计数采用论文摘要口径",
    )

    labels = [
        ("01", "3 × 3 人设", "3 组族裔线索\n× 3 个收入档", PURPLE),
        ("02", "双重定位", "住宅代理 IP\n+ 地点提示词", BLUE),
        ("03", "每天同题", "从 335 题中\n抽同一组 30 题", ORANGE),
        ("04", "同时抓取", "回答 · 广告\n页面截图", TEAL),
        ("05", "分两层比较", "是否首次曝光\n曝光后的广告率", RED),
    ]
    x_positions = [52, 277, 502, 727, 952]
    for i, ((idx, heading, body, accent), x) in enumerate(zip(labels, x_positions)):
        rounded(draw, (x, 226, x + 196, 430), 20, PAPER, LINE, 2)
        draw.text((x + 18, 247), idx, font=font(17, True), fill=accent)
        draw.text((x + 18, 284), heading, font=font(23, True), fill=INK)
        draw.multiline_text((x + 18, 334), body, font=font(17), fill=MUTED, spacing=6)
        if i < 4:
            arrow(draw, (x + 196, 328), (x + 217, 328), "#9B948A", 3)

    stats = [
        (52, "91", "模拟帐号"),
        (235, "14 天", "首次广告中位等待"),
        (484, "3000+", "广告（摘要口径）"),
        (731, "186", "广告主（摘要口径）"),
    ]
    for x, number, label in stats:
        draw.text((x, 472), number, font=font(31, True), fill=RED if x == 235 else INK)
        draw.text((x, 513), label, font=font(16), fill=MUTED)
    rounded(draw, (52, 557, 1148, 636), 18, INK)
    draw.text((76, 579), "关键不是只问『广告多不多』，而是分开看：谁会先看到，以及看到后有多频繁。", font=font(21, True), fill=PAPER)
    image.save(ASSETS / "11-chatgpt-ads-method-v2.png", "PNG", optimize=True)


def render_egg() -> None:
    image = Image.new("RGB", (W, 675), "#151515")
    draw = ImageDraw.Draw(image)
    pill(draw, (54, 44), "HUNT GOOD · EGG", ORANGE, INK, 17)
    paste_logo(image, (1032, 46), 27)
    draw.text((54, 116), "聊天框只是入口", font=font(55, True), fill=PAPER)
    draw.text((54, 188), "真正的争夺在基础设施里", font=font(55, True), fill="#FF6B32")
    draw.text((58, 277), "跟着成本走，也跟着控制权走。", font=font(24), fill="#BBB3A9")

    items = [
        (62, "ROUTE", "谁替请求选模型", PURPLE),
        (340, "REPO", "代码与 Agent 住哪", BLUE),
        (618, "CHIP", "订单换成多少算力", ORANGE),
        (896, "POWER", "最后由谁付电费", TEAL),
    ]
    for i, (x, title, body, accent) in enumerate(items):
        rounded(draw, (x, 360, x + 232, 518), 20, "#242424", "#3D3D3D", 2)
        draw.rectangle((x, 360, x + 232, 8 + 360), fill=accent)
        draw.text((x + 20, 386), f"0{i + 1}", font=font(17, True), fill=accent)
        draw.text((x + 20, 420), title, font=font(28, True), fill=PAPER)
        draw.text((x + 20, 470), body, font=font(17), fill="#C8C1B8")
        if i < 3:
            arrow(draw, (x + 232, 438), (x + 270, 438), "#665F57", 4)
    draw.line((54, 600, 1146, 600), fill="#393939", width=2)
    draw.text((54, 622), "下一期见。", font=font(20, True), fill=PAPER)
    draw.text((1028, 623), "非 AI 生成", font=font(15), fill="#8F877E")
    image.save(ASSETS / "15-egg-v2.png", "PNG", optimize=True)


def crop_and_save(source_name: str, output_name: str, box: tuple[int, int, int, int], max_width: int = 1600) -> None:
    source_path = SOURCE / source_name
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    with Image.open(source_path) as source:
        image = source.convert("RGB").crop(box)
        if image.width > max_width:
            height = round(image.height * max_width / image.width)
            image = image.resize((max_width, height), Image.Resampling.LANCZOS)
        image.save(ASSETS / output_name, "PNG", optimize=True)


def process_cursor_sources() -> None:
    mapping = [
        ("cursor-origin-settings.png", "05-cursor-origin-official-v2.png"),
        ("cursor-origin-apps.png", "05b-cursor-origin-apps-official.png"),
    ]
    for source_name, output_name in mapping:
        source_path = SOURCE / source_name
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        with Image.open(source_path) as source:
            image = ImageOps.fit(source.convert("RGB"), (1600, 900), method=Image.Resampling.LANCZOS, centering=(0.5, 0.47))
            image.save(ASSETS / output_name, "PNG", optimize=True)


def process_paper_figures() -> None:
    # Boxes were selected from locally rendered PDF pages after an original-resolution inspection.
    crop_and_save("ads-p03-03.png", "11-chatgpt-ads-method-paper.png", (710, 120, 1415, 1815), 1050)
    crop_and_save("ads-p06-06.png", "11b-chatgpt-ads-income-paper.png", (85, 70, 1450, 825), 1600)
    crop_and_save("hypnosis-p02-02.png", "12-model-hypnosis-paper-fig1.png", (150, 125, 1395, 585), 1600)
    crop_and_save("coord-p03-03.png", "13-agent-coordination-paper-fig1.png", (250, 130, 1140, 505), 1400)
    crop_and_save("coord-p13-13.png", "13b-agent-coordination-paper-fig8.png", (165, 120, 1350, 875), 1500)


def contact_sheet() -> None:
    paths = [ASSETS / name for name in FINAL_VISUALS]
    missing = [path.name for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing visuals: {missing}")
    columns = 3
    cell_w, cell_h = 500, 374
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "#D7D1C7")
    for i, path in enumerate(paths):
        cell = Image.new("RGB", (cell_w - 12, cell_h - 12), PAPER)
        with Image.open(path) as source:
            thumb = ImageOps.contain(source.convert("RGB"), (cell_w - 36, cell_h - 70), Image.Resampling.LANCZOS)
        cell.paste(thumb, ((cell.width - thumb.width) // 2, 8 + (cell_h - 78 - thumb.height) // 2))
        d = ImageDraw.Draw(cell)
        d.text((14, cell.height - 42), path.name, font=font(15), fill=INK)
        x = (i % columns) * cell_w + 6
        y = (i // columns) * cell_h + 6
        sheet.paste(cell, (x, y))
    sheet.save(ROOT / "research" / "contact-sheet-v2.png", "PNG", optimize=True)
    sheet.save(ROOT / "research" / "contact-sheet.png", "PNG", optimize=True)


def mobile_check(names: Iterable[str]) -> None:
    names = list(names)
    columns = 3
    cell_w, cell_h = 420, 360
    rows = (len(names) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "#D7D1C7")
    for i, name in enumerate(names):
        path = ASSETS / name
        with Image.open(path) as source:
            thumb = ImageOps.contain(source.convert("RGB"), (375, 300), Image.Resampling.LANCZOS)
        cell = Image.new("RGB", (400, 340), PAPER)
        cell.paste(thumb, ((400 - thumb.width) // 2, 8 + (300 - thumb.height) // 2))
        d = ImageDraw.Draw(cell)
        d.text((12, 312), name, font=font(14), fill=INK)
        x = (i % columns) * cell_w + 10
        y = (i // columns) * cell_h + 10
        sheet.paste(cell, (x, y))
    sheet.save(ROOT / "research" / "mobile-visual-check-v2.png", "PNG", optimize=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    render_cover()
    render_wechat_cover()
    render_marvell()
    render_zdr()
    render_ads_method()
    render_egg()
    process_cursor_sources()
    process_paper_figures()
    contact_sheet()
    mobile_check(
        [
            "00-cover-v2.png",
            "04-google-marvell-v2.png",
            "07-openai-zdr-v2.png",
            "11-chatgpt-ads-method-v2.png",
            "11b-chatgpt-ads-income-paper.png",
            "12-model-hypnosis-paper-fig1.png",
            "13-agent-coordination-paper-fig1.png",
            "13b-agent-coordination-paper-fig8.png",
            "15-egg-v2.png",
        ]
    )
    print("Rendered Hunt Good visual revision v2")


if __name__ == "__main__":
    main()
