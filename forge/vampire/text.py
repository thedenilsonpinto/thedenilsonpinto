"""Text → SVG outlines.

GitHub serves README SVGs as images, so web fonts can't be fetched. We shape
text with HarfBuzz (kerning, ligatures) and emit glyph outlines instead, so every
visitor sees the same typography. Two output modes:

  * text_path(): one absolute <path> per run — use for display titles that need
    gradients, masks or filters across the whole word.
  * text_use():  glyph outlines stored once in <defs> and placed with <use> —
    compact for body copy that repeats letters.
"""
from __future__ import annotations

import io
from functools import lru_cache
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from .core import Doc, attrs, compact_path, n

try:  # optional, gives proper kerning/ligatures
    import uharfbuzz as hb
except Exception:  # pragma: no cover
    hb = None

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"

FONTS = {
    "cinzel9": "Cinzel-900.woff2",           # section titles
    "cinzel7": "Cinzel-700.woff2",
    "serif_i": "CormorantGaramond-500i.woff2",  # taglines / quotes
    "ui4": "ChakraPetch-400.woff2",          # cyber HUD labels
    "ui5": "ChakraPetch-500.woff2",
    "ui6": "ChakraPetch-600.woff2",
    "mono": "JetBrainsMono-400.woff2",       # terminal
    "mono7": "JetBrainsMono-700.woff2",
}

# short prefixes for glyph ids inside documents
_PREFIX = {k: f"g{i:x}" for i, k in enumerate(FONTS)}


# ── Synthetic glyphs ─────────────────────────────────────────────────────────
# Web subsets of our fonts omit box-drawing/geometric symbols. These are drawn
# as simple shapes in font units (y-up), sized to the font's cell.
def _synth_shapes(ch: str, adv: float, cap: float):
    t = 70            # stroke thickness
    mid = cap * .5
    top, bot = cap + 260, -300
    cx = adv / 2
    R = lambda x0, y0, x1, y1: ("poly", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    table = {
        "\u2500": [R(0, mid - t / 2, adv, mid + t / 2)],                                  # ─
        "\u2502": [R(cx - t / 2, bot, cx + t / 2, top)],                                  # │
        "\u250c": [R(cx - t / 2, mid + t / 2, adv, mid - t / 2), R(cx - t / 2, bot, cx + t / 2, mid + t / 2)],  # ┌
        "\u2514": [R(cx - t / 2, mid - t / 2, adv, mid + t / 2), R(cx - t / 2, mid - t / 2, cx + t / 2, top)],  # └
        "\u251c": [R(cx, mid - t / 2, adv, mid + t / 2), R(cx - t / 2, bot, cx + t / 2, top)],                  # ├
        "\u2588": [R(0, bot + 40, adv, top - 60)],                                        # █
        "\u2591": [R(0, bot + 40, adv, top - 60)],                                        # ░ (drawn same; fade via opacity)
        "\u25b6": [("poly", [(adv * .18, 0), (adv * .82, cap * .5), (adv * .18, cap)])],   # ▶
        "\u25c6": [("poly", [(cx, cap * .95), (adv * .92, cap * .45), (cx, -cap * .05), (adv * .08, cap * .45)])],  # ◆
        "\u25cf": [("circle", (cx, cap * .45, adv * .36))],                                # ●
        "\u2713": [("poly", [(adv * .08, cap * .5), (adv * .22, cap * .62), (adv * .40, cap * .30), (adv * .84, cap * .92), (adv * .96, cap * .80), (adv * .40, 0)])],  # ✓
        "\u2192": [R(adv * .05, mid - t / 2, adv * .7, mid + t / 2), ("poly", [(adv * .6, mid + 190), (adv * .98, mid), (adv * .6, mid - 190)])],  # →
        "\u2194": [R(adv * .25, mid - t / 2, adv * .75, mid + t / 2), ("poly", [(adv * .32, mid + 170), (adv * .02, mid), (adv * .32, mid - 170)]), ("poly", [(adv * .68, mid + 170), (adv * .98, mid), (adv * .68, mid - 170)])],  # ↔
    }
    return table.get(ch)


def _shapes_d(shapes, sx, sy, dx, dy, d=0):
    """Primitives (font units, y-up) → path data under x'=sx*x+dx, y'=sy*y+dy."""
    out = []
    for kind, data in shapes:
        if kind == "poly":
            p = [(sx * x + dx, sy * y + dy) for x, y in data]
            out.append("M" + "L".join(f"{n(x, d)} {n(y, d)}" for x, y in p) + "Z")
        else:
            cx, cy, r = data
            X, Y, rr = sx * cx + dx, sy * cy + dy, abs(sx) * r
            out.append(f"M{n(X - rr, d)} {n(Y, d)}a{n(rr, d)} {n(rr, d)} 0 1 0 {n(2 * rr, d)} 0a{n(rr, d)} {n(rr, d)} 0 1 0 {n(-2 * rr, d)} 0Z")
    return "".join(out)


class MissingGlyph(Exception):
    pass


class Face:
    def __init__(self, key: str):
        self.key = key
        tt = TTFont(FONT_DIR / FONTS[key])
        self.tt = tt
        self.upem = tt["head"].unitsPerEm
        self.gs = tt.getGlyphSet()
        self.order = tt.getGlyphOrder()
        self.cmap = tt.getBestCmap()
        self.hmtx = tt["hmtx"].metrics
        os2 = tt["OS/2"]
        from fontTools.pens.boundsPen import BoundsPen
        bp = BoundsPen(self.gs)
        self.gs[self.cmap[ord("H")]].draw(bp)
        self.ascent = bp.bounds[3] if bp.bounds else int(self.upem * .7)   # cap height
        self.xheight = getattr(os2, "sxHeight", 0) or int(self.upem * .5)
        self.hbfont = None
        if hb is not None:
            buf = io.BytesIO()
            tt2 = TTFont(FONT_DIR / FONTS[key])
            tt2.flavor = None
            tt2.save(buf)
            self.hbfont = hb.Font(hb.Face(hb.Blob(buf.getvalue())))
        self._outline_cache: dict[str, str] = {}

    # shaping ---------------------------------------------------------------
    def cell(self) -> float:
        g = self.cmap.get(ord("0")) or self.cmap.get(ord("M"))
        return self.hmtx[g][0]

    def shape(self, text: str):
        """→ list of (glyph, x_advance, x_offset, y_offset) in font units.
        Characters missing from the font use synthetic shapes ("§<char>")."""
        out, run = [], ""
        for ch in text:
            if ord(ch) in self.cmap or ch in " \u00a0":
                run += ch
                continue
            if _synth_shapes(ch, self.cell(), self.ascent) is None:
                raise MissingGlyph(f"{self.key}: no glyph for {ch!r} (U+{ord(ch):04X}) in {text!r}")
            out += self._shape_run(run)
            run = ""
            out.append(("\u00a7" + ch, self.cell(), 0, 0))
        return out + self._shape_run(run)

    def _shape_run(self, text: str):
        if not text:
            return []
        if self.hbfont is not None:
            b = hb.Buffer()
            b.add_str(text)
            b.guess_segment_properties()
            hb.shape(self.hbfont, b, {"kern": True, "liga": True})
            return [(self.order[i.codepoint], p.x_advance, p.x_offset, p.y_offset)
                    for i, p in zip(b.glyph_infos, b.glyph_positions)]
        out = []
        for ch in text:
            g = self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))
            out.append((g, self.hmtx[g][0], 0, 0))
        return out

    def outline(self, gname: str) -> str:
        """Glyph outline in y-down font units (integers)."""
        if gname.startswith("\u00a7"):
            return _shapes_d(_synth_shapes(gname[1], self.cell(), self.ascent), 1, -1, 0, 0)
        if gname not in self._outline_cache:
            pen = SVGPathPen(self.gs, ntos=lambda v: n(v, 0))
            self.gs[gname].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
            self._outline_cache[gname] = compact_path(pen.getCommands(), 0)
        return self._outline_cache[gname]


@lru_cache(maxsize=None)
def face(key: str) -> Face:
    return Face(key)


def _layout(text: str, font: str, size: float, tracking: float):
    """Glyph placements in px relative to the pen start, plus total width.
    tracking is in em units (0.1 = 10% of the font size added per glyph)."""
    f = face(font)
    s = size / f.upem
    x, placed = 0.0, []
    glyphs = f.shape(text)
    for i, (g, adv, xo, yo) in enumerate(glyphs):
        placed.append((g, x + xo * s, -yo * s))
        x += adv * s + (tracking * size if i < len(glyphs) - 1 else 0)
    return placed, x, s


def measure(text: str, font: str, size: float, tracking: float = 0) -> float:
    return _layout(text, font, size, tracking)[1]


def char_stops(text: str, font: str, size: float, tracking: float = 0) -> list[float]:
    """x position (px) after each character — for typing reveals."""
    out = []
    for i in range(1, len(text) + 1):
        out.append(measure(text[:i], font, size, tracking))
    return out


def _anchor_x(x: float, width: float, anchor: str) -> float:
    return x - width / 2 if anchor == "middle" else x - width if anchor == "end" else x


def text_path(text: str, x: float, y: float, size: float, font: str = "cinzel7",
              anchor: str = "start", tracking: float = 0, d: int = 1, **kw) -> tuple[str, float]:
    """Whole run as one absolute <path>. Returns (svg, width)."""
    placed, width, s = _layout(text, font, size, tracking)
    x0 = _anchor_x(x, width, anchor)
    f = face(font)
    parts = []
    for g, gx, gy in placed:
        if g.startswith("\u00a7"):
            parts.append(_shapes_d(_synth_shapes(g[1], f.cell(), f.ascent), s, -s, x0 + gx, y + gy, d))
            continue
        pen = SVGPathPen(f.gs, ntos=lambda v: n(v, d))
        f.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x0 + gx, y + gy)))
        c = pen.getCommands()
        if c:
            parts.append(c)
    return f'<path d="{compact_path("".join(parts), d)}"{attrs(**kw)}/>', width


def path_d(text: str, x: float, y: float, size: float, font: str = "cinzel7",
           anchor: str = "start", tracking: float = 0, d: int = 1) -> str:
    """Just the path data (for clipPath/mask use)."""
    svg, _ = text_path(text, x, y, size, font, anchor, tracking, d)
    return svg[len('<path d="'):-3]


def text_use(doc: Doc, text: str, x: float, y: float, size: float, font: str = "ui5",
             anchor: str = "start", tracking: float = 0, **kw) -> tuple[str, float]:
    """Glyphs stored once per document in <defs>, placed with <use>. Returns (svg, width)."""
    f = face(font)
    placed, width, s = _layout(text, font, size, tracking)
    x0 = _anchor_x(x, width, anchor)
    pre = _PREFIX[font]
    uses = []
    for g, gx, gy in placed:
        o = f.outline(g)
        if not o:
            continue  # spaces
        gid = f"{pre}_{_gid(f, g)}"
        if gid not in doc.glyph_defs:
            doc.glyph_defs[gid] = f'<path id="{gid}" d="{o}"/>'
        ux = gx / s
        uy = gy / s
        uses.append(f'<use href="#{gid}" x="{n(ux, 0)}"' + (f' y="{n(uy, 0)}"' if abs(uy) > .5 else "") + "/>")
    tr = f"translate({n(x0, 2)} {n(y, 2)}) scale({n(s, 5)})"
    return f'<g transform="{tr}"{attrs(**kw)}>{"".join(uses)}</g>', width


_GID: dict[tuple[str, str], str] = {}


def _gid(f: Face, g: str) -> str:
    k = (f.key, g)
    if k not in _GID:
        _GID[k] = ("s" + format(ord(g[1]), "x")) if g.startswith("\u00a7") else format(f.order.index(g), "x")
    return _GID[k]


def wrap(text: str, font: str, size: float, max_w: float, tracking: float = 0) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if cur and measure(t, font, size, tracking) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def cap(font: str, size: float) -> float:
    """Cap height in px — for optically centring caps text."""
    f = face(font)
    return f.ascent * size / f.upem
