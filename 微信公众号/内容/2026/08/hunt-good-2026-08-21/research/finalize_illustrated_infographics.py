from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


PACKAGE = Path(__file__).resolve().parents[1]
WORKSPACE = PACKAGE.parents[4]
LOGO = (
    WORKSPACE
    / "APPSO-数字资产"
    / "01-栏目与品牌"
    / "品牌视觉"
    / "原始资料"
    / "APPSO Logo 红底白字.png"
)

TARGETS = (
    PACKAGE / "assets" / "04-google-marvell-illustrated-v4.png",
    PACKAGE / "assets" / "07-openai-zdr-illustrated-v3.png",
    PACKAGE / "assets" / "11-chatgpt-ads-illustrated-v3.png",
)

CANVAS_SIZE = (1080, 1440)
CONTENT_BOX = (24, 0, 1056, 1338)
FOOTER_LINE_Y = 1354
LOGO_WIDTH = 132


def corner_background(image: Image.Image) -> tuple[int, int, int]:
    rgb = image.convert("RGB")
    width, height = rgb.size
    samples = (
        rgb.getpixel((0, 0)),
        rgb.getpixel((width - 1, 0)),
        rgb.getpixel((0, height - 1)),
        rgb.getpixel((width - 1, height - 1)),
    )
    return tuple(round(sum(pixel[channel] for pixel in samples) / 4) for channel in range(3))


def contain(size: tuple[int, int], box: tuple[int, int, int, int]) -> tuple[int, int]:
    width, height = size
    box_width = box[2] - box[0]
    box_height = box[3] - box[1]
    scale = min(box_width / width, box_height / height)
    return round(width * scale), round(height * scale)


def finalize(path: Path, logo: Image.Image) -> None:
    with Image.open(path) as source_image:
        source = source_image.convert("RGB")
        background = corner_background(source)
        canvas = Image.new("RGB", CANVAS_SIZE, background)
        fitted_size = contain(source.size, CONTENT_BOX)
        fitted = source.resize(fitted_size, Image.Resampling.LANCZOS)
        x = (CANVAS_SIZE[0] - fitted.width) // 2
        y = CONTENT_BOX[1]
        canvas.paste(fitted, (x, y))

        draw = ImageDraw.Draw(canvas)
        draw.line((48, FOOTER_LINE_Y, 1032, FOOTER_LINE_Y), fill=(225, 205, 193), width=1)

        logo_height = round(LOGO_WIDTH * logo.height / logo.width)
        fitted_logo = logo.resize((LOGO_WIDTH, logo_height), Image.Resampling.LANCZOS)
        logo_x = (CANVAS_SIZE[0] - fitted_logo.width) // 2
        logo_y = FOOTER_LINE_Y + 18
        canvas.paste(fitted_logo, (logo_x, logo_y))
        canvas.save(path, format="PNG", optimize=True)


def main() -> None:
    with Image.open(LOGO) as logo_image:
        logo = logo_image.convert("RGB")
        for target in TARGETS:
            finalize(target, logo)
            print(f"finalized {target.relative_to(PACKAGE)}")


if __name__ == "__main__":
    main()
