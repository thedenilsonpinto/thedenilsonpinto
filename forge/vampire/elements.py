"""World elements: violet moon, castle, bats, fog, stars, embers, lightning."""
from __future__ import annotations

import math
import random

from .core import Doc, glow_filter, n, radial
from .palette import P


# ── Violet moon ────────────────────────────────────────────────────────────────

def moon(doc: Doc, cx: float, cy: float, r: float, seed: int = 4, clouds: bool = True, cloud_w: float = 1.0) -> str:
    halo = radial(doc, "mHalo", [(0, P.accent, .45), (.35, P.primary, .2), (1, P.primary, 0)])
    disc = radial(doc, "mDisc", [(0, "#F5F3FF"), (.32, "#E2D3F8"), (.68, "#A06CE7"), (.9, "#631EBB"), (1, "#3D1372")], .4, .36, .74)
    doc.keyframes("mPulse", "0%,100%{opacity:.75;transform:scale(.96)}50%{opacity:1;transform:scale(1.05)}")
    doc.css("mPulse", ".mH{transform-box:fill-box;transform-origin:center;animation:mPulse 7s ease-in-out infinite}")
    rnd = random.Random(seed)
    blots = []
    for _ in range(7):
        a, d = rnd.uniform(0, 6.28), rnd.uniform(0, .62) * r
        bx, by, br = cx + math.cos(a) * d, cy + math.sin(a) * d, rnd.uniform(.12, .3) * r
        pts = [(bx + math.cos(t) * br * rnd.uniform(.7, 1.2), by + math.sin(t) * br * rnd.uniform(.7, 1.2)) for t in [i * .785 for i in range(8)]]
        blots.append("M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts) + "Z")
    craters = "".join(f'<circle cx="{n(cx + rnd.uniform(-.6, .6) * r)}" cy="{n(cy + rnd.uniform(-.6, .6) * r)}" r="{n(rnd.uniform(.03, .08) * r)}"/>' for _ in range(9))
    clip = doc.defs("mClip", f'<clipPath id="mClip"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/></clipPath>')
    o = [f'<circle class="mH" cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 2.9)}" fill="{halo}"/>',
         f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{disc}"/>',
         f'<g clip-path="url(#{clip})"><path d="{"".join(blots)}" fill="#471686" opacity=".38"/>'
         f'<g fill="#471686" opacity=".42">{craters}</g></g>',
         f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - .8)}" fill="none" stroke="{P.ice}" stroke-width="1.2" opacity=".35"/>']
    if clouds:
        doc.keyframes("mCloud", "0%{transform:translateX(-40px)}100%{transform:translateX(40px)}")
        for i, (dy, w, op, dur) in enumerate(((.35, 2.3 * cloud_w, .8, 26), (-.2, 1.6 * cloud_w, .55, 34))):
            y = cy + dy * r
            d = (f"M{n(cx - w * r)} {n(y)}q{n(r * .3)} {n(-r * .12)} {n(r * .6)} 0t{n(r * .6)} {n(-r * .02)}t{n(r * .6)} {n(r * .03)}"
                 f"t{n(r * .6)} 0t{n(r * .6)} {n(-r * .02)}l0 {n(r * .07)}q{n(-w * r)} {n(r * .05)} {n(-w * r * 2 + r * .6)} 0Z")
            o.append(f'<path d="{d}" fill="#060309" opacity="{op}" style="animation:mCloud {dur}s ease-in-out {i * -9}s infinite alternate"/>')
    return "".join(o)


# ── Castle ─────────────────────────────────────────────────────────────────────

def castle(doc: Doc, x: float, base: float, s: float = 1, fill: str = "#050506", windows: bool = True, seed: int = 2) -> str:
    """Gothic castle on a crag. (x, base) = bottom-centre; ~420 wide × 300 tall at s=1."""
    rnd = random.Random(seed)
    doc.keyframes("cFlick", "0%,100%{opacity:.95}40%{opacity:.55}45%{opacity:.9}70%{opacity:.7}")
    # towers: (cx, width, top, spire height)
    towers = [(-170, 24, -150, 70), (-122, 32, -196, 92), (-66, 28, -168, 76), (0, 44, -250, 150),
              (58, 30, -186, 84), (112, 38, -214, 110), (164, 22, -140, 60)]
    crag = (f"M-230 0L-214 -38L-190 -52L-176 -84L-150 -92L-120 -100L-80 -96L-40 -110L40 -112L90 -104L140 -98"
            f"L176 -86L196 -58L220 -40L236 0Z")
    parts = [crag, "M-176 -86L-176 -120L176 -120L176 -86Z"]
    wins = []
    for cx, w, top, sp in towers:
        x0, x1 = cx - w / 2, cx + w / 2
        # battlement notches + tower body + spire with a tiny flag pole
        parts.append(f"M{n(x0)} -96L{n(x0)} {n(top)}L{n(x0 - 3)} {n(top)}L{n(cx)} {n(top - sp)}L{n(x1 + 3)} {n(top)}L{n(x1)} {n(top)}L{n(x1)} -96Z")
        parts.append(f"M{n(cx - .8)} {n(top - sp)}L{n(cx - .8)} {n(top - sp - 12)}L{n(cx + .8)} {n(top - sp - 12)}L{n(cx + .8)} {n(top - sp)}Z")
        for k in range(int((-96 - top) / 26)):
            if rnd.random() < .55:
                wy = top + 14 + k * 26
                wins.append((cx + rnd.choice([-w * .2, 0, w * .2]), wy, rnd.uniform(0, 4)))
    # connecting walls with crenellations
    for a, b in ((-170, -122), (-122, -66), (-66, 0), (0, 58), (58, 112), (112, 164)):
        parts.append(f"M{a} -96L{a} -128" + "".join(f"L{n(a + (b - a) * (i + .5) / 6)} -128L{n(a + (b - a) * (i + .5) / 6)} -134L{n(a + (b - a) * (i + 1) / 6)} -134L{n(a + (b - a) * (i + 1) / 6)} -128" for i in range(6)) + f"L{b} -96Z")
    o = [f'<g transform="translate({n(x)} {n(base)}) scale({n(s, 3)})"><path d="{"".join(parts)}" fill="{fill}" stroke="{P.deep}" stroke-width="1.2" stroke-opacity=".55"/>']
    if windows:
        rose = radial(doc, "cRose", [(0, P.ice), (.45, P.glow, .8), (1, P.glow, 0)])
        o.append(f'<circle cx="0" cy="-205" r="16" fill="{rose}" style="animation:cFlick 5s infinite"/>'
                 f'<circle cx="0" cy="-205" r="6" fill="none" stroke="#050506" stroke-width="1.6"/>'
                 f'<path d="M0 -216L0 -194M-11 -205L11 -205" stroke="#050506" stroke-width="1.6"/>')
    if windows:
        wg = radial(doc, "cWin", [(0, P.ice), (.5, P.glow, .8), (1, P.glow, 0)])
        for wx, wy, dly in wins:
            o.append(f'<g style="animation:cFlick {n(2.5 + dly)}s {n(dly)}s infinite"><circle cx="{n(wx)}" cy="{n(wy)}" r="7" fill="{wg}" opacity=".5"/>'
                     f'<path d="M{n(wx - 2.2)} {n(wy + 4)}L{n(wx - 2.2)} {n(wy - 1.5)}Q{n(wx)} {n(wy - 5)} {n(wx + 2.2)} {n(wy - 1.5)}L{n(wx + 2.2)} {n(wy + 4)}Z" fill="{P.ice}"/></g>')
    o.append("</g>")
    return "".join(o)


# ── Bats ──────────────────────────────────────────────────────────────────────
BAT_UP = ("M0 -2C-4 -6 -10 -12 -18 -14C-16 -10 -17 -7 -20 -5C-15 -6 -12 -3 -10 0C-7 -1 -4 1 0 4"
          "C4 1 7 -1 10 0C12 -3 15 -6 20 -5C17 -7 16 -10 18 -14C10 -12 4 -6 0 -2Z")
BAT_DOWN = ("M0 -2C-4 -1 -10 2 -18 8C-15 8 -14 10 -15 14C-12 10 -9 9 -8 8C-6 7 -3 6 0 4"
            "C3 6 6 7 8 8C9 9 12 10 15 14C14 10 15 8 18 8C10 2 4 -1 0 -2Z")


def bat(flap: float = .42, delay: float = 0, eyes: bool = True, fill: str = "#030303") -> str:
    """One bat centred at 0,0 (wingspan 40). Wing flap = SMIL path morph."""
    e = (f'<circle cx="-1.3" cy="-.6" r=".75" fill="{P.glow}"/><circle cx="1.3" cy="-.6" r=".75" fill="{P.glow}"/>' if eyes else "")
    return (f'<path d="{BAT_UP}" fill="{fill}" stroke="{P.deep}" stroke-width=".5">'
            f'<animate attributeName="d" values="{BAT_UP};{BAT_DOWN};{BAT_UP}" dur="{n(flap, 2)}s" begin="{n(-delay, 2)}s" repeatCount="indefinite"/></path>'
            f'<path d="M-2.5 -3L-2 -6.5L-.8 -4L.8 -4L2 -6.5L2.5 -3Q2.8 3 0 5Q-2.8 3 -2.5 -3Z" fill="{fill}"/>{e}')


def bat_defs(doc: Doc) -> None:
    """Three shared animated bats (different flap speeds) referenced with <use>."""
    for i, flap in enumerate((.3, .38, .47)):
        doc.defs(f"bat{i}", f'<g id="bat{i}">{bat(flap, 0)}</g>')


def bat_swarm(doc: Doc, w: float, y0: float, y1: float, count: int = 9, seed: int = 11,
              dur: tuple = (9, 16), scale: tuple = (.45, 1.1), direction: int = 1, name: str = "bf") -> str:
    """Bats crossing a w-wide band between y0..y1 (CSS translate waypoints)."""
    rnd = random.Random(seed)
    bat_defs(doc)
    o = []
    for i in range(count):
        sc = rnd.uniform(*scale)
        d = rnd.uniform(*dur) * (1.25 - sc * .35)
        ys = [rnd.uniform(y0, y1) for _ in range(5)]
        xs = [-60, w * .25, w * .5, w * .75, w + 60]
        if direction < 0:
            xs = xs[::-1]
        kf = "".join(f"{p}%{{transform:translate({n(x)}px,{n(y)}px) scale({n(sc, 2)})}}" for p, x, y in zip((0, 25, 50, 75, 100), xs, ys))
        doc.keyframes(f"{name}{i}", kf)
        o.append(f'<g style="animation:{name}{i} {n(d)}s linear {n(-rnd.uniform(0, d))}s infinite">'
                 f'<use href="#bat{i % 3}" transform="scale({direction} 1)"/></g>')
    return "".join(o)


# ── Atmosphere ────────────────────────────────────────────────────────────────

def stars(doc: Doc, w: float, h: float, count: int = 60, seed: int = 5, avoid=()) -> str:
    """Twinkling star field; `avoid` = rects (x0, y0, x1, y1) kept clear (e.g. behind text)."""
    rnd = random.Random(seed)
    doc.keyframes("sTw", "0%,100%{opacity:.15}50%{opacity:.9}")
    out = []
    for _ in range(count):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h) ** 1.15 / h ** .15
        r, fill = rnd.choice([.6, .8, 1, 1.3]), rnd.choice(["#FFFFFF", "#E9DAFD", P.silver])
        dur, delay = rnd.uniform(2.5, 6), rnd.uniform(0, 5)
        if any(x0 - 4 <= x <= x1 + 4 and y0 - 4 <= y <= y1 + 4 for x0, y0, x1, y1 in avoid):
            continue
        out.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{fill}" style="animation:sTw {n(dur)}s {n(delay)}s infinite"/>')
    return "".join(out)


def fog(doc: Doc, w: float, y: float, h: float, seed: int = 8, dur: float = 60, opacity: float = .16,
        color: str = "#B9B9C6", name: str = "fg") -> str:
    """Seamless drifting fog band (two copies scroll by one width)."""
    g = radial(doc, f"{name}G", [(0, color, opacity), (1, color, 0)])
    rnd = random.Random(seed)
    blobs = "".join(f'<ellipse cx="{n(rnd.uniform(0, w))}" cy="{n(y + rnd.uniform(-.3, .3) * h)}" rx="{n(rnd.uniform(.12, .25) * w)}" '
                    f'ry="{n(rnd.uniform(.35, .6) * h)}" fill="{g}"/>' for _ in range(9))
    doc.keyframes(name, f"from{{transform:translateX(0)}}to{{transform:translateX({n(-w)}px)}}")
    return (f'<g style="animation:{name} {n(dur)}s linear infinite">{blobs}'
            f'<g transform="translate({n(w)} 0)">{blobs}</g></g>')


def embers(doc: Doc, w: float, h: float, count: int = 22, seed: int = 9, rise: float = 160) -> str:
    rnd = random.Random(seed)
    doc.keyframes("eRise", f"0%{{transform:translate(0,0);opacity:0}}15%{{opacity:1}}100%{{transform:translate(18px,-{n(rise)}px);opacity:0}}")
    return "".join(f'<circle cx="{n(rnd.uniform(0, w))}" cy="{n(rnd.uniform(h * .45, h))}" r="{n(rnd.uniform(.7, 1.9))}" '
                   f'fill="{rnd.choice([P.glow, P.ice, P.accent])}" style="animation:eRise {n(rnd.uniform(5, 11))}s linear {n(-rnd.uniform(0, 11))}s infinite"/>'
                   for _ in range(count))


def lightning(doc: Doc, x: float, y: float, h: float, w: float, H: float, seed: int = 3, period: float = 11) -> str:
    """A rare bolt near the horizon plus a faint sky flash."""
    rnd = random.Random(seed)
    doc.keyframes("lBolt", "0%,93%,100%{opacity:0}94%{opacity:1}95%{opacity:.15}96.5%{opacity:.9}98%{opacity:0}")
    doc.keyframes("lSky", "0%,93%,100%{opacity:0}94%{opacity:.14}95%{opacity:.03}96.5%{opacity:.1}98%{opacity:0}")
    px, py, d = x, y, f"M{n(x)} {n(y)}"
    while py < y + h:
        px += rnd.uniform(-14, 14)
        py += rnd.uniform(10, 22)
        d += f"L{n(px)} {n(py)}"
    gl = glow_filter(doc, "lGlow", 3, 2)
    return (f'<rect width="{n(w)}" height="{n(H)}" fill="#E4D1FD" style="animation:lSky {period}s infinite"/>'
            f'<path d="{d}" stroke="#EFE4FE" stroke-width="1.6" fill="none" filter="{gl}" style="animation:lBolt {period}s infinite"/>')

