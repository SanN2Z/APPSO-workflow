#!/usr/bin/env python3
"""Crop / resize selected primary-source captures into publishable assets.

This file is the source of truth for what ships in the article. Each entry
names the raw capture, the crop window (fractions of width/height) and the
output name. Crops exist because a full-page screenshot is unreadable at
WeChat's mobile width -- the crop keeps the evidence and drops the chrome.

Nothing is generated or retouched: crop, resize, encode only.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "research" / "source-assets" / "v2"
OLD = ROOT / "research" / "source-assets"
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)

TARGET_WIDTH = 1080

# out_name, source_path, (left, top, right, bottom) as fractions | None
JOBS: list[tuple[str, Path, tuple[float, float, float, float] | None]] = [
    # --- News 1: Anthropic cyber-eval incidents ---
    ("01-anthropic-x-post.png", RAW / "x-anthropic-incidents.png", None),
    ("02-anthropic-incident1-database.png", RAW / "anthropic-report-incident1.png", (0.19, 0.30, 0.81, 0.62)),
    ("03-anthropic-incident2-pypi.png", RAW / "anthropic-report-incident2.png", (0.19, 0.30, 0.81, 0.62)),
    ("04-techcrunch-anthropic-headline.png", RAW / "techcrunch-anthropic.png", (0.04, 0.30, 0.96, 0.78)),
    ("05-hf-intrusion-actions.png", RAW / "hf-timeline-glm.png", (0.275, 0.29, 0.79, 0.44)),
    # --- News 2: Google AI leadership shakeup ---
    ("06-jeffdean-farewell-x.png", RAW / "x-jeffdean-farewell.png", None),
    ("07-jeffdean-discoveryloop-x.png", RAW / "x-jeffdean-discoveryloop.png", None),
    ("08-hassabis-chair-x.png", RAW / "x-hassabis-chair.png", None),
    ("09-jiqizhixin-hassabis-rumor.png", RAW / "wx-jiqizhixin-rumor.png", (0.02, 0.28, 0.98, 0.47)),
    # --- News 3: AI actor "Fang Taozi" contact-lens ad ---
    ("10-nbd-fangtaozi-report.png", RAW / "m-nbd-fangtaozi.png", (0.0, 0.055, 1.0, 1.0)),
    ("11-fangtaozi-price-tiers.png", RAW / "m-sina-fangtaozi-price.png", (0.02, 0.385, 0.98, 0.56)),
    ("12-xinwaner-fangtaozi-removed.png", RAW / "wx-xinwaner-fangtaozi.png", (0.02, 0.01, 0.98, 0.22)),
    ("13-nbd-fangtaozi-law.png", RAW / "m-nbd-fangtaozi-law.png", (0.0, 0.293, 1.0, 0.625)),
    ("14-nbd-fangtaozi-fine.png", RAW / "m-nbd-fangtaozi-fine.png", (0.0, 0.409, 1.0, 0.632)),
    # --- News 4: Apple Intelligence x Qwen in mainland China ---
    ("15-ithome-apple-qwen.png", RAW / "ithome-apple-qwen.png", (0.02, 0.02, 0.98, 0.62)),
    ("16-apple-qwen-requirements.png", RAW / "ithome-apple-qwen-setup.png", (0.02, 0.24, 0.98, 0.62)),
    ("17-apple-qwen-siri.png", RAW / "ithome-apple-qwen-siri.png", (0.02, 0.28, 0.98, 0.60)),
    ("18-apple-cn-still-unavailable.png", RAW / "apple-cn-still-unavailable.png", (0.02, 0.30, 0.98, 0.62)),
    ("19-baidu-visual-search.png", RAW / "sina-baidu-component.png", (0.02, 0.30, 0.98, 0.68)),
    # --- News 5: Meta Muse Code ---
    ("20-cnbc-muse-code.png", RAW / "cnbc-muse-code.png", (0.175, 0.155, 0.90, 0.325)),
    ("21-macrumors-muse-contributor.png", RAW / "macrumors-muse-20x.png", (0.04, 0.10, 0.72, 0.42)),
    # --- News 4: price war ---
    ("22-openai-price-x.png", RAW / "x-openai-price.png", None),
    ("23-openaidevs-fastmode-x.png", RAW / "x-openaidevs-fastmode.png", None),
    ("24-anthropic-sonnet-intro-price.png", RAW / "anthropic-sonnet-pricing.png", (0.09, 0.28, 0.99, 0.44)),
    # --- News 5: DeepSeek stuck for 22 hours ---
    ("25-linuxdo-prompt-terminal.png", RAW / "linuxdo-prompt.png", (0.30, 0.03, 0.84, 0.45)),
    ("26-linuxdo-22h-stuck.png", RAW / "linuxdo-prompt.png", (0.30, 0.42, 0.84, 0.78)),
    ("27-linuxdo-replies.png", RAW / "linuxdo-22h-replies.png", (0.24, 0.02, 0.72, 0.52)),
    ("28-linuxdo-reversal-pi.png", RAW / "linuxdo-reversal.png", (0.30, 0.46, 0.84, 0.95)),
    # --- News 6: Qwen3.8-Max ---
    ("29-qwen-ecommerce-bench.png", RAW / "qwen-416.png", (0.26, 0.58, 0.98, 0.92)),
    ("30-ohmycli-repo.png", RAW / "ohmycli-repo.png", (0.02, 0.02, 0.74, 0.23)),
    ("31-ohmycli-commits.png", RAW / "ohmycli-commits.png", (0.06, 0.10, 0.94, 0.62)),
    # --- News 7: Agent Village ---
    ("32-edgecity-village-x.png", RAW / "x-edgecity-village.png", None),
    ("33-village-numbers.png", RAW / "cosmos-village-numbers.png", (0.20, 0.36, 0.86, 0.86)),
    # --- Tools: Claude Code cross-session messaging ---
    ("34-claudedevs-crosssession-x.png", RAW / "x-claudedevs-crosssession.png", None),
    ("35-claude-docs-crosssession.png", RAW / "claude-docs-crosssession.png", (0.270, 0.06, 0.72, 0.42)),
    ("36-claude-docs-usecases.png", RAW / "claude-docs-tools.png", (0.276, 0.42, 0.71, 0.80)),
    # --- Tools ---
    ("37-rescript-showhn.png", RAW / "rescript-hn.png", (0.02, 0.02, 0.80, 0.26)),
    ("38-rescript-ui.jpg", OLD / "rescript-ui-01.png", None),
    ("39-liquidai-lfm-x.png", RAW / "x-liquidai-lfm25.png", None),
    ("40-lfm-benchmarks.png", RAW / "lfm-hf-bench.png", (0.135, 0.28, 0.60, 0.52)),
    ("41-ruview-demo.png", RAW / "ruview-demo.png", (0.02, 0.42, 0.98, 0.98)),
    ("42-ruview-entities.png", RAW / "ruview-entities.png", (0.02, 0.28, 0.76, 0.68)),
    # --- Insights: Conduit ---
    ("43-naomi-bashkansky-x.png", RAW / "x-naomi-conduit.png", None),
    ("44-conduit-training-headset.jpg", OLD / "conduit-03.jpg", None),
    ("45-conduit-booth.jpg", OLD / "conduit-08.png", None),
    ("46-conduit-corridor.jpg", OLD / "conduit-09.png", None),
    ("47-conduit-60hz-noise.png", OLD / "conduit-02.png", None),
    ("48-conduit-simple-keyboard.jpg", OLD / "conduit-06.jpg", None),
    # --- Insights: Transluce user awareness ---
    ("49-transluce-x-post.png", RAW / "x-transluce-awareness.png", None),
    ("50-transluce-askell-shift.png", RAW / "transluce-amanda.png", (0.10, 0.28, 0.90, 0.66)),
    ("51-transluce-borderline.png", RAW / "transluce-borderline.png", (0.10, 0.30, 0.90, 0.66)),
    # --- Insights: AI teammate paper ---
    ("52-teammate-paper-fig1.png", RAW / "arxiv-teammate-fig1.png", (0.14, 0.50, 0.86, 0.92)),
    ("53-teammate-paper-fig2.png", RAW / "arxiv-teammate-fig2.png", (0.14, 0.28, 0.86, 0.78)),
    # --- Fun: gstack ---
    ("54-gstack-roles.png", RAW / "gstack-roles.png", (0.16, 0.10, 0.84, 0.70)),
    ("55-gstack-dashboard.jpg", OLD / "gstack-dashboard.png", None),
    # --- Bonus ---
    ("56-hf-glm-forensics.png", RAW / "hf-timeline-glm.png", (0.275, 0.60, 0.79, 0.80)),
]

def autotrim(im: Image.Image, tol: int = 6) -> Image.Image:
    """Drop uniform blank margins left by a crop, keeping a small padding.

    A crop window sized for one screen often leaves a wide band of page
    background. Trimming it keeps the evidence filling the WeChat column.
    """
    from PIL import ImageChops

    bg = Image.new("RGB", im.size, im.getpixel((im.width - 1, im.height - 1)))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > tol else 0)
    box = diff.getbbox()
    if not box:
        return im
    pad = 12
    left = max(0, box[0] - pad)
    top = max(0, box[1] - pad)
    right = min(im.width, box[2] + pad)
    bottom = min(im.height, box[3] + pad)
    if right - left < 80 or bottom - top < 60:
        return im
    return im.crop((left, top, right, bottom))


built: list[str] = []
for name, src, box in JOBS:
    if not src.exists():
        raise SystemExit(f"[fail] missing source: {src}")
    im = Image.open(src)
    if box:
        w, h = im.size
        left, top, right, bottom = box
        im = im.crop((int(w * left), int(h * top), int(w * right), int(h * bottom)))
    im = im.convert("RGB")
    if box:
        im = autotrim(im)
    if im.width > TARGET_WIDTH:
        ratio = TARGET_WIDTH / im.width
        im = im.resize((TARGET_WIDTH, max(1, round(im.height * ratio))), Image.LANCZOS)
    target = OUT / name
    if target.suffix.lower() in (".jpg", ".jpeg"):
        im.convert("RGB").save(target, quality=88, optimize=True)
    else:
        im.convert("RGB").save(target, optimize=True)
    built.append(f"{name}  {im.size[0]}x{im.size[1]}")

print(f"[ok] built {len(built)} assets into {OUT}")
for line in built:
    print("   ", line)
