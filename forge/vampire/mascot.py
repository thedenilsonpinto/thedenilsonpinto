"""The Midnight AI Vampire — an ORIGINAL character, the mascot of the Midnight AI Lab.

Not based on any real person or existing character. One master design, drawn as a
2D rig so every scene shows exactly the same vampire:

  tall, elegant, realistic proportions (~8 heads) · pale moonlit skin · sharp jaw and
  cheekbones · black, slightly messy swept hair with loose strands · subtly pointed ears ·
  dark violet glowing eyes · small realistic fangs · long black gothic coat with a high
  standing collar and satin lapels · layered black vest + silk cravat · silver clasps,
  silver chain and rings · a dark violet gemstone at the throat (his signature) ·
  a violet energy signature (particles, rim light, aura).

Coordinates: feet at (0, 0), y up is negative, ~476 units tall. The head is drawn with
its chin at (0, 0) and mounted at CHIN_Y.
"""
from __future__ import annotations

import math
import random

from .core import Doc, linear, n, radial
from .palette import P

CHIN_Y = -412
NECK_PIVOT = -406
SHOULDER = (41.0, -388.0)
HIP = (14.0, -262.0)
UPPER, FORE = 84.0, 76.0
THIGH, SHIN = 110.0, 112.0


# ── shading helpers ────────────────────────────────────────────────────────────

def _defs(doc: Doc) -> None:
    doc.defs("mvSoft", '<filter id="mvSoft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.1"/></filter>')
    doc.defs("mvSoft2", '<filter id="mvSoft2" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2.4"/></filter>')
    doc.defs("mvGlow", '<filter id="mvGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="1.6" result="b"/>'
                       '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    doc.keyframes("mvEye", "0%,100%{opacity:.55}50%{opacity:1}")
    doc.keyframes("mvGem", "0%,100%{opacity:.45}50%{opacity:1}")


def rim_filter(doc: Doc, k: float = 1.0) -> str:
    """Moonlight from behind-left: a soft violet rim + bloom on the left edges, a faint lavender
    edge on the right. k = drawing scale (pass it for close-ups so the rim stays fine)."""
    key = "mvRim" if k == 1 else f"mvRim{int(k * 100)}"
    d1, d2 = 2.2 / k, 1.2 / k
    doc.defs(key, (
        f'<filter id="{key}" x="-15%" y="-8%" width="130%" height="116%" color-interpolation-filters="sRGB">'
        f'<feOffset in="SourceAlpha" dx="{n(d1, 2)}" dy="{n(-d1 * .25, 2)}" result="o1"/>'
        '<feComposite in="SourceAlpha" in2="o1" operator="out" result="e1"/>'
        f'<feGaussianBlur in="e1" stdDeviation="{n(.45 / k, 2)}" result="e1s"/>'
        f'<feFlood flood-color="{P.glow}" flood-opacity=".78"/><feComposite in2="e1s" operator="in" result="r1"/>'
        f'<feGaussianBlur in="r1" stdDeviation="{n(2.6 / k, 2)}" result="r1b"/>'
        f'<feOffset in="SourceAlpha" dx="{n(-d2, 2)}" dy="0" result="o2"/>'
        '<feComposite in="SourceAlpha" in2="o2" operator="out" result="e2"/>'
        f'<feFlood flood-color="{P.ice}" flood-opacity=".16"/><feComposite in2="e2" operator="in" result="r2"/>'
        f'<feTurbulence type="fractalNoise" baseFrequency="{n(.8 * k, 2)}" numOctaves="2" seed="7" result="nz"/>'
        '<feColorMatrix in="nz" type="matrix" values="0 0 0 0 .55  0 0 0 0 .5  0 0 0 0 .68  0 0 0 .24 -.1" result="nzc"/>'
        '<feComposite in="nzc" in2="SourceAlpha" operator="in" result="grain"/>'
        '<feMerge><feMergeNode in="r1b"/><feMergeNode in="SourceGraphic"/><feMergeNode in="grain"/><feMergeNode in="r1"/><feMergeNode in="r2"/></feMerge></filter>'))
    return f"url(#{key})"


def aura(doc: Doc, rx: float = 110, ry: float = 230, cy: float = -240, strength: float = 1.0) -> str:
    key = "mvAura" if strength == 1 else f"mvAura{round(strength * 100)}"
    g = radial(doc, key, [(0, P.primary, min(1, .34 * strength)), (.45, P.deep, min(1, .14 * strength)), (1, P.deep, 0)])
    doc.keyframes("mvAuraPulse", "0%,100%{opacity:.65;transform:scale(.97)}50%{opacity:1;transform:scale(1.03)}")
    return (f'<ellipse cx="0" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{g}" '
            f'style="transform-box:fill-box;transform-origin:center;animation:mvAuraPulse 6s ease-in-out infinite"/>')


# ── head (chin at 0,0) ─────────────────────────────────────────────────────────

FACE = ("M0 .6C2.6 .6 5 .1 6.6-1C9.4-3 12.8-7.2 15.2-11.8C16.2-13.8 16.8-15.6 17.2-17.6"
        "C17.9-22 18.6-26.5 18.9-31C19.2-37 18.6-43 16.8-47.5C14.4-53.6 8.2-57 0-57"
        "C-8.2-57-14.4-53.6-16.8-47.5C-18.6-43-19.2-37-18.9-31C-18.6-26.5-17.9-22-17.2-17.6"
        "C-16.8-15.6-16.2-13.8-15.2-11.8C-12.8-7.2-9.4-3-6.6-1C-5 .1-2.6 .6 0 .6Z")
EAR = "M18.5-35.5C20-37.2 21.4-38.8 22.6-40.4C23.3-36.8 23-32 22-27.8C21.4-25 20.2-23 18.7-22.4Z"


def _lock(x0: float, y0: float, x1: float, y1: float, bend: float, w: float) -> str:
    """Tapered curved hair lock from root (x0,y0), width w, to a fine tip (x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    mx, my = (x0 + x1) / 2 + nx * bend, (y0 + y1) / 2 + ny * bend
    return (f"M{n(x0 + nx * w / 2)} {n(y0 + ny * w / 2)}Q{n(mx + nx * w * .3)} {n(my + ny * w * .3)} {n(x1)} {n(y1)}"
            f"Q{n(mx - nx * w * .3)} {n(my - ny * w * .3)} {n(x0 - nx * w / 2)} {n(y0 - ny * w / 2)}Z")


# The one hairstyle, identical in every scene: swept to his right (screen-left) from a side part,
# volume on top, messy tips, a few loose strands over the forehead. (root x, y, tip x, y, bend, width)
HAIR_BASE = ("M-18.9-31C-20.8-37-21.2-44.6-19.6-51.4C-17.6-58.6-11.6-64.2-4-66.4C3.4-68.2 11.4-66.8 16.8-62.6"
             "C20.8-59.4 22.6-53.8 22.2-47.6C21.9-41.4 20.9-35.6 18.9-31L17.2-38.4C15.8-43.4 12.4-47.6 7.2-49.8"
             "C1.6-51.8-4.8-51.4-9.8-49.2C-13.8-47.2-16.4-43.4-17.1-38.4Z")
FLICKS = [(-12, -61, -21.2, -60.6, -2.2, 5.5), (-3, -65, -14.6, -67.4, -2.4, 5), (6, -65.8, -3.8, -69.6, -2.6, 4.6),
          (15, -61, 20.6, -64.8, 1.8, 3.6), (-17.5, -52, -22.8, -47.6, -1.6, 4.4), (-8, -64, -19, -65.5, -2, 4.2),
          (11, -64, 3, -70.2, -2.2, 3.8), (19, -55, 24, -57.4, 1.4, 3.2), (-19.4, -44, -23.4, -38.4, -1.2, 3.4)]
STRANDS = [(7.4, -50.4, -3.6, -39.2, 3.4, 5.2), (3.6, -51.2, -9.4, -42.6, 3, 4.6), (10.8, -48.6, 4.6, -40.8, 1.8, 3.6),
           (-2, -50.8, -13.6, -44.8, 2.2, 3.6), (15.4, -45.4, 18.8, -36.4, 1.2, 3.2), (12.6, -47, 9.8, -37.6, 1.4, 2.6)]
FLOW = [(12, -58, -8, -64.4, 3), (14, -54, -12, -61, 3.4), (15, -50, -15.6, -55, 3.2), (17, -46, -18, -47, 2.6),
        (18.6, -52, 19.4, -42, -1.2), (10, -62.6, -2, -66, 1.6), (8, -60, -14, -62.4, 2.4), (16.4, -57, -4, -66.6, 2.8)]


def head(doc: Doc, expr: str = "calm", glow: float = 1.0, eyes: bool = True) -> str:
    """The master face. expr: calm | smirk | fangs | intense. glow scales the eye light."""
    _defs(doc)
    skin = linear(doc, "mvSkin", [(0, "#E6DFEF"), (.42, "#CDC3DD"), (.78, "#9A8DB2"), (1, "#6E6188")], 0, 0, 1, 0)
    skinN = linear(doc, "mvNeck", [(0, "#A99DBE"), (.6, "#5E5270"), (1, "#3B3149")], 0, 0, 1, 1)
    hairG = linear(doc, "mvLock", [(0, "#2A2238"), (.35, "#110D18"), (1, "#040306")], 0, 0, 1, 1)
    sheen = linear(doc, "mvSheen", [(0, "#8E80B0", 0), (.45, "#8E80B0", .55), (1, "#8E80B0", 0)], 0, 0, 1, 0)
    o = [
        # neck (behind the jaw) + ears
        f'<path d="M-7.4-6L7.4-6L8.8 15L-8.8 15Z" fill="{skinN}"/>',
        '<path d="M-7.4-3Q0 3 7.4-3L8 4.6Q0 9.6-8 4.6Z" fill="#2B2238" opacity=".85"/>',
        f'<path d="{EAR}" fill="#8C7FA5"/><path d="{EAR}" transform="scale(-1 1)" fill="#C9BFDA"/>',
        '<path d="M20.2-33C21.2-34.2 22-35.4 22.4-36.4C22.6-33 22.2-29.6 21-26.6Z" fill="#5E5270" opacity=".7"/>',
        '<path d="M-20.2-33C-21.2-34.2-22-35.4-22.4-36.4C-22.6-33-22.2-29.6-21-26.6Z" fill="#8C7FA5" opacity=".6"/>',
        # face
        f'<path d="{FACE}" fill="{skin}"/>',
        # soft modelling (blurred): sockets, temples, cheek hollows, nose side, jaw, under-lip
        '<g filter="url(#mvSoft2)">'
        '<ellipse cx="-7.6" cy="-28.2" rx="6.8" ry="4.4" fill="#3E3252" opacity=".6"/>'
        '<ellipse cx="7.6" cy="-28.2" rx="6.8" ry="4.4" fill="#2A2139" opacity=".75"/>'
        '<ellipse cx="-7.2" cy="-24.2" rx="4.6" ry="1.6" fill="#4D3F66" opacity=".35"/>'
        '<ellipse cx="7.2" cy="-24.2" rx="4.6" ry="1.6" fill="#3B2F52" opacity=".45"/>'
        '<path d="M9-23.5C12.8-22 15.8-19.5 16.8-16C14.8-12.6 12.6-10.4 10.4-9.6C11-14 10.6-19 9-23.5Z" fill="#3E3252" opacity=".8"/>'
        '<path d="M-9-23.5C-12.8-22-15.8-19.5-16.8-16C-14.8-12.6-12.6-10.4-10.4-9.6C-11-14-10.6-19-9-23.5Z" fill="#6E6188" opacity=".42"/>'
        '<path d="M12-46C15.5-40 17.4-33 17.6-26C17.2-20 16.4-16 15-12.5L17.2-17.6C17.9-22 18.6-26.5 18.9-31C19.2-37 18.6-43 16.8-47.5Z" fill="#2E2440" opacity=".8"/>'
        '<path d="M-16.4-44C-18.2-40-18.6-36-18.4-33L-17-35C-16.8-38-16.4-41-15.6-43.6Z" fill="#54476C" opacity=".35"/>'
        '<path d="M1.1-31L2.9-17.2C3.2-15.6 2.3-14.3.8-14.2L.4-17.8Z" fill="#3E3252" opacity=".75"/>'
        '<ellipse cx="0" cy="-13.4" rx="3.6" ry="1.1" fill="#2E2440" opacity=".6"/>'
        '<path d="M-15.2-11.8C-12.8-7.2-9.4-3-6.6-1C-5 .1-2.6 .6 0 .6C2.6 .6 5 .1 6.6-1C9.4-3 12.8-7.2 15.2-11.8C13-6.4 8.4-.6 0 1.8C-8.4-.6-13-6.4-15.2-11.8Z" fill="#2E2440" opacity=".7"/>'
        '<ellipse cx="0" cy="-4.4" rx="3.8" ry="1.4" fill="#4D3F66" opacity=".45"/>'
        '</g>',
        # moonlight highlights: forehead, cheekbone ridge, nose bridge, lip, chin
        '<g filter="url(#mvSoft)" fill="#F7F4FC">'
        '<ellipse cx="-5" cy="-45.4" rx="8.8" ry="4.2" opacity=".32"/>'
        '<path d="M-15.6-27.6C-13.4-25.2-11-24.6-8.6-24.8C-11-23.6-13.6-23.8-16-25.4Z" opacity=".38"/>'
        '<ellipse cx="-1.6" cy="-2.8" rx="3" ry="1.3" opacity=".26"/>'
        '<ellipse cx="-1.4" cy="-7.2" rx="1.8" ry=".7" opacity=".3"/>'
        '</g>',
        '<path d="M-.5-30.5L-.9-18.4" stroke="#F7F4FC" stroke-width=".85" stroke-linecap="round" opacity=".5"/>',
        # nostrils
        '<path d="M-3.4-13.9Q-2.2-12.7-.9-13.3M3.4-13.9Q2.2-12.7.9-13.3" stroke="#2E2440" stroke-width=".75" fill="none" stroke-linecap="round"/>',
    ]
    # brows — straight, slightly raised outer ends: calm & mysterious
    lift = -.6 if expr == "intense" else 0
    for s in (-1, 1):
        o.append(f'<path d="M{n(s * 2.8)} {n(-31.4 - lift)}C{n(s * 6)} {n(-32.6 - lift * .5)} {n(s * 9.6)} -33.8 {n(s * 13.2)} -33.4'
                 f'L{n(s * 13)} -32.5C{n(s * 9.4)} -32.6 {n(s * 6)} {n(-31.4 - lift * .5)} {n(s * 3)} {n(-30.2 - lift)}Z" fill="#0E0914"/>')
    # eyes — almond, upper lid low (mysterious); violet irises
    iris = radial(doc, "mvIris", [(0, "#F1ECFF"), (.35, P.ice), (.7, P.glow), (1, P.primary)])
    for s in (-1, 1):
        cx = s * 7.6
        almond = (f"M{n(cx - s * 4.4)} -27.4C{n(cx - s * 2.2)} -29.4 {n(cx + s * 2.2)} -29.7 {n(cx + s * 4.6)} -28.3"
                  f"C{n(cx + s * 2.4)} -26.2 {n(cx - s * 1.8)} -25.6 {n(cx - s * 4.4)} -27.4Z")
        o.append(f'<path d="{almond}" fill="#150E1D"/>')
        if eyes:
            o.append(f'<circle cx="{n(cx + s * .2)}" cy="-27.6" r="1.75" fill="{iris}"/>'
                     f'<circle cx="{n(cx + s * .2)}" cy="-27.6" r=".55" fill="#120C1A"/>'
                     f'<circle cx="{n(cx - .5)}" cy="-28.2" r=".35" fill="#FFFFFF" opacity=".9"/>')
        o.append(f'<path d="M{n(cx - s * 4.6)} -27.3C{n(cx - s * 2.2)} -29.6 {n(cx + s * 2.4)} -29.9 {n(cx + s * 4.8)} -28.2" '
                 f'stroke="#09060D" stroke-width="1.35" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{n(cx - s * 3.4)} -25.9Q{n(cx)} -25.1 {n(cx + s * 3.6)} -26.4" stroke="#54476C" stroke-width=".45" fill="none"/>')
    # mouth — thin dusky lips; smirk lifts his left corner; fangs show just below the upper lip
    corner = -9.4 if expr in ("smirk", "fangs") else -8.7
    o.append(f'<path d="M-5.6-8.6C-3.2-9.7-1-9.3 0-9C1-9.3 3.2-9.8 5.8 {n(corner)}C3.2-8.3 1-8.2 0-8.1C-1-8.2-3.2-8.2-5.6-8.6Z" fill="#43334F"/>'
             '<path d="M-4.6-8C-2.6-5.9 2.6-5.9 4.8-8C2.6-7.2-2.6-7.2-4.6-8Z" fill="#6E5E84"/>'
             f'<path d="M-5.6-8.6C-3-8.1 3-8.1 5.8 {n(corner)}" stroke="#1E1528" stroke-width=".75" fill="none" stroke-linecap="round"/>')
    if expr == "fangs":
        o.append('<path d="M-3.1-8.3L-2.4-6.4L-1.8-8.2Z M3.1-8.3L2.4-6.4L1.8-8.2Z" fill="#F5F3FF"/>')
    # hair: shadow cast on the forehead, the dark mass, messy silhouette flicks, sheen, flow lines, loose strands
    o.append('<path d="M-17-38.6C-14-47-6-50.6 2-50.4C9-50.2 14.6-46.6 17.2-38.6C13-44.6 7-47 0-47C-7-47-13.6-44.6-17-38.6Z" '
             'fill="#1E1728" opacity=".8" filter="url(#mvSoft)"/>')
    o.append("".join(f'<path d="{_lock(*lk)}" fill="#050407"/>' for lk in FLICKS))
    o.append(f'<path d="{HAIR_BASE}" fill="{hairG}"/>')
    o.append(f'<path d="M-16-50C-12-60-2-64.6 8-63.6" stroke="{sheen}" stroke-width="4.2" fill="none" stroke-linecap="round" filter="url(#mvSoft)"/>')
    o.append("".join(f'<path d="M{n(x0)} {n(y0)}Q{n((x0 + x1) / 2)} {n((y0 + y1) / 2 - b)} {n(x1)} {n(y1)}" stroke="{"#43365C" if i % 2 else "#2A2139"}" '
                     f'stroke-width="{n(.45 + i % 3 * .22, 2)}" fill="none" stroke-linecap="round" opacity=".9"/>'
                     for i, (x0, y0, x1, y1, b) in enumerate(FLOW)))
    o.append("".join(f'<path d="{_lock(*lk)}" fill="#07060B"/>' for lk in STRANDS))
    o.append("".join(f'<path d="M{n(x0)} {n(y0)}Q{n((x0 + x1) / 2 + b * .6)} {n((y0 + y1) / 2)} {n(x0 + (x1 - x0) * .75)} {n(y0 + (y1 - y0) * .75)}" '
                     f'stroke="#4A3D63" stroke-width=".45" fill="none" stroke-linecap="round"/>' for x0, y0, x1, y1, b, _ in STRANDS[:4]))
    if eyes:
        eg = radial(doc, "mvEyeG", [(0, "#EFEAFF", .9), (.3, P.glow, .75), (1, P.glow, 0)])
        o.append(f'<g style="animation:mvEye 4.2s ease-in-out infinite" opacity="{n(min(1, .8 * glow), 2)}">'
                 + "".join(f'<circle cx="{n(s * 7.8)}" cy="-27.6" r="{n(3.3 * glow)}" fill="{eg}"/>' for s in (-1, 1)) + "</g>")
    return "".join(o)


# ── hands (wrist at 0,0; fingers toward +y) ────────────────────────────────────

def hand(kind: str, s: int = 1, ring: bool = False) -> str:
    skin = "#CFC7DD"
    shade = "#8C7FA5"
    fing = lambda pts, w=2.5, c=skin: (f'<path d="M{pts[0][0]} {pts[0][1]}' + "".join(f"L{x} {y}" for x, y in pts[1:])
                                       + f'" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')
    palm_ = f'<path d="M-5 0L5 0L6 11L-5.6 11.4Z" fill="{skin}"/><path d="M1.5 0L5 0L6 11L2.6 11.3Z" fill="{shade}" opacity=".45"/>'
    if kind == "open":
        body = (palm_ + fing([(-4.4, 10.6), (-6.6, 17.6), (-7.6, 22.6)], 2.3) + fing([(-1.6, 11.2), (-2.4, 19), (-2.6, 25)], 2.3)
                + fing([(1.4, 11.2), (2, 18.6), (2.4, 24)], 2.3, "#B6ACC8") + fing([(4.2, 10.6), (5.8, 16.6), (6.6, 20.6)], 2.1, "#A89CBD")
                + fing([(5, 3.4), (8.6, 7.8), (10.4, 11.8)], 2.5))
    elif kind == "cast":       # fingers softly curled, energy between them
        body = (palm_ + fing([(-4.4, 10.6), (-6.8, 16), (-6, 20.4)], 2.3) + fing([(-1.6, 11.2), (-2.4, 17.6), (-1.2, 22.2)], 2.3)
                + fing([(1.4, 11.2), (2.4, 17.2), (3.8, 21)], 2.3, "#B6ACC8") + fing([(4.2, 10.6), (6.2, 15), (7.4, 18)], 2.1, "#A89CBD")
                + fing([(5, 3.4), (9, 7), (10.2, 10.6)], 2.5))
    elif kind == "point":
        body = (f'<path d="M-5.2 0L5.2 0Q7 6 6.4 11.6Q4 15 0 15Q-4 15-6.4 11.6Q-7 6-5.2 0Z" fill="{skin}"/>'
                f'<path d="M1 0L5.2 0Q7 6 6.4 11.6Q4 15 1.6 15Z" fill="{shade}" opacity=".45"/>'
                + fing([(-3.4, 13), (-3.8, 21), (-4, 27)], 2.3))
    elif kind == "hold":
        body = (f'<path d="M-5.4 0L5.4 0Q7.6 6 7 12L2.6 15.6L-2.6 15.6L-7 12Q-7.6 6-5.4 0Z" fill="{skin}"/>'
                f'<path d="M1.4 0L5.4 0Q7.6 6 7 12L2.6 15.6Z" fill="{shade}" opacity=".45"/>')
    else:                      # relaxed
        body = (f'<path d="M-5 0C-6 5-6.6 11-5.6 16.4C-4.6 21.6-2 24.6.6 24.6C3.2 24.6 5.2 21.4 5.6 16.4C6 11 6 5 5 0Z" fill="{skin}"/>'
                f'<path d="M1.6 0C3 6 3.4 12 3 18C2.6 21.6 1.8 23.8.6 24.6C3.2 24.6 5.2 21.4 5.6 16.4C6 11 6 5 5 0Z" fill="{shade}" opacity=".45"/>'
                f'<path d="M4.6 3.4C7.8 6.4 8.4 10.4 7 13.4C6 12.2 5.4 9.4 4.2 7.4Z" fill="{skin}"/>'
                '<path d="M-1.6 14V23M1.6 14.4V23.2" stroke="#8C7FA5" stroke-width=".5" opacity=".7"/>')
    sh = f'<path d="M-5 0L5 0L5.6 4L-5.4 4.2Z" fill="{shade}" opacity=".55"/>'
    rg = f'<rect x="-3" y="13.6" width="2.6" height="1.5" rx=".5" fill="{P.silver}"/>' if ring else ""
    return f'<g transform="scale({s} 1)">{body}{sh}{rg}</g>'


# ── limbs ──────────────────────────────────────────────────────────────────────

def _seg(length: float, w0: float, w1: float, fill: str, bulge: float = 0) -> str:
    """Tapered limb segment hanging from its joint; bulge swells the outline (fabric volume)."""
    b = bulge
    return (f'<path d="M{n(-w0 / 2)} 0C{n(-w0 / 2 - b)} {n(length * .35)} {n(-w1 / 2 - b * .6)} {n(length * .7)} {n(-w1 / 2)} {n(length)}'
            f'Q0 {n(length + w1 * .4)} {n(w1 / 2)} {n(length)}C{n(w1 / 2 + b * .6)} {n(length * .7)} {n(w0 / 2 + b)} {n(length * .35)} {n(w0 / 2)} 0Z" fill="{fill}"/>'
            f'<circle r="{n(w0 / 2)}" fill="{fill}"/>')


def arm(doc: Doc, s: int, sh: float, el: float, wr: float = 0, hk: str = "relaxed", prop: str = "", ring: bool = False) -> str:
    r1, r2, r3 = -s * sh, s * el, s * wr
    lit = s < 0                                     # screen-left arm faces the moon
    sleeve = linear(doc, "mvSleeveL" if lit else "mvSleeveR",
                    [(0, "#2A2238"), (.28, "#130F1B"), (.7, "#08070C"), (1, "#040306")] if lit else
                    [(0, "#16121E"), (.4, "#09080D"), (1, "#030204")], 0, 0, 1, 0)
    cuff = (f'<path d="M-8.4 {n(FORE - 10)}L8.4 {n(FORE - 10)}L9.4 {n(FORE + 1)}L-9.4 {n(FORE + 1)}Z" fill="#060509"/>'
            f'<path d="M-8.6 {n(FORE - 10)}L8.6 {n(FORE - 10)}" stroke="{P.silver}" stroke-width=".75" opacity=".85"/>'
            f'<path d="M-7.4 {n(FORE + .8)}L7.4 {n(FORE + .8)}" stroke="#A89CBD" stroke-width="1.8" opacity=".75"/>')
    folds = (f'<path d="M-3 {n(UPPER * .22)}Q1.4 {n(UPPER * .5)} -1.6 {n(UPPER * .82)}" stroke="#2E2540" stroke-width="1.4" fill="none" '
             f'opacity=".75" filter="url(#mvSoft)"/>'
             f'<path d="M-5.6 {n(UPPER - 6)}Q0 {n(UPPER + 1)} 5.6 {n(UPPER - 5)}" stroke="#241C31" stroke-width="1.2" fill="none" opacity=".8"/>')
    ffold = f'<path d="M2.4 {n(FORE * .15)}Q-1.4 {n(FORE * .45)} 1.2 {n(FORE * .72)}" stroke="#221B2E" stroke-width="1.1" fill="none" opacity=".8" filter="url(#mvSoft)"/>'
    return (f'<g transform="translate({n(s * SHOULDER[0])} {n(SHOULDER[1])}) rotate({n(r1)})">'
            + _seg(UPPER, 19.5, 15.6, sleeve, 1.2) + folds +
            f'<g transform="translate(0 {n(UPPER)}) rotate({n(r2)})">' + _seg(FORE, 15.6, 13, sleeve, .7) + ffold + cuff +
            f'<g transform="translate(0 {n(FORE + 1)}) rotate({n(r3)})">{hand(hk, -s, ring)}{prop}</g></g></g>')


def leg(doc: Doc, s: int, hip: float, knee: float) -> str:
    r1, r2 = -s * hip, s * knee
    tr = linear(doc, "mvTrL" if s < 0 else "mvTrR", [(0, "#1C1726"), (.4, "#0B0910"), (1, "#050407")] if s < 0 else
                [(0, "#0E0B14"), (1, "#040306")], 0, 0, 1, 0)
    boot = linear(doc, "mvBoot", [(0, "#2A2436"), (.25, "#0B0910"), (1, "#030204")], 0, 0, 1, 0)
    shaft = (f'<path d="M-9.2 {n(SHIN * .42)}L9.2 {n(SHIN * .42)}L8.6 {n(SHIN)}L-8.6 {n(SHIN)}Z" fill="{boot}"/>'
             f'<path d="M-9 {n(SHIN * .42)}L9 {n(SHIN * .42)}" stroke="#2E2540" stroke-width="1.2"/>'
             f'<path d="M-5.6 {n(SHIN * .5)}L-6.2 {n(SHIN * .95)}" stroke="#6E6188" stroke-width=".9" opacity=".45" stroke-linecap="round"/>')
    foot = (f'<path d="M-8.6 -2L8.6 -2L9.2 12Q{n(8 + 4 * s)} 20 {n(3 + 6 * s)} 21L{n(-6 + 2 * s)} 21Q-9.8 20-9.4 12Z" fill="{boot}"/>'
            f'<path d="M{n(-4 + 5 * s)} 16.6Q{n(1 + 5 * s)} 19 {n(6 + 5 * s)} 17" stroke="#3B3149" stroke-width="1" fill="none"/>'
            f'<rect x="-5.2" y="3" width="10.4" height="2.2" rx=".8" fill="{P.silver}" opacity=".8"/>')
    crease = f'<path d="M{s * 2} 10L{s * 3} {n(THIGH - 8)}" stroke="#231C2E" stroke-width="1.2" opacity=".8"/>'
    return (f'<g transform="translate({n(s * HIP[0])} {n(HIP[1])}) rotate({n(r1)})">' + _seg(THIGH, 25, 19, tr, .6) + crease +
            f'<g transform="translate(0 {n(THIGH)}) rotate({n(r2)})">' + _seg(SHIN, 19, 15, tr) + shaft +
            f'<g transform="translate(0 {n(SHIN)}) rotate({n(-r1 - r2)})">{foot}</g></g></g>')


def foot_y(hip: float, knee: float, s: int) -> float:
    a1 = math.radians(-s * hip)
    a2 = math.radians(-s * hip + s * knee)
    return HIP[1] + THIGH * math.cos(a1) + SHIN * math.cos(a2) + 21


# ── costume ────────────────────────────────────────────────────────────────────

def coat_back(doc: Doc, flare: float, wind: float) -> str:
    """Back skirt + violet satin lining, seen between the open front panels."""
    hx = 62 + flare
    lining = linear(doc, "mvLining", [(0, "#241137"), (.45, "#12091C"), (1, "#050309")], 0, 0, 0, 1)
    sheen = linear(doc, "mvLinSheen", [(0, "#6D28D9", 0), (.5, "#6D28D9", .22), (1, "#6D28D9", 0)], 0, 0, 1, 0)
    back = (f"M-32-302L32-302Q{n(42 + flare * .4)}-180 {n(hx + wind)}-60L{n(hx * .45 + wind)}-54L{n(wind * .7)}-70"
            f"L{n(-hx * .45 + wind)}-54L{n(-hx + wind)}-60Q{n(-42 - flare * .4)}-180-32-302Z")
    return (f'<path d="{back}" fill="#040306"/>'
            f'<path d="M-20-290L20-290L{n(26 + flare * .3 + wind * .6)}-68L{n(-26 - flare * .3 + wind * .6)}-68Z" fill="{lining}"/>'
            f'<path d="M-12-286L12-286L{n(16 + wind * .6)}-70L{n(-16 + wind * .6)}-70Z" fill="{sheen}"/>'
            f'<path d="M{n(wind * .7)}-72L{n(wind * .4)}-200" stroke="#120E19" stroke-width="1.4"/>')


def torso(doc: Doc) -> str:
    vest = linear(doc, "mvVest", [(0, "#1B1524"), (.5, "#0C0A11"), (1, "#060509")], 0, 0, 1, 0)
    silk = linear(doc, "mvSilk", [(0, "#3B1C66"), (.45, "#1E0F33"), (1, "#07040C")], 0, 0, 1, 1)
    gem = radial(doc, "mvGem", [(0, "#EFEAFF"), (.25, P.ice), (.6, P.primary), (1, "#2A0E5C")], .4, .35, .7)
    gl = radial(doc, "mvGemGl", [(0, P.glow, .8), (1, P.glow, 0)])
    doc.defs("mvBrocade", '<pattern id="mvBrocade" width="6" height="6" patternUnits="userSpaceOnUse">'
                          '<path d="M3 .6L5.4 3L3 5.4L.6 3Z" fill="none" stroke="#1E1829" stroke-width=".45"/></pattern>')
    o = [
        # neck base + shirt
        '<path d="M-9-414L9-414L10.5-397L-10.5-397Z" fill="#6E6188"/>',
        '<path d="M-10.5-400L10.5-400L14-392L-14-392Z" fill="#2A2336"/>',
        # waistcoat with a faint brocade
        f'<path d="M-14.5-394L14.5-394L20.5-296L7-289L0-294L-7-289L-20.5-296Z" fill="{vest}"/>',
        '<path d="M-14.5-394L14.5-394L20.5-296L7-289L0-294L-7-289L-20.5-296Z" fill="url(#mvBrocade)" opacity=".9"/>',
        '<path d="M0-376V-294" stroke="#05040A" stroke-width="1"/>',
        "".join(f'<circle cx="1.8" cy="{y}" r="1.3" fill="{P.silver}"/><circle cx="1.4" cy="{y - .4}" r=".45" fill="#FFFFFF" opacity=".8"/>'
                for y in (-368, -352, -336, -320, -304)),
        # watch chain
        f'<path d="M2.6-336Q10-326 17-330" stroke="{P.silver}" stroke-width=".8" stroke-dasharray="1.4 .9" fill="none"/>',
        # cravat (violet silk) with the gem
        f'<path d="M-8.8-400Q0-396 8.8-400L7.6-388Q10.2-378 7.4-366L0-360L-7.4-366Q-10.2-378-7.6-388Z" fill="{silk}"/>',
        '<path d="M-3-386Q0-372-1.4-364M3.2-386Q1.6-374 3.2-366" stroke="#4C2A80" stroke-width=".7" fill="none" opacity=".8"/>',
        '<path d="M-6-384Q-4-374-5.4-367" stroke="#8E80B0" stroke-width=".9" fill="none" opacity=".35" filter="url(#mvSoft)"/>',
        f'<circle cx="0" cy="-391" r="10" fill="{gl}" style="animation:mvGem 3.6s ease-in-out infinite"/>',
        f'<ellipse cx="0" cy="-391" rx="4.6" ry="5.6" fill="{P.silver}"/>',
        '<ellipse cx="0" cy="-391" rx="4.6" ry="5.6" fill="none" stroke="#6E6188" stroke-width=".5"/>',
        f'<path d="M0-395.8L3.4-393L3.4-389L0-386.2L-3.4-389L-3.4-393Z" fill="{gem}"/>',
        '<path d="M0-395.8L0-386.2M-3.4-393L3.4-389M3.4-393L-3.4-389" stroke="#EFEAFF" stroke-width=".3" opacity=".6"/>',
    ]
    return "".join(o)


def coat_front(doc: Doc, flare: float, wind: float) -> str:
    hx = 60 + flare
    open_ = 6 + flare * .35
    lit = linear(doc, "mvCoatL", [(0, "#2B2338"), (.22, "#15111C"), (.6, "#0A0810"), (1, "#060509")], 0, 0, 1, 0)
    shd = linear(doc, "mvCoatR", [(0, "#0B0910"), (.6, "#060509"), (1, "#020203")], 0, 0, 1, 0)
    lapel = linear(doc, "mvLapel", [(0, "#352B45"), (.5, "#15101E"), (1, "#07060B")], 0, 0, 1, 1)
    lin = linear(doc, "mvLinEdge", [(0, "#4C2A80"), (1, "#1E0F33")], 0, 0, 0, 1)
    o = []
    for s in (-1, 1):
        fill = lit if s < 0 else shd
        w = wind
        panel = (f"M{s * 10}-398L{s * 30}-395Q{s * 44}-392 {s * 47}-385L{s * 46}-370L{s * 44}-352L{s * 36}-318L{s * 33}-298"
                 f"L{s * 37}-264Q{n(s * (46 + flare * .4) + w * .4)}-170 {n(s * hx + w)}-66"
                 f"Q{n(s * (hx * .66) + w * .9)}-57 {n(s * (19 + open_) + w * .5)}-63"
                 f"L{n(s * (7 + open_ * .3))}-250L{s * 2}-296L{s * 9}-338L{s * 10}-398Z")
        o.append(f'<path d="{panel}" fill="{fill}"/>')
        # satin lining turned out along the open skirt edge
        o.append(f'<path d="M{n(s * (7 + open_ * .3))}-250L{n(s * (19 + open_) + w * .5)}-63L{n(s * (15 + open_) + w * .5)}-64'
                 f'L{n(s * (5 + open_ * .3))}-252Z" fill="{lin}" opacity=".85"/>')
        # folds: soft shadowed troughs + moonlit ridges on the lit panel
        for fx, op in ((.3, .9), (.55, .75), (.8, .6)):
            bx = s * (24 + (hx - 24) * fx) + w * fx
            path = f"M{n(s * (22 + 9 * fx))}-282Q{n(s * (29 + 12 * fx) + w * .3)}-170 {n(bx)}-70"
            o.append(f'<path d="{path}" stroke="#030204" stroke-width="3.2" fill="none" opacity="{op * .7:.2f}" filter="url(#mvSoft2)"/>')
            if s < 0:
                o.append(f'<path d="{path}" transform="translate(-3 0)" stroke="#3A3050" stroke-width="1.4" fill="none" opacity="{op * .45:.2f}" filter="url(#mvSoft)"/>')
        # satin peaked lapel
        o.append(f'<path d="M{s * 10}-398L{s * 31}-378L{s * 26.5}-371.5L{s * 23}-356L{s * 9.5}-337L{s * 10.5}-360Z" fill="{lapel}"/>'
                 f'<path d="M{s * 31}-378L{s * 26.5}-371.5L{s * 23}-356L{s * 9.5}-337" stroke="#4A3D63" stroke-width=".7" fill="none" opacity=".9"/>')
        # waist button + pocket flap
        o.append(f'<circle cx="{n(s * 4.6)}" cy="-299" r="1.6" fill="{P.silver}"/><circle cx="{n(s * 4.2)}" cy="-299.5" r=".5" fill="#FFFFFF" opacity=".8"/>'
                 f'<path d="M{s * 22}-252L{s * 38}-254L{s * 38.5}-248L{s * 22.5}-246Z" fill="#020203" opacity=".9"/>')
    # ambient occlusion under the collar and at the waist seam
    o.append('<path d="M-30-394Q0-386 30-394L28-384Q0-378-28-384Z" fill="#000" opacity=".35" filter="url(#mvSoft2)"/>')
    o.append(f'<path d="M-19.5-354Q0-338 19.5-354" stroke="{P.silver}" stroke-width=".8" stroke-dasharray="1.6 1" fill="none"/>')
    return "".join(o)


def collar(doc: Doc, spread: float = 0) -> str:
    """Tall standing collar: rises beside the jaw, flares slightly, satin inner face catching the moon."""
    satin = linear(doc, "mvCollar", [(0, "#3A2E4E"), (.45, "#15101E"), (1, "#060509")], 0, 0, 0, 1)
    satinR = linear(doc, "mvCollarR", [(0, "#1E1829"), (.5, "#0C0A11"), (1, "#040306")], 0, 0, 0, 1)
    o = ['<path d="M-17-426Q0-431 17-426L15-398L-15-398Z" fill="#050407"/>']
    for s in (-1, 1):
        top = s * (31 + spread)
        o.append(f'<path d="M{s * 12}-398L{s * 16}-428L{n(top)}-425L{s * 38}-395Z" fill="#07060A"/>'
                 f'<path d="M{s * 13.6}-399L{s * 17}-425.4L{n(top - s * 2.6)}-422L{s * 33.5}-397Z" fill="{satin if s < 0 else satinR}"/>'
                 f'<path d="M{s * 16}-428L{n(top)}-425" stroke="{P.glow}" stroke-width=".7" opacity="{.7 if s < 0 else .35}"/>'
                 f'<path d="M{s * 17.5}-423L{n(top - s * 3)}-420" stroke="#8E80B0" stroke-width=".5" opacity="{.35 if s < 0 else .12}"/>')
    return "".join(o)


# ── poses ──────────────────────────────────────────────────────────────────────
# arm: (shoulder swing, elbow bend, wrist, hand); leg: (hip, knee)
POSES = {
    "stand":      dict(arms=((6, 8, 0, "relaxed"), (6, 8, 0, "relaxed")), legs=((3, 0), (3, 0))),
    "hero":       dict(arms=((6, 10, 0, "relaxed"), (20, -130, -10, "open")), legs=((5, 0), (4, 0)), flare=8, wind=6, expr="smirk"),
    "shadow":     dict(arms=((6, 8, 0, "relaxed"), (40, 12, 8, "cast")), legs=((5, 0), (5, 0)), flare=4, wind=-4, tilt=-3, glow=1.2),
    "holo":       dict(arms=((30, -110, 0, "open"), (30, -110, 0, "open")), legs=((5, 0), (5, 0)), flare=3, glow=1.2),
    "portal":     dict(arms=((6, 10, 0, "relaxed"), (84, -4, 0, "open")), legs=((7, -2), (7, -2)), flare=10, wind=-8, expr="smirk", tilt=-2),
    "sorcerer":   dict(arms=((40, -70, 0, "cast"), (40, -70, 0, "cast")), legs=((8, -2), (8, -2)), flare=12, expr="intense", glow=1.4),
    "commander":  dict(arms=((6, 10, 0, "relaxed"), (62, -8, 0, "point")), legs=((6, 0), (6, 0)), flare=5, wind=4, tilt=3),
    "timekeeper": dict(arms=((6, 8, 0, "relaxed"), (20, -130, -6, "open")), legs=((5, 0), (4, 0)), flare=4, tilt=-2),
    "scholar":    dict(arms=((15, 150, 0, "hold"), (15, 150, 0, "hold")), legs=((4, 0), (4, 0)), flare=2, tilt=5),
    "guardian":   dict(arms=((4, 70, 0, "relaxed"), (4, 70, 0, "relaxed")), legs=((7, 0), (7, 0)), flare=8, wind=10,
                       behind=(True, True)),
    "walk":       dict(arms=((10, 12, 0, "relaxed"), (-4, 6, 0, "relaxed")), legs=((10, -18), (-2, 6)), flare=16, wind=-18),
    "awaken":     dict(arms=((24, -10, 0, "open"), (24, -10, 0, "open")), legs=((9, 0), (9, 0)), flare=18, expr="fangs", glow=1.6, tilt=-4),
    "coder":      dict(arms=((26, 84, -6, "open"), (26, 84, -6, "open")), legs=((3, 0), (3, 0)), tilt=6),
    "final":      dict(arms=((5, 6, 0, "relaxed"), (5, 6, 0, "relaxed")), legs=((6, 0), (6, 0)), flare=10, wind=6, expr="smirk"),
}


def pose(name: str) -> dict:
    p = dict(flare=0, wind=0, tilt=0, lean=0, expr="calm", glow=1.0, behind=(False, False))
    p.update(POSES[name])
    return p


def head_ref(doc: Doc, expr: str = "calm", glow: float = 1.0, eyes: bool = True) -> str:
    """The head is the most detailed part, so each variant is drawn once per SVG (in <defs>)
    and every figure in that SVG reuses it with <use>."""
    hid = f"mvH{expr[:3]}{round(glow * 10)}{'' if eyes else 'x'}"
    if hid not in doc._defs:
        doc.defs(hid, f'<g id="{hid}">{head(doc, expr, glow, eyes)}</g>')
    return f'<use href="#{hid}"/>'


def symbol(doc: Doc, name: str, rim: bool = False) -> str:
    """A whole posed figure stored once in <defs> — for clones, echoes and repeats."""
    fid = f"mvF{name}{'r' if rim else ''}"
    if fid not in doc._defs:
        doc.defs(fid, f'<g id="{fid}">{figure(doc, name, rim=rim)}</g>')
    return f'<use href="#{fid}"/>'


def figure(doc: Doc, name: str, props: dict | None = None, rim: bool = True, silhouette: bool = False) -> str:
    """The full vampire, feet at (0,0). props: back / front / hand_L / hand_R (SVG snippets)."""
    _defs(doc)
    p, props = pose(name), props or {}
    (aL, aR), (lL, lR) = p["arms"], p["legs"]
    arms = [arm(doc, -1, *aL, prop=props.get("hand_L", ""), ring=True), arm(doc, 1, *aR, prop=props.get("hand_R", ""))]
    body = [coat_back(doc, p["flare"], p["wind"]), leg(doc, -1, *lL), leg(doc, 1, *lR),
            f'<g transform="rotate({n(p["lean"])} 0 -262)">',
            arms[0] if p["behind"][0] else "", arms[1] if p["behind"][1] else "",
            torso(doc), coat_front(doc, p["flare"], p["wind"]), collar(doc),
            f'<g transform="translate(0 {CHIN_Y}) rotate({n(p["tilt"])} 0 {NECK_PIVOT - CHIN_Y})">'
            f'{head_ref(doc, p["expr"], p["glow"], eyes=not silhouette)}</g>',
            "" if p["behind"][0] else arms[0], "" if p["behind"][1] else arms[1], "</g>"]
    drop = max(foot_y(*lL, -1), foot_y(*lR, 1))
    inner = "".join(body)
    if silhouette:
        inner = f'<g filter="url(#mvShade)">{inner}</g>'
        doc.defs("mvShade", '<filter id="mvShade" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" '
                            'values="0 0 0 0 .02  0 0 0 0 .016  0 0 0 0 .03  0 0 0 1 0"/></filter>')
    f = f' filter="{rim_filter(doc)}"' if rim else ""
    out = props.get("back", "") + f'<g{f}>{inner}</g>' + props.get("front", "")
    if silhouette:
        out += silhouette_marks(doc, name)
    return f'<g transform="translate(0 {n(-drop)})">{out}</g>' if abs(drop) > .5 else out


def silhouette_marks(doc: Doc, name: str) -> str:
    """For the black silhouette: only the violet eyes and the gemstone stay lit."""
    p = pose(name)
    eg = radial(doc, "mvSilEye", [(0, "#F1ECFF"), (.35, P.glow, .9), (1, P.glow, 0)])
    gl = radial(doc, "mvSilGem", [(0, P.ice), (.4, P.primary, .8), (1, P.primary, 0)])
    t = math.radians(p["tilt"])
    pts = []
    for s in (-1, 1):
        x, y = s * 7.7, -27.6
        pts.append((x * math.cos(t) - (y - (NECK_PIVOT - CHIN_Y)) * math.sin(t),
                    CHIN_Y + (NECK_PIVOT - CHIN_Y) + x * math.sin(t) + (y - (NECK_PIVOT - CHIN_Y)) * math.cos(t)))
    eyes = "".join(f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="4.4" ry="1.9" fill="{eg}"/>' for x, y in pts)
    return (f'<g style="animation:mvEye 4.2s ease-in-out infinite">{eyes}</g>'
            f'<circle cx="0" cy="-391" r="6" fill="{gl}" style="animation:mvGem 3.6s ease-in-out infinite"/>')


def wrist(name: str, side: int) -> tuple[float, float]:
    """World position (feet at 0,0) of a wrist, for placing props / effects."""
    p = pose(name)
    (aL, aR), (lL, lR) = p["arms"], p["legs"]
    sh, el = (aL if side < 0 else aR)[:2]
    r1, t = math.radians(-side * sh), math.radians(-side * sh + side * el)
    ex = side * SHOULDER[0] - UPPER * math.sin(r1)
    ey = SHOULDER[1] + UPPER * math.cos(r1)
    wx, wy = ex - (FORE + 1) * math.sin(t), ey + (FORE + 1) * math.cos(t)
    drop = max(foot_y(*lL, -1), foot_y(*lR, 1))
    return wx, wy - drop


def palm(name: str, side: int, reach: float = 14) -> tuple[float, float]:
    """A point just beyond the hand (where energy gathers)."""
    p = pose(name)
    (aL, aR) = p["arms"]
    sh, el, wr = (aL if side < 0 else aR)[:3]
    ang = math.radians(-side * sh + side * el + side * wr)
    wx, wy = wrist(name, side)
    return wx - reach * math.sin(ang), wy + reach * math.cos(ang)


def smoke(doc: Doc, w: float = 180, y: float = 0, seed: int = 3, count: int = 7, key: str = "mvSmoke") -> str:
    """Black-violet smoke pooling at his feet."""
    rnd = random.Random(seed)
    g = radial(doc, key + "G", [(0, "#050309", .92), (.55, "#12091C", .55), (1, "#1A0D26", 0)])
    doc.keyframes(key, "0%,100%{transform:translateX(-6px) scaleX(1)}50%{transform:translateX(6px) scaleX(1.06)}")
    blobs = "".join(f'<ellipse cx="{n(rnd.uniform(-w / 2, w / 2))}" cy="{n(y + rnd.uniform(-10, 4))}" rx="{n(rnd.uniform(40, 80))}" '
                    f'ry="{n(rnd.uniform(9, 18))}" fill="{g}"/>' for _ in range(count))
    return f'<g style="transform-box:fill-box;transform-origin:center;animation:{key} 9s ease-in-out infinite">{blobs}</g>'
