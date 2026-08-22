from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PACKAGE = Path(__file__).resolve().parents[1]
RESEARCH = PACKAGE / "research"
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\((assets/[^)]+)\)")


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def contain(image: Image.Image, width: int, height: int) -> Image.Image:
    copy = image.copy()
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    return copy


def render_mobile_check() -> None:
    names = (
        "04-google-marvell-illustrated-v4.png",
        "07-openai-zdr-illustrated-v3.png",
        "11-chatgpt-ads-illustrated-v3.png",
    )
    canvas = Image.new("RGB", (1250, 610), (244, 242, 238))
    draw = ImageDraw.Draw(canvas)
    label_font = font(22)
    for index, name in enumerate(names):
        with Image.open(PACKAGE / "assets" / name) as source:
            mobile = source.convert("RGB").resize((390, 520), Image.Resampling.LANCZOS)
        x = 20 + index * 410
        canvas.paste(mobile, (x, 56))
        draw.text((x, 18), name, fill=(28, 28, 28), font=label_font)
    canvas.save(RESEARCH / "mobile-visual-check-v3.png", optimize=True)


def render_contact_sheet() -> None:
    draft = (PACKAGE / "draft.md").read_text(encoding="utf-8")
    image_refs = IMAGE_PATTERN.findall(draft)
    columns = 4
    cell_width = 300
    thumb_height = 185
    label_height = 52
    gap = 18
    rows = (len(image_refs) + columns - 1) // columns
    width = gap + columns * (cell_width + gap)
    height = 70 + rows * (thumb_height + label_height + gap)
    canvas = Image.new("RGB", (width, height), (239, 237, 232))
    draw = ImageDraw.Draw(canvas)
    title_font = font(30)
    label_font = font(16)
    draw.text((gap, 18), f"Hunt Good 2026-08-21 · {len(image_refs)} draft images", fill=(24, 24, 24), font=title_font)

    for index, relative in enumerate(image_refs):
        row, column = divmod(index, columns)
        x = gap + column * (cell_width + gap)
        y = 64 + row * (thumb_height + label_height + gap)
        with Image.open(PACKAGE / relative) as source:
            thumb = contain(source.convert("RGB"), cell_width, thumb_height)
        frame = Image.new("RGB", (cell_width, thumb_height), (255, 255, 255))
        frame_x = (cell_width - thumb.width) // 2
        frame_y = (thumb_height - thumb.height) // 2
        frame.paste(thumb, (frame_x, frame_y))
        canvas.paste(frame, (x, y))
        draw.rectangle((x, y, x + cell_width - 1, y + thumb_height - 1), outline=(215, 210, 202), width=1)
        name = Path(relative).name
        draw.text((x, y + thumb_height + 8), f"{index + 1:02d}  {name}", fill=(55, 55, 55), font=label_font)

    canvas.save(RESEARCH / "contact-sheet-v3.png", optimize=True)


def main() -> None:
    render_mobile_check()
    render_contact_sheet()
    print("rendered research/mobile-visual-check-v3.png")
    print("rendered research/contact-sheet-v3.png")


if __name__ == "__main__":
    main()
