"""Castle backdrops — crops of your two castle paintings, embedded as WebP.

SVGs shown through <img> on GitHub can't load other files, so every panel that
uses a painting carries its own crop (sized to the panel) inside the SVG.
"""
from __future__ import annotations

import base64
import io
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from .core import Doc, n

BG = Path(__file__).resolve().parents[2] / "assets" / "backgrounds"
SOURCES = {"land": "castle-landscape.jpg", "port": "castle-portrait.jpg"}


@lru_cache(maxsize=None)
def crop(name: str, box: tuple | None = None, size: tuple = (1000, 600), mirror: bool = False,
         blur: float = 0, bright: float = 1.0, quality: int = 72, centering: tuple = (.5, .5)) -> str:
    """Crop (source-pixel box) → cover-fit to `size` → optional mirror/blur/brightness → WebP data URI."""
    im = Image.open(BG / SOURCES[name]).convert("RGB")
    if box:
        im = im.crop(box)
    if mirror:
        im = ImageOps.mirror(im)
    im = ImageOps.fit(im, size, Image.LANCZOS, centering=centering)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if bright != 1.0:
        im = ImageEnhance.Brightness(im).enhance(bright)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def image(doc: Doc, name: str, x: float, y: float, w: float, h: float, box: tuple | None = None,
          px: float = 1.0, key: str | None = None, opacity: float = 1.0, **kw) -> str:
    """<image> of a painting crop placed at (x, y, w, h); px = pixel density of the embedded crop."""
    uri = crop(name, box, (round(w * px), round(h * px)), **kw)
    k = key or doc.uid("bg")
    doc.defs(k, f'<image id="{k}" href="{uri}" width="{n(w)}" height="{n(h)}" preserveAspectRatio="none"/>')
    op = f' opacity="{n(opacity, 2)}"' if opacity < 1 else ""
    return f'<use href="#{k}" x="{n(x)}" y="{n(y)}"{op}/>'
