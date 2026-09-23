"""Midnight AI Lab HUD system: black glass panels, thin violet borders, grid, brackets, scanline."""
from __future__ import annotations

from .core import Doc, linear, n, radial
from .ornament import diamond
from .palette import P
from .text import measure, text_path, text_use


def grid(doc: Doc, W: float, H: float, step: int = 24, key: str = "hudGrid") -> str:
    doc.defs(key, f'<pattern id="{key}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
                  f'<path d="M{step} 0L0 0L0 {step}" fill="none" stroke="#371B5C" stroke-width=".6" opacity=".35"/></pattern>')
    return f'<rect width="{n(W)}" height="{n(H)}" fill="url(#{key})"/>'


def scanline(doc: Doc, W: float, H: float, dur: float = 7, key: str = "hudScan") -> str:
    g = linear(doc, key + "G", [(0, P.glow, 0), (.5, P.glow, .07), (1, P.glow, 0)], 0, 0, 0, 1)
    doc.keyframes(key, f"0%{{transform:translateY(-80px)}}100%{{transform:translateY({n(H + 80)}px)}}")
    return f'<rect width="{n(W)}" height="60" fill="{g}" style="animation:{key} {n(dur)}s linear infinite"/>'


def brackets(W: float, H: float, inset: float = 10, arm: float = 22, color: str | None = None) -> str:
    c = color or P.glow
    d = (f"M{inset} {inset + arm}V{inset}H{inset + arm}M{W - inset - arm} {inset}H{W - inset}V{inset + arm}"
         f"M{W - inset} {H - inset - arm}V{H - inset}H{W - inset - arm}M{inset + arm} {H - inset}H{inset}V{H - inset - arm}")
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="square"/>'


def panel(doc: Doc, W: float, H: float, key: str = "pn", r: float = 18, grid_on: bool = True,
          glow_at: tuple = (.5, .15)) -> tuple[str, str]:
    """(under, over) layers for a dark-glass HUD panel with its own clip-path `{key}Clip`."""
    bg = linear(doc, f"{key}Bg", [(0, "#0B0712"), (.55, "#050507"), (1, "#020203")], 0, 0, 0, 1)
    halo = radial(doc, f"{key}Halo", [(0, "#3A126D", .55), (.6, "#261240", .18), (1, "#020203", 0)], glow_at[0], glow_at[1], .75)
    border = linear(doc, f"{key}Bd", [(0, P.glow, .9), (.35, P.primary, .5), (.7, P.deep, .45), (1, P.glow, .8)], 0, 0, 1, 1)
    doc.defs(f"{key}Clip", f'<clipPath id="{key}Clip"><rect width="{n(W)}" height="{n(H)}" rx="{n(r)}"/></clipPath>')
    under = (f'<rect width="{n(W)}" height="{n(H)}" rx="{n(r)}" fill="{bg}"/>'
             f'<g clip-path="url(#{key}Clip)"><rect width="{n(W)}" height="{n(H)}" fill="{halo}"/>'
             + (grid(doc, W, H) if grid_on else "") + "</g>")
    doc.keyframes("hudPulse", "0%,100%{opacity:.55}50%{opacity:1}")
    over = (f'<rect x=".75" y=".75" width="{n(W - 1.5)}" height="{n(H - 1.5)}" rx="{n(r - .5)}" fill="none" stroke="{border}" stroke-width="1.5" '
            f'style="animation:hudPulse 5s ease-in-out infinite"/>'
            f'<rect x="6" y="6" width="{n(W - 12)}" height="{n(H - 12)}" rx="{n(max(2, r - 5))}" fill="none" stroke="{P.accent}" stroke-opacity=".12"/>'
            + brackets(W, H, 12, 20))
    return under, over


def title_bar(doc: Doc, x: float, y: float, sector: str, label: str, title: str, size: float = 34,
              anchor: str = "start", key: str = "tb", width: float | None = None, kicker: str | None = None) -> tuple[str, float]:
    """Kicker (// SECTOR 03 · LABEL) + Cinzel title with ice gradient + neon underline."""
    k, kw = text_use(doc, kicker or f"// CHAMBER {sector}  •  {label}", x, y, 11.5, "ui6", anchor=anchor, tracking=.34, fill=P.ice)
    tw = measure(title, "cinzel9", size, .06)
    if width and tw > width:
        size *= width / tw
        tw = measure(title, "cinzel9", size, .06)
    ty = y + 14 + size * .78
    ice = linear(doc, f"{key}Ice", [(0, "#FFFFFF"), (.55, "#E3D1FD"), (1, "#C4A6F1")], 0, ty - size * .75, 0, ty, units="userSpaceOnUse")
    tp, _ = text_path(title, x, ty, size, "cinzel9", anchor=anchor, tracking=.06)
    d = tp[len('<path d="'):-3]
    doc.defs("tbBlur", '<filter id="tbBlur" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>')
    x0 = x - (tw / 2 if anchor == "middle" else tw if anchor == "end" else 0)
    line = linear(doc, f"{key}Ln", [(0, P.glow), (.6, P.primary, .8), (1, P.primary, 0)], 0, 0, 1, 0)
    out = (k + f'<path d="{d}" fill="{P.primary}" opacity=".55" filter="url(#tbBlur)"/><path d="{d}" fill="{ice}"/>'
           f'<rect x="{n(x0)}" y="{n(ty + 12)}" width="{n(min(tw + 60, 520))}" height="1.6" fill="{line}"/>' + diamond(x0, ty + 12.8, 3.2, P.glow))
    return out, ty + 12


def chip(doc: Doc, x: float, y: float, label: str, size: float = 13, fill: str | None = None,
         stroke: str | None = None, color: str | None = None, h: float = 26, dashed: bool = False) -> tuple[str, float]:
    w = measure(label, "ui5", size) + 22
    t, _ = text_use(doc, label, x + 11, y + h / 2 + size * .36, size, "ui5", fill=color or P.text)
    da = ' stroke-dasharray="4 3"' if dashed else ""
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{h}" rx="{n(h / 2)}" fill="{fill or "#1A0D2B"}" '
            f'stroke="{stroke or "#4A1C85"}"{da}/>' + t), w


def flow_chips(doc: Doc, x: float, y: float, labels, max_w: float, gap: float = 8, row_h: float = 34, **kw) -> tuple[str, float]:
    out, cx, cy = [], x, y
    for lb in labels:
        svg, w = chip(doc, cx, cy, lb, **kw)
        if cx + w > x + max_w and cx > x:
            cx, cy = x, cy + row_h
            svg, w = chip(doc, cx, cy, lb, **kw)
        out.append(svg)
        cx += w + gap
    return "".join(out), cy + row_h


def status_pill(doc: Doc, x: float, y: float, text: str, anchor: str = "start", color: str | None = None, size: float = 11) -> tuple[str, float]:
    c = color or P.glow
    w = measure(text, "ui6", size, .28) + 38
    x0 = x - (w if anchor == "end" else w / 2 if anchor == "middle" else 0)
    doc.keyframes("pillDot", "0%,100%{opacity:.3}50%{opacity:1}")
    t, _ = text_use(doc, text, x0 + 26, y + 16 + size * .02, size, "ui6", tracking=.28, fill=c)
    return (f'<rect x="{n(x0)}" y="{n(y)}" width="{n(w)}" height="24" rx="12" fill="#170B27" stroke="{c}" stroke-opacity=".75"/>'
            f'<circle cx="{n(x0 + 14)}" cy="{n(y + 12)}" r="4" fill="{c}" style="animation:pillDot 1.4s ease-in-out infinite"/>' + t), w
