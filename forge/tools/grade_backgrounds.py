#!/usr/bin/env python3
"""Grade the castle artwork into the Midnight AI Lab palette (one-time step).

  pip install numpy pillow
  python forge/tools/grade_backgrounds.py SRC_LANDSCAPE SRC_PORTRAIT

Writes assets/backgrounds/castle-landscape.jpg and castle-portrait.jpg. The only change
is that warm pixels (the few orange torch flames) are turned violet, so the whole page
stays black + violet; everything else is left exactly as painted.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[2] / "assets" / "backgrounds"
VIOLET_HUE = 272 / 360


def grade(src: str) -> Image.Image:
    im = Image.open(src).convert("RGB")
    hsv = np.asarray(im.convert("HSV")).astype(np.float32) / 255
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    deg = h * 360
    warm = ((deg < 75) | (deg > 325)) & (s > .08)
    h = np.where(warm, VIOLET_HUE, h)
    s = np.where(warm, s * .9, s)
    out = np.stack([h, s, v], -1)
    return Image.fromarray((out * 255).round().astype(np.uint8), "HSV").convert("RGB")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    for src, name in zip(sys.argv[1:], ("castle-landscape.jpg", "castle-portrait.jpg")):
        grade(src).save(OUT / name, quality=90, optimize=True, progressive=True, subsampling=0)
        print("wrote", OUT / name)


if __name__ == "__main__":
    main()
