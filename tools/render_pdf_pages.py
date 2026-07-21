#!/usr/bin/env python3
"""Render a PDF to PNG pages and extract its text with PyMuPDF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--text-output", type=Path)
    return parser.parse_args()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()

    if not args.pdf.is_file():
        raise FileNotFoundError(f"PDF not found: {args.pdf}")
    if args.dpi <= 0:
        raise ValueError("--dpi must be positive")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    document = fitz.open(args.pdf)
    if document.page_count == 0:
        raise ValueError(f"PDF has no pages: {args.pdf}")

    scale = args.dpi / 72
    matrix = fitz.Matrix(scale, scale)
    text_pages: list[str] = []

    for index, page in enumerate(document):
        output = args.output_dir / f"page-{index + 1:02d}.png"
        page.get_pixmap(matrix=matrix, alpha=False).save(output)
        text_pages.append(page.get_text("text"))

    if args.text_output:
        args.text_output.parent.mkdir(parents=True, exist_ok=True)
        args.text_output.write_text(
            "\n\n".join(text_pages), encoding="utf-8", errors="strict"
        )

    print(f"Rendered {document.page_count} pages to {args.output_dir}")
    if args.text_output:
        print(f"Extracted text to {args.text_output}")


if __name__ == "__main__":
    main()
