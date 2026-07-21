#!/usr/bin/env python3
"""Crop a rectangular region from an image without resampling it."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--box", nargs=4, type=int, required=True, metavar=("L", "T", "R", "B"))
    return parser.parse_args()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()

    if not args.input.is_file():
        raise FileNotFoundError(f"Image not found: {args.input}")

    with Image.open(args.input) as image:
        left, top, right, bottom = args.box
        if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
            raise ValueError(
                f"Crop box {args.box} is outside image bounds {(image.width, image.height)}"
            )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        image.crop((left, top, right, bottom)).save(args.output)
        print(f"Saved {args.output} ({right - left}x{bottom - top})")


if __name__ == "__main__":
    main()
