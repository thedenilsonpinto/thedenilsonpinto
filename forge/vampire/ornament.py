"""Gothic ornaments: panel frames, corner filigree, dividers, sigils, emblem."""
from __future__ import annotations

import math

from .core import Doc, glow_filter, linear, n
from .palette import P


def corner(x: float, y: float, sx: int = 1, sy: int = 1, s: float = 1, color: str | None = None) -> str:
    """Gothic filigree bracket for a panel corner (x,y = the corner point)."""
    c = color or P.deep
    d = ("M0 34L0 8Q0 0 8 0L34 0M6 40L6 14Q6 6 14 6L40 6"
         "M14 14Q22 10 26 18Q20 22 14 14ZM4 52L4 60M52 4L60 4")
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(sx * s, 2)} {n(sy * s, 2)})" fill="none" stroke="{c}" stroke-width="1.4">'
            f'<path d="{d}"/><path d="M11 11L17 11L17 17L11 17Z" fill="{P.glow}" stroke="none" transform="rotate(45 14 14)"/></g>')


def frame(doc: Doc, w: float, h: float, r: float = 22, fill: str | None = None, key: str = "fr",
          corners: bool = True, clip: bool = True) -> tuple[str, str]:
    """Panel background + (clip-path id, border/corners overlay). Returns (bg, overlay)."""
    bg = fill or linear(doc, f"{key}Bg", [(0, "#0B0B0C"), (1, "#050505")], 0, 0, 0, 1)
    border = linear(doc, f"{key}Bd", [(0, "#1F0F34"), (.5, P.deep), (1, "#1F0F34")], 0, 0, 1, 0)
    if clip:
        doc.defs(f"{key}Clip", f'<clipPath id="{key}Clip"><rect width="{n(w)}" height="{n(h)}" rx="{n(r)}"/></clipPath>')
    under = f'<rect width="{n(w)}" height="{n(h)}" rx="{n(r)}" fill="{bg}"/>'
    over = (f'<rect x=".75" y=".75" width="{n(w - 1.5)}" height="{n(h - 1.5)}" rx="{n(r - .5)}" fill="none" stroke="{border}" stroke-width="1.5"/>'
            f'<rect x="7" y="7" width="{n(w - 14)}" height="{n(h - 14)}" rx="{n(max(2, r - 6))}" fill="none" stroke="#FFFFFF" stroke-opacity=".04"/>')
    if corners:
        over += corner(14, 14) + corner(w - 14, 14, -1) + corner(14, h - 14, 1, -1) + corner(w - 14, h - 14, -1, -1)
    return under, over


def diamond(x: float, y: float, r: float, fill: str) -> str:
    return f'<path d="M{n(x)} {n(y - r)}L{n(x + r)} {n(y)}L{n(x)} {n(y + r)}L{n(x - r)} {n(y)}Z" fill="{fill}"/>'


def rule(doc: Doc, x0: float, x1: float, y: float, center: bool = True, key: str = "rl") -> str:
    """Thin neon rule fading at both ends, with a central gem."""
    g = linear(doc, f"{key}G", [(0, P.deep, 0), (.5, P.accent), (1, P.deep, 0)], 0, 0, 1, 0)
    cx = (x0 + x1) / 2
    o = f'<rect x="{n(x0)}" y="{n(y - .6)}" width="{n(x1 - x0)}" height="1.2" fill="{g}"/>'
    if center:
        o += diamond(cx, y, 6, P.bg0) + f'<path d="M{n(cx)} {n(y - 6)}L{n(cx + 6)} {n(y)}L{n(cx)} {n(y + 6)}L{n(cx - 6)} {n(y)}Z" fill="none" stroke="{P.accent}" stroke-width="1.2"/>' + diamond(cx, y, 2.2, P.glow)
        o += diamond(cx - 22, y, 2.4, P.deep) + diamond(cx + 22, y, 2.4, P.deep)
    return o


def bat_wings(cx: float, cy: float, s: float = 1, fill: str = "#0A0A0C", stroke: str | None = None) -> str:
    """Stylised spread bat wings (for crests), centred."""
    w = ("M0 -6C-10 -14 -30 -22 -58 -20C-50 -14 -48 -8 -50 -2C-42 -6 -36 -4 -32 2C-26 -2 -20 0 -16 6"
         "C-12 2 -6 2 0 8C6 2 12 2 16 6C20 0 26 -2 32 2C36 -4 42 -6 50 -2C48 -8 50 -14 58 -20C30 -22 10 -14 0 -6Z")
    st = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
    return f'<path transform="translate({n(cx)} {n(cy)}) scale({n(s, 3)})" d="{w}" fill="{fill}"{st}/>'


def emblem(doc: Doc, cx: float, cy: float, s: float = 1, spin: bool = True) -> str:
    """Crest: rune ring, bat wings, fang-shield, circuit drop."""
    shield = linear(doc, "emS", [(0, "#16161B"), (1, "#070708")], 0, 0, 0, 1)
    drop = linear(doc, "emD", [(0, P.ice), (.45, P.glow), (1, P.deep)], 0, 0, 0, 1)
    gl = glow_filter(doc, "emGlow", 2.5, 1)
    doc.keyframes("emSpin", "to{transform:rotate(360deg)}")
    doc.keyframes("emBeat", "0%,100%{transform:scale(1)}10%{transform:scale(1.12)}20%{transform:scale(1)}30%{transform:scale(1.08)}45%{transform:scale(1)}")
    doc.css("em", ".emR{transform-box:fill-box;transform-origin:center;animation:emSpin 40s linear infinite}"
                  ".emB{transform-box:fill-box;transform-origin:center;animation:emBeat 2.4s ease-in-out infinite}")
    ticks = "".join(f'<path d="M{n(math.cos(math.radians(a)) * 58)} {n(math.sin(math.radians(a)) * 58)}L{n(math.cos(math.radians(a)) * (52 if a % 30 else 49))} {n(math.sin(math.radians(a)) * (52 if a % 30 else 49))}"/>' for a in range(0, 360, 10))
    ring = (f'<g class="{"emR" if spin else ""}" fill="none" stroke="{P.deep}" stroke-width="1.2"><circle r="60"/><circle r="46" stroke-dasharray="3 5"/>'
            f'<g stroke="{P.accent}">{ticks}</g></g>')
    body = (f'{bat_wings(0, -4, 1.05, "#0B0B0E", P.deep)}'
            f'<path d="M0 -36L22 -26L20 6Q15 26 0 40Q-15 26 -20 6L-22 -26Z" fill="{shield}" stroke="{P.accent}" stroke-width="1.6"/>'
            f'<path d="M-14 -30L-10 -42L-6 -30M14 -30L10 -42L6 -30M-4 -34L0 -48L4 -34" fill="{P.silver}"/>'
            f'<g class="emB" filter="{gl}"><path d="M0 -20C6 -10 12 -2 12 8A12 12 0 0 1 -12 8C-12 -2 -6 -10 0 -20Z" fill="{drop}"/></g>'
            f'<path d="M-5 4L-5 12L0 16M5 2L5 10L9 13" stroke="#FFFFFF" stroke-width="1" fill="none" opacity=".8"/>'
            f'<circle cx="0" cy="16" r="1.4" fill="#fff"/><circle cx="9" cy="13" r="1.2" fill="#fff"/>')
    return f'<g transform="translate({n(cx)} {n(cy)}) scale({n(s, 3)})">{ring}{body}</g>'
