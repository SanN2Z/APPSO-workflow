from __future__ import annotations

from pathlib import Path
from math import cos, pi, sin

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)
REPO_ROOT = Path(__file__).resolve().parents[6]
APPSO_LOGO = REPO_ROOT / "APPSO-数字资产" / "01-栏目与品牌" / "品牌视觉" / "原始资料" / "APPSO Logo 红底白字.png"

FINAL_BODY_VISUALS = [
    "00-cover.png",
    "01-stripe-openrouter-official.png",
    "02-amazon-prime-air-official.jpg",
    "03-pa-data-center-commonwealth.jpg",
    "04-google-marvell.png",
    "05-cursor-origin-official.png",
    "06-chatgpt-teens-official.png",
    "07-openai-zdr.png",
    "08-gemini-37-flash-official.png",
    "09-openmotion-official.png",
    "10-kitbitz-official.webp",
    "11-chatgpt-ads.png",
    "12-model-hypnosis.png",
    "13-agent-coordination.png",
    "14-cuda-island-author.jpg",
    "15-egg.png",
]

W, H = 1080, 1440
BG = "#F8F5EC"
PAPER = "#FFFFFF"
INK = "#121212"
MUTED = "#67645F"
RED = "#EC1700"
ORANGE = "#FC7C0A"
LINE = "#DDD7CA"
BLUE = "#3976F6"
TEAL = "#14A38B"
PURPLE = "#7656D8"
YELLOW = "#FFC84A"
PINK = "#F05D8B"


def font_path(bold: bool = False) -> str:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    raise FileNotFoundError("No usable CJK font found")


REGULAR = font_path(False)
BOLD = font_path(True)


def f(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD if bold else REGULAR, size=size)


def paste_appsso_logo(img: Image.Image, xy: tuple[int, int], height: int = 36) -> tuple[int, int]:
    if not APPSO_LOGO.is_file():
        raise FileNotFoundError(f"Missing registered APPSO logo: {APPSO_LOGO}")
    with Image.open(APPSO_LOGO) as source:
        logo = source.convert("RGB")
        width = round(logo.width * height / logo.height)
        logo = logo.resize((width, height), Image.Resampling.LANCZOS)
    img.paste(logo, xy)
    return width, height


def gradient(top: str = BG, bottom: str = "#F2EBDD") -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    t = tuple(int(top[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(bottom[i : i + 2], 16) for i in (1, 3, 5))
    for y in range(H):
        k = y / (H - 1)
        color = tuple(round(t[j] * (1 - k) + b[j] * k) for j in range(3))
        for x in range(W):
            px[x, y] = color
    return img


def rounded(draw: ImageDraw.ImageDraw, box, radius=28, fill=PAPER, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        candidate = current + ch
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def text_block(
    draw: ImageDraw.ImageDraw,
    xy,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill=INK,
    max_width=900,
    spacing=12,
    max_lines=None,
):
    x, y = xy
    lines = wrap(draw, text, font, max_width)
    if max_lines:
        lines = lines[:max_lines]
    line_h = font.size + spacing
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def center_text(draw, box, text, font, fill=INK):
    x1, y1, x2, y2 = box
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text(((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2 - bb[1]), text, font=font, fill=fill)


def arrow(draw, start, end, fill=INK, width=6, head=18):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=fill, width=width)
    a = pi / 6
    angle = __import__("math").atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * cos(angle - a), y2 - head * sin(angle - a))
    p2 = (x2 - head * cos(angle + a), y2 - head * sin(angle + a))
    draw.polygon([(x2, y2), p1, p2], fill=fill)


def pill(draw, xy, label, fill=INK, text_fill=PAPER, pad_x=22, pad_y=10, size=26):
    x, y = xy
    font = f(size, True)
    bb = draw.textbbox((0, 0), label, font=font)
    w = bb[2] - bb[0] + pad_x * 2
    h = bb[3] - bb[1] + pad_y * 2
    rounded(draw, (x, y, x + w, y + h), radius=h // 2, fill=fill)
    draw.text((x + pad_x, y + pad_y - bb[1]), label, font=font, fill=text_fill)
    return w, h


def base(section: str, index: str, title: str, deck: str, accent=RED, source="来源见正文"):
    img = gradient()
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 16), fill=accent)
    draw.ellipse((68, 64, 88, 84), fill=accent)
    draw.text((104, 52), f"HUNT FOR {section.upper()}", font=f(25, True), fill=INK)
    draw.text((870, 52), index, font=f(26, True), fill=accent)
    y = text_block(draw, (64, 118), title, f(56, True), max_width=952, spacing=8, max_lines=2)
    text_block(draw, (68, y + 20), deck, f(27), fill=MUTED, max_width=920, spacing=9, max_lines=2)
    draw.line((64, 1340, 1016, 1340), fill=LINE, width=2)
    paste_appsso_logo(img, (64, 1358), height=36)
    bb = draw.textbbox((0, 0), source, font=f(18))
    draw.text((1016 - (bb[2] - bb[0]), 1365), source, font=f(18), fill=MUTED)
    return img, draw


def save(img: Image.Image, name: str):
    img.save(OUT / name, "PNG", optimize=True)


def node(draw, center, r=42, fill=PAPER, outline=INK, width=4, label=None, label_fill=INK):
    x, y = center
    draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=width)
    if label:
        center_text(draw, (x - r, y - r, x + r, y + r), label, f(24, True), label_fill)


def repo_icon(draw, box, fill="#FFF4E5", outline=INK):
    x1, y1, x2, y2 = box
    rounded(draw, box, 22, fill, outline, 4)
    draw.rectangle((x1 + 28, y1 - 12, x1 + 132, y1 + 22), fill=fill, outline=outline, width=4)
    draw.line((x1 + 40, y1 + 76, x2 - 40, y1 + 76), fill=outline, width=4)
    draw.line((x1 + 40, y1 + 118, x2 - 84, y1 + 118), fill=outline, width=4)


def chip_icon(draw, box, fill=INK, accent=ORANGE):
    x1, y1, x2, y2 = box
    rounded(draw, box, 26, fill, None)
    inner = (x1 + 48, y1 + 48, x2 - 48, y2 - 48)
    rounded(draw, inner, 16, accent, None)
    for i in range(5):
        yy = y1 + 40 + i * ((y2 - y1 - 80) / 4)
        draw.line((x1 - 20, yy, x1, yy), fill=fill, width=8)
        draw.line((x2, yy, x2 + 20, yy), fill=fill, width=8)
        xx = x1 + 40 + i * ((x2 - x1 - 80) / 4)
        draw.line((xx, y1 - 20, xx, y1), fill=fill, width=8)
        draw.line((xx, y2, xx, y2 + 20), fill=fill, width=8)


def lock_icon(draw, center, scale=1.0, fill=INK, accent=YELLOW):
    x, y = center
    w, h = int(108 * scale), int(88 * scale)
    draw.arc((x - w // 3, y - h, x + w // 3, y), 180, 360, fill=fill, width=max(5, int(9 * scale)))
    rounded(draw, (x - w // 2, y - h // 3, x + w // 2, y + h // 2), int(14 * scale), fill, None)
    draw.ellipse((x - 8 * scale, y - 5 * scale, x + 8 * scale, y + 11 * scale), fill=accent)


def agent_icon(draw, center, r=40, fill=PAPER, outline=INK):
    x, y = center
    draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=4)
    draw.ellipse((x - r * 0.42, y - r * 0.35, x - r * 0.16, y - r * 0.09), fill=outline)
    draw.ellipse((x + r * 0.16, y - r * 0.35, x + r * 0.42, y - r * 0.09), fill=outline)
    draw.arc((x - r * 0.42, y - r * 0.12, x + r * 0.42, y + r * 0.45), 20, 160, fill=outline, width=4)
    draw.line((x, y - r, x, y - r - 20), fill=outline, width=4)
    draw.ellipse((x - 6, y - r - 30, x + 6, y - r - 18), fill=RED)


def cover():
    img = gradient("#FBF7EE", "#EDE2D2")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 22), fill=RED)
    d.text((64, 74), "HUNT GOOD", font=f(32, True), fill=RED)
    d.text((64, 126), "WEEKLY  ·  2026.08.21", font=f(24, True), fill=INK)
    paste_appsso_logo(img, (900, 70), height=36)
    d.text((64, 230), "AI 开始争夺", font=f(86, True), fill=INK)
    d.text((64, 340), "中间那一层", font=f(86, True), fill=INK)
    d.text((68, 475), "模型路由 · 代码仓库 · 芯片订单 · 数据中心", font=f(28), fill=MUTED)

    centers = [(170, 875), (390, 720), (590, 900), (820, 700), (890, 1000), (470, 1120), (180, 1110)]
    for a, b in [(0, 1), (1, 2), (1, 3), (2, 4), (2, 5), (5, 6), (3, 4), (0, 6)]:
        d.line((*centers[a], *centers[b]), fill="#BFB5A5", width=6)
    labels = ["$", "ROUTE", "CODE", "CHIP", "VOTE", "POWER", "TEEN"]
    fills = [YELLOW, RED, BLUE, ORANGE, PURPLE, TEAL, PINK]
    for c, lab, col in zip(centers, labels, fills):
        node(d, c, 70 if lab == "ROUTE" else 58, col, INK, 5, lab, INK if col != RED else PAPER)

    pill(d, (64, 1280), "7 NEWS", RED)
    pill(d, (250, 1280), "3 TOOLS", INK)
    pill(d, (447, 1280), "3 INSIGHTS", PURPLE)
    pill(d, (692, 1280), "1 FUN", TEAL)
    save(img, "00-cover.png")


def wechat_cover():
    width, height = 1920, 818
    img = Image.new("RGB", (width, height), "#F7F1E6")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, width, 22), fill=RED)
    d.text((72, 58), "HUNT GOOD", font=f(34, True), fill=RED)
    d.text((72, 114), "WEEKLY  ·  2026.08.21", font=f(25, True), fill=INK)
    paste_appsso_logo(img, (1715, 58), height=42)
    d.text((72, 220), "AI 开始争夺", font=f(102, True), fill=INK)
    d.text((72, 350), "中间那一层", font=f(102, True), fill=INK)
    d.text((78, 500), "模型路由 · 代码仓库 · 芯片订单 · 数据中心", font=f(32), fill=MUTED)

    centers = [(1195, 278), (1415, 178), (1510, 402), (1730, 245), (1745, 565), (1450, 630), (1170, 570)]
    for a, b in [(0, 1), (1, 3), (0, 2), (2, 4), (2, 5), (5, 6), (3, 4), (0, 6)]:
        d.line((*centers[a], *centers[b]), fill="#BFB5A5", width=6)
    labels = ["ROUTE", "CHIP", "CODE", "VOTE", "?", "POWER", "$"]
    fills = [RED, ORANGE, BLUE, PURPLE, PINK, TEAL, YELLOW]
    for c, lab, col in zip(centers, labels, fills):
        node(d, c, 68 if lab == "ROUTE" else 55, col, INK, 5, lab, PAPER if col in (RED, PURPLE) else INK)

    pill(d, (72, 688), "7 NEWS", RED, size=24)
    pill(d, (255, 688), "3 TOOLS", INK, size=24)
    pill(d, (455, 688), "3 INSIGHTS", PURPLE, size=24)
    pill(d, (705, 688), "1 FUN", TEAL, size=24)
    img.save(OUT / "00-cover-wechat.png", "PNG", optimize=True)


def stripe_router():
    img, d = base("News", "01", "Stripe 要买下 OpenRouter", "钱的路由器，准备接管 token 的路由器", RED, "来源：Stripe")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    models = [(150, 520), (150, 680), (150, 840), (150, 1000)]
    for i, p in enumerate(models):
        node(d, p, 42, ["#E7F0FF", "#FCE9EF", "#E9F8F2", "#FFF0D7"][i], INK, 3, f"M{i+1}")
        arrow(d, (195, p[1]), (410, 740), MUTED, 4, 14)
    rounded(d, (410, 600, 690, 880), 42, INK)
    center_text(d, (410, 640, 690, 760), "ROUTER", f(36, True), PAPER)
    center_text(d, (410, 755, 690, 835), "复杂度 · 价格\n速度 · 可靠性", f(23), "#F4EBDC")
    arrow(d, (690, 740), (840, 740), RED, 8, 24)
    rounded(d, (840, 640, 960, 840), 26, YELLOW, INK, 4)
    center_text(d, (840, 640, 960, 840), "TOKEN\n↕\n$", f(30, True))
    pill(d, (90, 1180), "400+ 模型", RED)
    pill(d, (350, 1180), "80+ 供应商", INK)
    pill(d, (650, 1180), "金额未披露", "#6B6258")
    save(img, "01-stripe-openrouter.png")


def drone_card():
    img, d = base("News", "02", "无人机送货要铺到近 500 个城镇", "最快 30 分钟，但这是一张年底计划表", ORANGE, "来源：Amazon / ABC News")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    d.text((92, 430), "≈ 500", font=f(116, True), fill=RED)
    d.text((100, 560), "CITIES & TOWNS", font=f(30, True), fill=INK)
    # Drone
    d.rounded_rectangle((570, 470, 790, 570), radius=30, fill=INK)
    d.line((620, 520, 520, 450), fill=INK, width=12)
    d.line((740, 520, 840, 450), fill=INK, width=12)
    d.line((620, 520, 520, 595), fill=INK, width=12)
    d.line((740, 520, 840, 595), fill=INK, width=12)
    for x, y in [(510, 440), (850, 440), (510, 605), (850, 605)]:
        d.ellipse((x - 55, y - 16, x + 55, y + 16), fill=ORANGE, outline=INK, width=3)
    rounded(d, (640, 565, 720, 650), 12, YELLOW, INK, 3)
    # Town network
    pts = [(150, 830), (300, 770), (470, 860), (630, 760), (820, 830), (920, 960), (710, 1010), (480, 980), (260, 1030)]
    for a, b in zip(pts, pts[1:]):
        d.line((*a, *b), fill="#D4C8B8", width=5)
    for p in pts:
        d.rounded_rectangle((p[0]-32, p[1]-32, p[0]+32, p[1]+32), radius=8, fill="#FFF1D6", outline=INK, width=3)
        d.polygon([(p[0]-38,p[1]-28),(p[0],p[1]-58),(p[0]+38,p[1]-28)], fill=RED)
    pill(d, (92, 1180), "≤ 5 磅", INK)
    pill(d, (310, 1180), "最快 30 分钟", RED)
    pill(d, (670, 1180), "年底目标", ORANGE)
    save(img, "02-amazon-prime-air.png")


def data_center_card():
    img, d = base("News", "03", "数据中心，开始进入投票箱", "当电、水和土地成本出现在家庭账单上", RED, "来源：Axios / AP / PA")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    # Servers
    for i in range(3):
        x = 100 + i * 125
        rounded(d, (x, 500, x + 95, 800), 18, INK)
        for yy in range(545, 760, 65):
            d.line((x + 20, yy, x + 72, yy), fill="#F8F5EC", width=6)
            d.ellipse((x + 72, yy - 5, x + 82, yy + 5), fill=ORANGE)
    arrow(d, (475, 650), (610, 650), RED, 8, 24)
    # Bill
    rounded(d, (610, 480, 825, 820), 22, "#FFF8E7", INK, 4)
    d.text((650, 520), "BILL", font=f(34, True), fill=INK)
    for yy, w in [(610,120),(665,145),(720,95)]:
        d.line((650, yy, 650+w, yy), fill=MUTED, width=5)
    d.text((650, 755), "↑ ?", font=f(42, True), fill=RED)
    arrow(d, (825, 650), (900, 820), RED, 8, 24)
    # Ballot
    rounded(d, (820, 820, 970, 1000), 18, PURPLE, INK, 4)
    d.rectangle((850, 780, 935, 870), fill=PAPER, outline=INK, width=4)
    d.line((868, 820, 892, 844), fill=TEAL, width=8)
    d.line((892, 844, 925, 800), fill=TEAL, width=8)
    d.text((94, 900), "谁受益？", font=f(34, True), fill=INK)
    d.text((94, 960), "谁付钱？", font=f(34, True), fill=INK)
    d.text((94, 1020), "社区能否说不？", font=f(34, True), fill=RED)
    pill(d, (92, 1180), "OHIO DATA CENTER RISK", RED, PAPER, size=24)
    save(img, "03-data-center-politics.png")


def marvell_card():
    img, d = base("News", "04", "Google 的 122 亿美元，不是现款", "它是一张跟未来芯片采购挂钩的认股权证", ORANGE, "来源：Marvell 8-K")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    chip_icon(d, (105, 560, 345, 800), INK, ORANGE)
    d.text((135, 830), "CUSTOM\nSILICON", font=f(27, True), fill=INK)
    arrow(d, (380, 680), (535, 680), ORANGE, 9, 25)
    rounded(d, (535, 520, 755, 850), 28, "#FFF3D7", INK, 4)
    center_text(d, (535, 545, 755, 665), "$500M", f(58, True), RED)
    center_text(d, (535, 675, 755, 770), "合格收入\n= 解锁 1 批", f(27, True), INK)
    center_text(d, (535, 780, 755, 830), "× 240", f(34, True), ORANGE)
    arrow(d, (775, 680), (865, 680), ORANGE, 9, 25)
    rounded(d, (850, 530, 975, 840), 22, PURPLE, INK, 4)
    center_text(d, (850, 555, 975, 690), "BUY\nSHARES", f(28, True), PAPER)
    center_text(d, (850, 700, 975, 820), "$206.58\n/ share", f(22, True), PAPER)
    d.text((90, 980), "若 240 批全部解锁", font=f(27), fill=MUTED)
    d.text((90, 1025), "对应 $120B 合格采购收入", font=f(42, True), fill=RED)
    pill(d, (90, 1180), "不是当前投资", INK)
    pill(d, (410, 1180), "不是已确认收入", RED)
    save(img, "04-google-marvell.png")


def cursor_card():
    img, d = base("News", "05", "Cursor 把代码仓库搬进工作台", "Repo、Agent、PR 开始住在同一个地方", BLUE, "来源：Cursor")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    repo_icon(d, (100, 575, 360, 820), "#EAF1FF")
    center_text(d, (100, 830, 360, 900), "REPO", f(30, True), BLUE)
    arrow(d, (390, 700), (500, 700), BLUE, 8, 22)
    agent_icon(d, (610, 700), 95, "#FFF2DF", INK)
    center_text(d, (490, 835, 730, 900), "AGENT", f(30, True), ORANGE)
    arrow(d, (720, 700), (825, 700), BLUE, 8, 22)
    rounded(d, (825, 560, 970, 840), 24, "#EDF9F5", INK, 4)
    d.text((855, 600), "PR", font=f(52, True), fill=TEAL)
    d.line((855, 700, 940, 700), fill=INK, width=5)
    d.line((855, 750, 920, 750), fill=INK, width=5)
    d.ellipse((872, 785, 900, 813), fill=TEAL)
    d.line((885, 798, 893, 806), fill=PAPER, width=4)
    d.line((893, 806, 910, 784), fill=PAPER, width=4)
    pill(d, (90, 980), "EARLY BETA", BLUE)
    pill(d, (360, 980), "PAID PLANS", INK)
    pill(d, (665, 980), "GITHUB SYNC", TEAL)
    d.text((92, 1060), "GitHub 来源仓库仍以 GitHub 为真源", font=f(27), fill=MUTED)
    save(img, "05-cursor-origin.png")


def teens_card():
    img, d = base("News", "06", "系统猜你未满 18 岁，就自动切换", "ChatGPT 为 13—17 岁用户单开一套体验", PINK, "来源：OpenAI")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    # shield
    d.polygon([(275, 490), (455, 550), (430, 840), (275, 980), (120, 840), (95, 550)], fill="#FBE8EF", outline=INK)
    d.text((160, 610), "13—17", font=f(54, True), fill=PINK)
    d.text((165, 710), "TEEN", font=f(42, True), fill=INK)
    d.line((180, 815, 250, 875), fill=TEAL, width=16)
    d.line((250, 875, 365, 735), fill=TEAL, width=16)
    arrow(d, (480, 735), (585, 735), PINK, 9, 26)
    features = [(610, 500, "学习模式", BLUE), (810, 500, "作业提醒", ORANGE), (610, 740, "测验", TEAL), (810, 740, "学习时段", PURPLE)]
    for x, y, lab, col in features:
        rounded(d, (x, y, x + 170, y + 170), 30, col, INK, 3)
        center_text(d, (x, y, x + 170, y + 170), lab, f(28, True), PAPER if col != ORANGE else INK)
    d.text((92, 1020), "自动分流 ≠ 年龄判断已经准确", font=f(32, True), fill=RED)
    save(img, "06-chatgpt-teens.png")


def zdr_card():
    img, d = base("News", "07", "跨对话看风险，但不拿走原文", "Private Safety Processing 想兼容零数据保留", TEAL, "来源：OpenAI")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    # customer side
    for y, lab in [(510, "PROMPT"), (690, "RESPONSE")]:
        rounded(d, (100, y, 360, y + 130), 26, "#E8F7F3", INK, 4)
        d.text((130, y + 42), lab, font=f(26, True), fill=INK)
        lock_icon(d, (315, y + 75), 0.55, INK, YELLOW)
    d.text((115, 865), "客户控制内容 / 密钥", font=f(25, True), fill=TEAL)
    arrow(d, (390, 670), (535, 670), TEAL, 8, 24)
    # pattern engine
    rounded(d, (535, 500, 760, 850), 36, INK)
    for i in range(3):
        yy = 575 + i * 90
        d.line((585, yy, 710, yy), fill=[ORANGE, TEAL, PURPLE][i], width=16)
        d.ellipse((630 + i * 20, yy - 16, 662 + i * 20, yy + 16), fill=PAPER)
    center_text(d, (535, 770, 760, 835), "PATTERN", f(26, True), PAPER)
    arrow(d, (790, 670), (895, 670), RED, 8, 24)
    rounded(d, (880, 550, 975, 790), 26, RED)
    center_text(d, (880, 560, 975, 790), "RISK\nSIGNAL", f(24, True), PAPER)
    d.text((92, 1010), "OpenAI 员工：看信号，不看底层内容", font=f(31, True), fill=INK)
    pill(d, (90, 1180), "EARLY CUSTOMER TEST", TEAL)
    pill(d, (525, 1180), "白皮书：9 月", INK)
    save(img, "07-openai-zdr.png")


def gemini_card():
    img, d = base("Tools", "01", "Gemini 3.7 Flash", "长上下文、三档思考，低价只到年底", BLUE, "来源：Google")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    d.text((92, 450), "1M", font=f(118, True), fill=BLUE)
    d.text((330, 515), "INPUT TOKENS", font=f(29, True), fill=INK)
    d.text((92, 650), "64K", font=f(84, True), fill=TEAL)
    d.text((330, 690), "MAX OUTPUT", font=f(29, True), fill=INK)
    for i, (lab, col) in enumerate([("LOW", "#DDE8FF"), ("MEDIUM", "#BFD1FF"), ("HIGH", BLUE)]):
        x = 92 + i * 250
        rounded(d, (x, 820, x + 210, 900), 22, col, INK, 3)
        center_text(d, (x, 820, x + 210, 900), lab, f(24, True), PAPER if i == 2 else INK)
    d.text((92, 970), "$0.75 IN  /  $3.75 OUT", font=f(44, True), fill=RED)
    d.text((92, 1035), "2027.01.01 起翻倍", font=f(28, True), fill=MUTED)
    save(img, "08-gemini-37-flash.png")


def openmotion_card():
    img, d = base("Tools", "02", "OpenMotion", "一句话进来，场景、时间线和导出仍能继续改", PURPLE, "来源：OpenMotion")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    rounded(d, (90, 500, 300, 650), 24, "#F2EAFE", INK, 4)
    d.text((125, 545), "PROMPT", font=f(31, True), fill=PURPLE)
    arrow(d, (325, 575), (420, 575), PURPLE, 8, 22)
    for i in range(3):
        x = 435 + i * 170
        rounded(d, (x, 480, x + 140, 670), 18, ["#FFF0D7", "#E7F2FF", "#EAF8F2"][i], INK, 3)
        d.polygon([(x+25,625),(x+70,540),(x+115,625)], fill=[ORANGE, BLUE, TEAL][i])
        d.ellipse((x+52,515,x+88,551), fill=YELLOW)
    # timeline
    d.line((110, 810, 950, 810), fill=INK, width=8)
    for i, col in enumerate([PURPLE, ORANGE, BLUE, TEAL]):
        x = 135 + i * 205
        rounded(d, (x, 770, x + 160, 850), 14, col)
    d.polygon([(555,745),(535,715),(575,715)], fill=RED)
    d.line((555, 735, 555, 890), fill=RED, width=5)
    pills = [(95, 960, "VIDEO", INK), (330, 960, "WEBM", PURPLE), (565, 960, "HTML", TEAL)]
    for x, y, lab, col in pills:
        pill(d, (x, y), lab, col)
    d.text((92, 1050), "MAC ONLY  ·  当前免费  ·  本轮未实测", font=f(27, True), fill=MUTED)
    save(img, "09-openmotion.png")


def kitbitz_card():
    img, d = base("Tools", "03", "Kitbitz", "2000+ 手绘素材，CC0，拼一个小世界", TEAL, "来源：Kitbitz / GitHub")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    # ground
    d.ellipse((120, 770, 960, 1100), fill="#DDF2E6", outline=INK, width=4)
    # castle
    d.rectangle((210, 650, 410, 920), fill="#F2C9A5", outline=INK, width=4)
    for x in [190, 280, 370]:
        d.rectangle((x, 585, x + 75, 735), fill=ORANGE, outline=INK, width=4)
        d.rectangle((x, 565, x + 22, 600), fill=ORANGE, outline=INK, width=4)
        d.rectangle((x + 53, 565, x + 75, 600), fill=ORANGE, outline=INK, width=4)
    d.arc((270, 785, 350, 930), 180, 360, fill=INK, width=8)
    # tree
    d.rectangle((520, 735, 555, 950), fill="#8A5A34")
    for cx, cy, r in [(505,690,85),(565,655,95),(620,720,80)]:
        d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=TEAL, outline=INK, width=4)
    # rocket
    d.ellipse((760, 550, 900, 850), fill="#DCE8FF", outline=INK, width=4)
    d.polygon([(830, 500),(760,650),(900,650)], fill=RED, outline=INK)
    d.ellipse((800, 660, 860, 720), fill=BLUE, outline=INK, width=3)
    d.polygon([(770,800),(720,900),(790,865)], fill=PURPLE, outline=INK)
    d.polygon([(890,800),(940,900),(870,865)], fill=PURPLE, outline=INK)
    d.polygon([(805,850),(830,1015),(855,850)], fill=YELLOW)
    pill(d, (90, 1180), "SVG + PNG", TEAL)
    pill(d, (360, 1180), "13 KITS", INK)
    pill(d, (610, 1180), "CC0 · 可商用", RED)
    save(img, "10-kitbitz.png")


def ads_card():
    img, d = base("Insights", "01", "低收入人设帐号，更容易收到广告", "91 个模拟帐号做了一次 3×3 审计", PURPLE, "来源：arXiv:2608.05008")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    d.text((90, 435), "3 族裔线索  ×  3 收入档", font=f(34, True), fill=INK)
    for row in range(3):
        for col in range(3):
            x, y = 135 + col * 210, 570 + row * 170
            fill = "#F9D8E4" if row == 0 else ["#EEE9FA", "#E8F1FF"][row - 1]
            node(d, (x, y), 52, fill, INK, 3)
            d.text((x + 70, y - 18), ["LOW", "MID", "HIGH"][row], font=f(20, True), fill=RED if row == 0 else MUTED)
    # Clock
    d.ellipse((780, 560, 950, 730), fill="#FFF3D2", outline=INK, width=5)
    d.line((865, 645, 865, 585), fill=INK, width=7)
    d.line((865, 645, 915, 665), fill=INK, width=7)
    center_text(d, (760, 750, 970, 820), "14 天后", f(30, True), RED)
    rounded(d, (740, 850, 970, 1005), 22, RED)
    center_text(d, (740, 850, 970, 1005), "ADS\n3000+", f(31, True), PAPER)
    pill(d, (90, 1180), "335 PROMPTS", PURPLE)
    pill(d, (420, 1180), "186 ADVERTISERS", INK)
    save(img, "11-chatgpt-ads.png")


def hypnosis_card():
    img, d = base("Insights", "02", "意思没变，答案翻了", "6 个弱措辞偏差叠加：94% NO → 99.93% YES", RED, "来源：arXiv:2608.16834")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    for i in range(6):
        x = 90 + i * 150
        rounded(d, (x, 520 + (i % 2) * 45, x + 120, 650 + (i % 2) * 45), 20, "#FFF0D8", INK, 3)
        center_text(d, (x, 520 + (i % 2) * 45, x + 120, 650 + (i % 2) * 45), f"CUE {i+1}", f(20, True), ORANGE)
        if i < 5:
            d.text((x + 125, 565), "+", font=f(38, True), fill=MUTED)
    arrow(d, (180, 790), (890, 790), RED, 12, 34)
    d.ellipse((100, 720, 260, 880), fill=INK)
    center_text(d, (100, 720, 260, 880), "NO\n94%", f(30, True), PAPER)
    d.ellipse((810, 690, 990, 870), fill=RED, outline=INK, width=5)
    center_text(d, (810, 690, 990, 870), "YES\n99.93%", f(29, True), PAPER)
    d.text((92, 970), "自然改写 · 错字 · 动物列表 · JSON", font=f(31, True), fill=INK)
    d.text((92, 1030), "实验：强制二选一 + 大量查询筛选", font=f(27), fill=MUTED)
    save(img, "12-model-hypnosis.png")


def coordination_card():
    img, d = base("Insights", "03", "共享文件有用，指定组长没那么有用", "8 Agent 的消息密集任务，输出 token 约少 42%", BLUE, "来源：arXiv:2608.16801")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    center = (540, 735)
    # message mesh faint
    pts = []
    for i in range(8):
        ang = 2 * pi * i / 8 - pi / 2
        pts.append((int(center[0] + 310 * cos(ang)), int(center[1] + 260 * sin(ang))))
    for i in range(8):
        d.line((*pts[i], *pts[(i + 1) % 8]), fill="#CFC7BC", width=3)
        d.line((*pts[i], *center), fill=BLUE, width=4)
    rounded(d, (440, 650, 640, 820), 22, "#E7F1FF", INK, 4)
    center_text(d, (440, 650, 640, 820), "SHARED\nFILE", f(27, True), BLUE)
    for i, p in enumerate(pts):
        agent_icon(d, p, 48, "#FFF4E5" if i else "#F4EAFB", INK)
        if i == 0:
            d.text((p[0] - 60, p[1] - 95), "协调者", font=f(20, True), fill=PURPLE)
    rounded(d, (695, 980, 965, 1075), 24, RED)
    center_text(d, (695, 980, 965, 1075), "OUTPUT −42%", f(30, True), PAPER)
    d.text((92, 1010), "1902 次主实验  +  244 次密封验证", font=f(28, True), fill=INK)
    save(img, "13-agent-coordination.png")


def island_card():
    img, d = base("Fun", "01", "一张小岛照片，8069 万个三角形", "不用 Google Lens，把整颗地球变成几何搜索题", TEAL, "来源：yassa9 / Gralhix")
    rounded(d, (60, 390, 1020, 1130), 36, PAPER, LINE, 2)
    # pseudo photo frame
    rounded(d, (90, 500, 430, 780), 22, "#CFEAF2", INK, 4)
    islands = [(170,680,58),(330,610,72),(235,560,45)]
    for x,y,r in islands:
        d.ellipse((x-r*1.2,y-r*0.55,x+r*1.2,y+r*0.55), fill=TEAL, outline=INK, width=3)
    for a,b in [(0,1),(1,2),(2,0)]:
        d.line((islands[a][0],islands[a][1],islands[b][0],islands[b][1]), fill=RED, width=5)
    d.text((120, 805), "3 个点 → 几何指纹", font=f(26, True), fill=INK)
    arrow(d, (455, 650), (565, 650), TEAL, 8, 24)
    # world search
    d.ellipse((570, 500, 965, 865), fill="#E7F3EB", outline=INK, width=5)
    for i in range(8):
        ang = 2*pi*i/8
        x = 768 + int(145*cos(ang))
        y = 682 + int(125*sin(ang))
        d.polygon([(x,y-18),(x-16,y+14),(x+16,y+14)], fill=ORANGE if i != 5 else RED)
    d.line((620, 680, 915, 680), fill="#A7BDAF", width=3)
    d.arc((620, 545, 915, 815), 0, 360, fill="#A7BDAF", width=3)
    d.text((92, 940), "80,690,777", font=f(74, True), fill=RED)
    d.text((95, 1030), "候选三角形  ·  CUDA 并行比较", font=f(29, True), fill=INK)
    save(img, "14-cuda-island.png")


def egg_card():
    img = gradient("#151515", "#2A211B")
    d = ImageDraw.Draw(img)
    d.text((64, 70), "HUNT GOOD · EGG", font=f(26, True), fill=ORANGE)
    text_block(d, (64, 145), "AI 的下一站\n不一定在聊天框里", f(66, True), fill=PAPER, max_width=940, spacing=18)
    path = [(120, 650), (290, 790), (475, 670), (645, 865), (840, 710), (930, 1000)]
    for i in range(len(path)-1):
        d.line((*path[i], *path[i+1]), fill="#7A6D61", width=8)
    labels = ["TOKEN", "REPO", "CHIP", "POWER", "VOTE", "?"]
    cols = [YELLOW, BLUE, ORANGE, TEAL, PURPLE, RED]
    for p, lab, col in zip(path, labels, cols):
        node(d, p, 58, col, PAPER, 4, lab, INK if col in (YELLOW, ORANGE) else PAPER)
    d.text((64, 1190), "FOLLOW THE COST.\nFOLLOW THE CONTROL.", font=f(38, True), fill=PAPER)
    paste_appsso_logo(img, (64, 1348), height=38)
    d.text((848, 1360), "非 AI 生成", font=f(20), fill="#BFB3A7")
    save(img, "15-egg.png")


def contact_sheet():
    files = [OUT / name for name in FINAL_BODY_VISUALS]
    missing = [path.name for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing final visuals for contact sheet: {missing}")
    sheet = Image.new("RGB", (1080, 1440), "#D8D2C7")
    for i, path in enumerate(files):
        with Image.open(path) as source:
            thumb = ImageOps.contain(source.convert("RGB"), (250, 310), method=Image.Resampling.LANCZOS)
        cell = Image.new("RGB", (258, 348), PAPER)
        cell.paste(thumb, ((258 - thumb.width) // 2, (310 - thumb.height) // 2))
        label_draw = ImageDraw.Draw(cell)
        label_draw.text((8, 320), path.name[:30], font=f(12), fill=INK)
        x = (i % 4) * 270 + 6
        y = (i // 4) * 360 + 6
        sheet.paste(cell, (x, y))
    sheet.save(ROOT / "research" / "contact-sheet.png", "PNG", optimize=True)


def main():
    cover()
    wechat_cover()
    marvell_card()
    zdr_card()
    ads_card()
    hypnosis_card()
    coordination_card()
    egg_card()
    contact_sheet()
    print(f"Rendered 7 original body graphics and 1 WeChat cover to {OUT}")


if __name__ == "__main__":
    main()
