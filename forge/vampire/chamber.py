"""Chambers of the castle — shared interior backdrops + the vampire's power effects.

Every section is a different room of the same castle; tall gothic windows look out on
your castle painting, so the painting is the backdrop of the whole README.
"""
from __future__ import annotations

import math
import random

from . import elements as el
from .backdrop import image
from .core import Doc, linear, n, radial
from .palette import P

# painting crops (source-pixel boxes) seen through the windows
VIEW_MOON = ("port", (150, 120, 560, 700))          # the moon over the towers
VIEW_TOWERS = ("port", (420, 180, 1000, 1000))      # spires, lit windows, waterfall
VIEW_GATE = ("port", (180, 620, 860, 1290))         # the gate and the lantern path
VIEW_WIDE = ("land", (420, 60, 1500, 760))          # the whole castle
VIEW_MOONL = ("land", (330, 60, 720, 520))          # landscape moon + bats


def arch_path(x: float, y: float, w: float, h: float) -> str:
    """Pointed gothic arch: (x, y) top-left of the bounding box."""
    cx, sp = x + w / 2, h * .34
    return (f"M{n(x)} {n(y + h)}L{n(x)} {n(y + sp)}Q{n(x)} {n(y + sp * .25)} {n(cx)} {n(y)}"
            f"Q{n(x + w)} {n(y + sp * .25)} {n(x + w)} {n(y + sp)}L{n(x + w)} {n(y + h)}Z")


def window(doc: Doc, x: float, y: float, w: float, h: float, view=VIEW_MOON, key: str = "win", tracery: bool = True) -> str:
    """A tall gothic window with the castle painting outside, stone frame and tracery."""
    ap = arch_path(x, y, w, h)
    doc.defs(key + "C", f'<clipPath id="{key}C"><path d="{ap}"/></clipPath>')
    src, box = view
    pic = image(doc, src, x, y, w, h, box=box, px=1.3, key=key + "I", bright=.95)
    glass = linear(doc, key + "G", [(0, "#C4B5FD", .10), (.5, "#8B5CF6", .04), (1, "#020203", .35)], 0, 0, 0, 1)
    o = [f'<g clip-path="url(#{key}C)">{pic}<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{glass}"/>']
    if tracery:
        cx = x + w / 2
        o.append(f'<path d="M{n(x)} {n(y + h * .64)}H{n(x + w)}M{n(x)} {n(y + h * .66)}H{n(x + w)}" stroke="#030205" '
                 f'stroke-width="{n(max(2, w * .018))}"/>')
    o.append("</g>")
    o.append(f'<path d="{ap}" fill="none" stroke="#1E1230" stroke-width="{n(max(5, w * .07))}"/>'
             f'<path d="{ap}" fill="none" stroke="{P.glow}" stroke-width="1.2" opacity=".55"/>')
    return "".join(o)


def rays(doc: Doc, x: float, y: float, w: float, h: float, floor: float, spread: float = 1.6, key: str = "ray") -> str:
    """Moonlight spilling from a window onto the floor."""
    g = linear(doc, key, [(0, P.ice, .07), (.6, P.glow, .03), (1, P.glow, 0)], 0, 0, 0, 1)
    x0, x1 = x + w * .12, x + w * .88
    fx0, fx1 = x + w / 2 - w * spread, x + w / 2 + w * spread
    doc.keyframes(key + "K", "0%,100%{opacity:.7}50%{opacity:1}")
    return (f'<path d="M{n(x0)} {n(y + h * .5)}L{n(x1)} {n(y + h * .5)}L{n(fx1)} {n(floor)}L{n(fx0)} {n(floor)}Z" fill="{g}" '
            f'style="animation:{key}K 8s ease-in-out infinite"/>')


def stone(doc: Doc, W: float, H: float, key: str = "stone") -> str:
    """Dark stone courses — barely visible, just enough texture."""
    doc.defs(key, f'<pattern id="{key}" width="120" height="44" patternUnits="userSpaceOnUse">'
                  f'<path d="M0 .5H120M0 22.5H120M40 0V22M100 0V22M10 22V44M70 22V44" stroke="#1A0D26" stroke-width="1" opacity=".55"/></pattern>')
    return f'<rect width="{n(W)}" height="{n(H)}" fill="url(#{key})"/>'


def pillar(doc: Doc, x: float, top: float, bottom: float, w: float = 34) -> str:
    g = linear(doc, "chPil", [(0, "#150C20"), (.5, "#08050D"), (1, "#020203")], 0, 0, 1, 0)
    return (f'<rect x="{n(x - w / 2)}" y="{n(top)}" width="{n(w)}" height="{n(bottom - top)}" fill="{g}"/>'
            f'<rect x="{n(x - w / 2 - 5)}" y="{n(bottom - 14)}" width="{n(w + 10)}" height="14" fill="#0B0712"/>'
            f'<path d="M{n(x - w / 2)} {n(top)}V{n(bottom)}" stroke="{P.glow}" stroke-width=".8" opacity=".35"/>')


def floor(doc: Doc, W: float, y: float, H: float, key: str = "fl") -> str:
    g = linear(doc, key, [(0, "#12091C", .9), (1, "#020203")], 0, 0, 0, 1)
    return (f'<rect y="{n(y)}" width="{n(W)}" height="{n(H - y)}" fill="{g}"/>'
            f'<path d="M0 {n(y)}H{n(W)}" stroke="{P.glow}" stroke-width=".8" opacity=".3"/>')


def candle(doc: Doc, x: float, y: float, s: float = 1, delay: float = 0) -> str:
    """Iron candle stand with a violet flame (like the lanterns in the painting)."""
    fl = radial(doc, "chFlame", [(0, "#FFFFFF"), (.35, P.ice), (.75, P.glow, .8), (1, P.primary, 0)], .5, .7, .6)
    halo = radial(doc, "chHalo", [(0, P.glow, .45), (1, P.glow, 0)])
    doc.keyframes("chFlick", "0%,100%{transform:scale(1,1)}30%{transform:scale(.9,1.12)}60%{transform:scale(1.08,.94)}")
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(s, 2)})">'
            f'<circle cx="0" cy="-30" r="20" fill="{halo}"/>'
            '<path d="M-1.6-22H1.6V20H-1.6Z M-9 20H9L6 24H-6Z M-6-22H6L4-18H-4Z" fill="#0B0712"/>'
            '<rect x="-3" y="-30" width="6" height="8" rx="1" fill="#E2D8F8"/>'
            f'<path d="M0-44C3-38 4-35 2.6-31.6A2.8 2.8 0 0 1-2.6-31.6C-4-35-3-38 0-44Z" fill="{fl}" '
            f'style="transform-box:fill-box;transform-origin:bottom;animation:chFlick 1.8s ease-in-out {n(delay)}s infinite"/></g>')


def chamber(doc: Doc, W: float, H: float, key: str, windows=(), floor_y: float | None = None,
            pillars=(), candles=(), fog: bool = True, stars: bool = False) -> str:
    """A castle room: stone, gothic windows onto the painting, moonlight rays, pillars, violet candles, fog."""
    bg = linear(doc, key + "Bg", [(0, "#0B0712"), (.6, "#050507"), (1, "#020203")], 0, 0, 0, 1)
    o = [f'<rect width="{n(W)}" height="{n(H)}" fill="{bg}"/>', stone(doc, W, H, key + "St")]
    if stars:
        o.append(el.stars(doc, W, H * .6, 40, seed=len(key)))
    fy = floor_y or H - 60
    for i, (x, y, w, h, view) in enumerate(windows):
        o.append(rays(doc, x, y, w, h, fy, key=f"{key}R{i}"))
        o.append(window(doc, x, y, w, h, view, key=f"{key}W{i}"))
    o.append(floor(doc, W, fy, H, key + "F"))
    for x in pillars:
        o.append(pillar(doc, x, 0, fy + 6))
    for i, (x, y, s) in enumerate(candles):
        o.append(candle(doc, x, y, s, delay=i * .37))
    if fog:
        o.append(el.fog(doc, W, fy + 10, 60, seed=len(key) + 3, dur=58, opacity=.14, color="#9C7FD6", name=key + "Fog"))
    return "".join(o)


def vignette(doc: Doc, W: float, H: float, key: str = "vig", strength: float = .75) -> str:
    g = radial(doc, key, [(0, "#020203", 0), (.65, "#020203", strength * .35), (1, "#020203", strength)], .5, .5, .75)
    return f'<rect width="{n(W)}" height="{n(H)}" fill="{g}"/>'


def grain(doc: Doc, W: float, H: float, key: str = "grain", opacity: float = .06) -> str:
    """Fine film grain over a scene (static)."""
    doc.defs(key, f'<filter id="{key}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" '
                  'numOctaves="2" seed="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>')
    return f'<rect width="{n(W)}" height="{n(H)}" filter="url(#{key})" opacity="{n(opacity, 2)}"/>'


# ── powers ─────────────────────────────────────────────────────────────────────

def tendrils(doc: Doc, x: float, y: float, count: int = 9, reach: float = 170, seed: int = 2, key: str = "tdr") -> str:
    """POWER 01 · shadow manipulation: black-violet smoke tendrils coiling up from his hand."""
    rnd = random.Random(seed)
    doc.defs(key + "B", f'<filter id="{key}B" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.2"/></filter>')
    doc.keyframes(key, "0%,100%{stroke-dashoffset:0}100%{stroke-dashoffset:-60}")
    doc.keyframes(key + "W", "0%,100%{transform:rotate(-5deg) scale(1)}50%{transform:rotate(5deg) scale(1.04)}")
    doc.keyframes("sTw", "0%,100%{opacity:.15}50%{opacity:.9}")
    o = [f'<circle cx="{n(x)}" cy="{n(y)}" r="30" fill="#050309" opacity=".8" filter="url(#{key}B)"/>']
    for i in range(count):
        a = math.radians(rnd.uniform(-175, -5))
        L = reach * rnd.uniform(.55, 1)
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
        c1 = (x + math.cos(a + 1.1) * L * .5, y + math.sin(a + 1.1) * L * .5)
        c2 = (x + math.cos(a - .8) * L * .85, y + math.sin(a - .8) * L * .85)
        d = f"M{n(x)} {n(y)}C{n(c1[0])} {n(c1[1])} {n(c2[0])} {n(c2[1])} {n(ex)} {n(ey)}"
        w = rnd.uniform(9, 18)
        o.append(f'<g style="transform-origin:{n(x)}px {n(y)}px;animation:{key}W {n(rnd.uniform(6, 10))}s ease-in-out {n(-i * 1.3)}s infinite">'
                 f'<path d="{d}" stroke="{P.primary}" stroke-width="{n(w + 6)}" fill="none" stroke-linecap="round" opacity=".22" filter="url(#{key}B)"/>'
                 f'<path d="{d}" stroke="#040207" stroke-width="{n(w)}" fill="none" stroke-linecap="round" opacity=".92" filter="url(#{key}B)"/>'
                 f'<path d="{d}" stroke="{P.glow}" stroke-width=".9" fill="none" stroke-dasharray="4 14" '
                 f'style="animation:{key} {n(rnd.uniform(3, 5))}s linear infinite" opacity=".85"/></g>')
    motes = "".join(f'<circle cx="{n(x + rnd.uniform(-reach, reach) * .7)}" cy="{n(y - rnd.uniform(0, reach))}" r="{n(rnd.uniform(.8, 2))}" '
                    f'fill="{P.glow}" style="animation:sTw {n(rnd.uniform(2, 4))}s {n(rnd.uniform(0, 3))}s infinite"/>' for _ in range(16))
    return "".join(o) + motes


def neural_panel(doc: Doc, x: float, y: float, w: float, h: float, key: str = "nn", layers=(3, 5, 5, 3), label: str = "NEURAL NET") -> str:
    """POWER 02 · AI hologram: a floating violet panel with a live neural network."""
    from .text import text_use
    g = linear(doc, key + "G", [(0, P.glow, .16), (1, P.primary, .04)], 0, 0, 0, 1)
    doc.keyframes(key + "F", "to{stroke-dashoffset:-24}")
    doc.keyframes(key + "N", "0%,100%{opacity:.35}50%{opacity:1}")
    cols = len(layers)
    pts = []
    for ci, cnt in enumerate(layers):
        cx = x + w * (ci + .5) / cols
        pts.append([(cx, y + 26 + (h - 40) * (k + .5) / cnt) for k in range(cnt)])
    edges = "".join(f"M{n(a[0])} {n(a[1])}L{n(b[0])} {n(b[1])}" for L1, L2 in zip(pts, pts[1:]) for a in L1 for b in L2)
    nodes = "".join(f'<circle cx="{n(px)}" cy="{n(py)}" r="3.2" fill="{P.bg3}" stroke="{P.ice}" stroke-width="1.1" '
                    f'style="animation:{key}N {n(1.4 + (i * 7 % 10) / 7)}s {n((i * 3 % 7) / 5)}s infinite"/>'
                    for i, (px, py) in enumerate(p for L in pts for p in L))
    t, _ = text_use(doc, label, x + 10, y + 15, 8.5, "ui6", tracking=.26, fill=P.ice)
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="6" fill="{g}" stroke="{P.glow}" stroke-opacity=".6"/>'
            f'<path d="{edges}" stroke="{P.glow}" stroke-width=".6" opacity=".45"/>'
            f'<path d="{edges}" stroke="{P.ice}" stroke-width=".7" stroke-dasharray="3 9" opacity=".7" style="animation:{key}F 1.6s linear infinite"/>'
            + nodes + t)


def code_panel(doc: Doc, x: float, y: float, w: float, h: float, lines, key: str = "cp", size: float = 9.5) -> str:
    """POWER 05 · code control: a floating code window."""
    from .text import text_use
    g = linear(doc, key + "G", [(0, "#1A0D26", .92), (1, "#050507", .92)], 0, 0, 0, 1)
    o = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="6" fill="{g}" stroke="{P.glow}" stroke-opacity=".65"/>',
         f'<path d="M{n(x)} {n(y + 16)}H{n(x + w)}" stroke="{P.line2}"/>',
         "".join(f'<circle cx="{n(x + 10 + i * 8)}" cy="{n(y + 8)}" r="2.4" fill="{c}"/>' for i, c in enumerate((P.glow, P.primary, P.dim)))]
    for i, (ln, col) in enumerate(lines):
        t, _ = text_use(doc, ln, x + 10, y + 32 + i * (size + 5), size, "mono", fill=col)
        o.append(t)
    return "".join(o)


def data_stream(doc: Doc, x0: float, y0: float, x1: float, y1: float, lift: float = 90, count: int = 24, key: str = "ds", seed: int = 5) -> str:
    """POWER 03 · data absorption: particles + glyphs flowing along an arc between two points."""
    rnd = random.Random(seed)
    path = f"M{n(x0)} {n(y0)}Q{n((x0 + x1) / 2)} {n(min(y0, y1) - lift)} {n(x1)} {n(y1)}"
    doc.defs(key, f'<path id="{key}" d="{path}"/>')
    doc.keyframes(key + "F", "to{stroke-dashoffset:-60}")
    o = [f'<path d="{path}" stroke="{P.glow}" stroke-width="10" fill="none" opacity=".12" filter="url(#mvSoft2)"/>',
         f'<path d="{path}" stroke="{P.ice}" stroke-width="1.2" fill="none" stroke-dasharray="2 10" opacity=".8" style="animation:{key}F 2s linear infinite"/>']
    glyphs = ["0", "1", "{", "}", "λ", "Σ", "∂", "<", ">", "·"]
    from .text import text_use
    for i in range(count):
        dur = rnd.uniform(2.4, 4.2)
        if i % 3 == 0:
            g = rnd.choice(glyphs[:4] + glyphs[7:])
            t, _ = text_use(doc, g, 0, 3, rnd.uniform(7, 10), "mono", anchor="middle", fill=P.ice)
            mark = f'<g>{t}</g>'
        else:
            mark = f'<circle r="{n(rnd.uniform(1, 2.2))}" fill="{rnd.choice([P.ice, P.glow, "#FFFFFF"])}"/>'
        o.append(f'<g opacity=".9">{mark}<animateMotion dur="{n(dur, 2)}s" begin="{n(-rnd.uniform(0, dur), 2)}s" repeatCount="indefinite">'
                 f'<mpath href="#{key}"/></animateMotion></g>')
    return "".join(o)


def clock(doc: Doc, cx: float, cy: float, r: float = 34, key: str = "clk") -> str:
    """POWER 06 · time control: a floating violet clock with rotating rings and hands."""
    face = radial(doc, key + "F", [(0, "#1A0D26", .9), (1, "#050507", .95)])
    halo = radial(doc, key + "H", [(0, P.glow, .35), (1, P.glow, 0)])
    doc.keyframes(key + "S", "to{transform:rotate(360deg)}")
    ticks = "".join(f'<path d="M{n(cx + math.cos(math.radians(a)) * r * .82)} {n(cy + math.sin(math.radians(a)) * r * .82)}'
                    f'L{n(cx + math.cos(math.radians(a)) * r * (.7 if a % 90 else .62))} {n(cy + math.sin(math.radians(a)) * r * (.7 if a % 90 else .62))}"/>'
                    for a in range(0, 360, 30))
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 2.4)}" fill="{halo}"/>'
            f'<g style="transform-origin:{n(cx)}px {n(cy)}px;animation:{key}S 40s linear infinite">'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 1.55)}" fill="none" stroke="{P.glow}" stroke-width=".8" stroke-dasharray="2 8" opacity=".7"/></g>'
            f'<g style="transform-origin:{n(cx)}px {n(cy)}px;animation:{key}S 24s linear infinite reverse">'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 1.25)}" fill="none" stroke="{P.ice}" stroke-width=".7" stroke-dasharray="14 6 2 6" opacity=".6"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{face}" stroke="{P.ice}" stroke-width="1.4"/>'
            f'<g stroke="{P.ice}" stroke-width="1.2" stroke-linecap="round">{ticks}</g>'
            f'<g style="transform-origin:{n(cx)}px {n(cy)}px;animation:{key}S 6s linear infinite">'
            f'<path d="M{n(cx)} {n(cy)}V{n(cy - r * .72)}" stroke="{P.glow}" stroke-width="1.4" stroke-linecap="round"/></g>'
            f'<g style="transform-origin:{n(cx)}px {n(cy)}px;animation:{key}S 72s linear infinite">'
            f'<path d="M{n(cx)} {n(cy)}H{n(cx + r * .5)}" stroke="{P.text}" stroke-width="2" stroke-linecap="round"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="2.4" fill="{P.text}"/>')


def floating_book(doc: Doc, cx: float, cy: float, s: float = 1, key: str = "bk") -> str:
    """POWER 07 · knowledge vision: an open ancient book, pages rising as holograms."""
    page = linear(doc, key + "P", [(0, "#F1ECFF"), (1, "#C4B5FD")], 0, 0, 1, 0)
    doc.keyframes(key + "R", "0%{transform:translateY(0) rotate(0);opacity:0}20%{opacity:.9}100%{transform:translateY(-70px) rotate(-8deg);opacity:0}")
    lines = "".join(f'<path d="M{sx * 5} {-18 + k * 4.5}Q{sx * 12} {-20 + k * 4.5} {sx * 19} {-18 + k * 4.5}" stroke="#6D5A96" stroke-width=".9" fill="none"/>'
                    for sx in (-1, 1) for k in range(4))
    pages = "".join(f'<g style="animation:{key}R 4.5s ease-out {i * 1.5}s infinite;opacity:0" class="rv">'
                    f'<rect x="{-9 + i * 4}" y="-36" width="16" height="20" rx="1.5" fill="none" stroke="{P.ice}" stroke-width=".8"/>'
                    f'<path d="M{-6 + i * 4} -30H{3 + i * 4}M{-6 + i * 4} -26H{1 + i * 4}M{-6 + i * 4} -22H{4 + i * 4}" stroke="{P.glow}" stroke-width=".7"/></g>'
                    for i in range(3))
    glow = radial(doc, key + "G", [(0, P.glow, .5), (1, P.glow, 0)])
    return (f'<g transform="translate({n(cx)} {n(cy)}) scale({n(s, 2)})"><ellipse cx="0" cy="-16" rx="42" ry="26" fill="{glow}"/>'
            f'<path d="M0 0L-27-4L-27-30L0-26L27-30L27-4Z" fill="#12091C" stroke="{P.glow}" stroke-width="1.1"/>'
            f'<path d="M0-3Q-12-8-25-6L-25-28Q-12-30 0-25Z" fill="{page}"/><path d="M0-3Q12-8 25-6L25-28Q12-30 0-25Z" fill="{page}"/>'
            f'{lines}<path d="M0-25L0-3" stroke="#6D5A96" stroke-width="1"/>{pages}</g>')


def contrib_grid(doc: Doc, x: float, y: float, cols: int = 22, rows: int = 7, cell: float = 11, gap: float = 3, key: str = "cg", seed: int = 9) -> str:
    """POWER 08 · GitHub energy: a decorative contribution-style grid (not real data)."""
    rnd = random.Random(seed)
    shades = [P.bg4, "#2E1065", "#4C1D95", P.accent, P.glow]
    doc.keyframes(key, "0%,100%{opacity:.45}50%{opacity:1}")
    cells = []
    for c in range(cols):
        for r in range(rows):
            lv = rnd.choices(range(5), weights=(5, 3, 2, 1.4, 1))[0]
            anim = f' style="animation:{key} {n(rnd.uniform(2, 5))}s {n(rnd.uniform(0, 4))}s infinite"' if lv >= 3 else ""
            cells.append(f'<rect x="{n(x + c * (cell + gap))}" y="{n(y + r * (cell + gap))}" width="{n(cell)}" height="{n(cell)}" rx="2" '
                         f'fill="{shades[lv]}"{anim}/>')
    return "".join(cells)


def clone(doc: Doc, fig: str, x: float, y: float, s: float, opacity: float = .35, key: str = "cl") -> str:
    """POWER 09 · digital clone: a translucent violet copy of the vampire."""
    doc.defs(key, f'<filter id="{key}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" '
                  'values="0 0 0 0 .42  0 0 0 0 .25  0 0 0 0 .9  0 0 0 .9 0"/><feGaussianBlur stdDeviation=".6"/></filter>')
    doc.keyframes(key + "F", "0%,100%{opacity:" + n(opacity * .6, 2) + "}50%{opacity:" + n(opacity, 2) + "}")
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(s, 3)})" style="animation:{key}F 5s ease-in-out infinite">'
            f'<g filter="url(#{key})">{fig}</g></g>')


def dissolve(doc: Doc, W: float, H: float, x0: float, x1: float, key: str = "dsv") -> tuple[str, str]:
    """POWER 10 · void teleportation: (mask defs id, particle field) — the figure fades to the right
    and scatters into black-violet motes."""
    g = linear(doc, key + "G", [(0, "#FFFFFF", 1), (.45, "#FFFFFF", 1), (.8, "#FFFFFF", .15), (1, "#FFFFFF", 0)], 0, 0, 1, 0)
    doc.defs(key, f'<mask id="{key}" maskUnits="userSpaceOnUse" x="0" y="0" width="{n(W)}" height="{n(H)}">'
                  f'<rect x="{n(x0)}" y="0" width="{n(x1 - x0)}" height="{n(H)}" fill="{g}"/></mask>')
    rnd = random.Random(12)
    doc.keyframes(key + "P", "0%{transform:translate(0,0);opacity:0}15%{opacity:1}100%{transform:translate(70px,-36px);opacity:0}")
    parts = "".join(f'<rect x="{n(rnd.uniform(x0 + (x1 - x0) * .5, x1))}" y="{n(rnd.uniform(H * .12, H * .95))}" '
                    f'width="{n(rnd.uniform(1.4, 3.6))}" height="{n(rnd.uniform(1.4, 3.6))}" '
                    f'fill="{rnd.choice([P.glow, P.ice, "#050309", P.primary])}" '
                    f'style="animation:{key}P {n(rnd.uniform(2.5, 5))}s linear {n(-rnd.uniform(0, 5))}s infinite"/>' for _ in range(90))
    return key, parts
