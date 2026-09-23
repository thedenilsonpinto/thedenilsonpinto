"""Icons & buttons (nav, links, contact, back-to-top), the divider, the boot loader, and the
standalone effect overlays in assets/effects (transparent, so they sit on any dark page)."""
from __future__ import annotations

import random

from . import chamber as C
from . import elements as el
from . import mascot as M
from .core import Doc, linear, n, radial
from .fx import typewriter
from .hud import grid, scanline
from .ornament import diamond
from .palette import P
from .text import measure, text_use

NAV = [("ABOUT", "sigil:user"), ("FLASHDROP", "sigil:bolt"), ("PROJECTS", "sigil:layers"), ("SKILLS", "sigil:brain"),
       ("EXPERIENCE", "sigil:briefcase"), ("EDUCATION", "sigil:cap"), ("GITHUB", "github"), ("CONTACT", "sigil:mail")]


def _icon(ic: str, cx: float, cy: float, size: float, color: str | None = None) -> str:
    from .midnight import icon
    return icon(ic, cx, cy, size, color)


def _glass(d: Doc, W: float, H: float, r: float, key: str, pulse: str, delay: float = 0) -> str:
    """Black glass with a thin violet edge that breathes, and a faint lavender highlight on top."""
    g = linear(d, key + "G", [(0, "#1A0D26"), (1, "#050507")], 0, 0, 0, 1)
    d.keyframes(pulse, "0%,100%{opacity:.35}50%{opacity:.85}")
    return (f'<rect x="1" y="1" width="{n(W - 2)}" height="{n(H - 2)}" rx="{n(r)}" fill="{g}"/>'
            f'<rect x="1" y="1" width="{n(W - 2)}" height="{n(H - 2)}" rx="{n(r)}" fill="none" stroke="{P.glow}" stroke-width="1" '
            f'style="animation:{pulse} 4s ease-in-out {delay:.1f}s infinite"/>'
            f'<path d="M{n(r + 2)} 1.6H{n(W * .42)}" stroke="{P.ice}" stroke-opacity=".45" stroke-width=".8"/>')


def nav_button(label: str, ic: str, i: int = 0) -> Doc:
    size, H = 12, 40
    tw = measure(label, "ui6", size, .24)
    W = round(tw + 60)
    d = Doc(W, H, "FlashDrop" if label == "FLASHDROP" else "GitHub" if label == "GITHUB" else label.title())
    d.keyframes("nbLine", "0%,100%{transform:scaleX(.25);opacity:.35}50%{transform:scaleX(1);opacity:.9}")
    t, _ = text_use(d, label, 42, 24.8, size, "ui6", tracking=.24, fill=P.text)
    d.add(_glass(d, W, H, 10, "nb", "nbPulse", i * .4), _icon(ic, 23, 20, 15, P.ice), t,
          f'<rect x="{W / 2 - 18:.1f}" y="{H - 4}" width="36" height="1.6" rx=".8" fill="{P.glow}" '
          f'style="transform-box:fill-box;transform-origin:center;animation:nbLine 4s ease-in-out {i * .4:.1f}s infinite"/>')
    return d


def link_button(label: str, ic: str, title: str) -> Doc:
    W, H = 200, 48
    d = Doc(W, H, title)
    d.keyframes("btArrow", "0%,100%{transform:translateX(0);opacity:.5}50%{transform:translateX(4px);opacity:1}")
    t, _ = text_use(d, label, 58, 29.5, 13.5, "ui6", tracking=.24, fill=P.text)
    d.add(_glass(d, W, H, 12, "bt", "btPulse"),
          f'<circle cx="30" cy="24" r="15" fill="#12091C" stroke="{P.glow}" stroke-opacity=".6"/>', _icon(ic, 30, 24, 16, P.ice), t,
          f'<path d="M{W - 30} 18L{W - 24} 24L{W - 30} 30" fill="none" stroke="{P.glow}" stroke-width="1.8" stroke-linecap="round" '
          f'stroke-linejoin="round" style="animation:btArrow 1.8s ease-in-out infinite"/>')
    return d


def contact_button(label: str, ic: str, value: str, title: str) -> Doc:
    W, H = 300, 64
    d = Doc(W, H, title)
    d.keyframes("cbArrow", "0%,100%{transform:translateX(0);opacity:.5}50%{transform:translateX(4px);opacity:1}")
    t, _ = text_use(d, label, 70, 28, 12, "ui6", tracking=.3, fill=P.ice)
    vs = 14
    while measure(value, "ui5", vs) > W - 110 and vs > 10:
        vs -= .5
    v, _ = text_use(d, value, 70, 47, vs, "ui5", fill=P.text)
    d.add(_glass(d, W, H, 14, "cb", "cbPulse"),
          f'<circle cx="36" cy="32" r="21" fill="#12091C" stroke="{P.glow}" stroke-opacity=".7"/>', _icon(ic, 36, 32, 20, P.ice), t, v,
          f'<path d="M{W - 30} 25L{W - 23} 32L{W - 30} 39" fill="none" stroke="{P.glow}" stroke-width="1.8" stroke-linecap="round" '
          f'stroke-linejoin="round" style="animation:cbArrow 1.8s ease-in-out infinite"/>')
    return d


def top_button() -> Doc:
    W, H = 170, 40
    d = Doc(W, H, "Back to top")
    d.keyframes("tpUp", "0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}")
    t, _ = text_use(d, "BACK TO TOP", 46, 24.8, 12, "ui6", tracking=.24, fill=P.text)
    d.add(_glass(d, W, H, 10, "tp", "tpPulse"),
          f'<path d="M18 23L25 16L32 23M25 16V29" fill="none" stroke="{P.ice}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
          f'style="animation:tpUp 1.8s ease-in-out infinite"/>', t)
    return d


def divider() -> Doc:
    W, H = 1000, 28
    d = Doc(W, H, "Divider")
    line = linear(d, "dvL", [(0, P.glow, 0), (.5, P.glow, .8), (1, P.glow, 0)], 0, 0, 1, 0)
    d.keyframes("dvRun", "0%{transform:translateX(0);opacity:0}15%,85%{opacity:1}100%{transform:translateX(440px);opacity:0}")
    d.keyframes("dvSpin", "to{transform:rotate(360deg)}")
    d.add(f'<rect x="40" y="13.4" width="920" height="1" fill="{line}"/>',
          f'<g style="transform-origin:500px 14px;animation:dvSpin 14s linear infinite"><circle cx="500" cy="14" r="10" fill="none" stroke="{P.accent}" stroke-dasharray="3 5"/></g>',
          diamond(500, 14, 4.6, P.glow),
          f'<circle cx="514" cy="14" r="2.2" fill="{P.ice}" style="animation:dvRun 3.8s ease-in-out infinite"/>',
          f'<g transform="scale(-1 1) translate(-1000 0)"><circle cx="514" cy="14" r="2.2" fill="{P.ice}" style="animation:dvRun 3.8s ease-in-out infinite"/></g>')
    return d


def loader(name: str = "DENILSON PINTO B") -> Doc:
    W, H = 1000, 64
    d = Doc(W, H, "The Midnight AI Lab — boot sequence",
            f"Boot sequence: summoning the Midnight AI Lab, waking the guardian — {name}, AI engineer profile online.")
    bg = linear(d, "ldBg", [(0, "#0B0712"), (1, "#020203")], 0, 0, 0, 1)
    d.defs("ldClip", f'<clipPath id="ldClip"><rect width="{W}" height="{H}" rx="12"/></clipPath>')
    d.add(f'<rect width="{W}" height="{H}" rx="12" fill="{bg}"/><g clip-path="url(#ldClip)">{grid(d, W, H)}{scanline(d, W, H, 5, "ldScan")}</g>',
          f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="11.5" fill="none" stroke="{P.glow}" stroke-opacity=".5"/>')
    k, _ = text_use(d, "THE MIDNIGHT AI LAB", 44, 37, 12, "ui6", tracking=.3, fill=P.ice)
    d.add(diamond(28, 32.5, 4.6, P.glow), k)
    d.add(typewriter(d, ["summoning the midnight ai lab …", "waking the guardian …", "the gate is open — profile online"],
                     300, 37, 14, "mono", fill=P.text, caret=P.glow, cps=22, hold=1.6, key="ldTw"))
    d.keyframes("ldBar", "0%{transform:scaleX(0)}70%,100%{transform:scaleX(1)}")
    d.add(f'<rect x="770" y="29" width="186" height="6" rx="3" fill="#241137"/>'
          f'<rect x="770" y="29" width="186" height="6" rx="3" fill="{P.glow}" style="transform-box:fill-box;transform-origin:left;animation:ldBar 4.2s ease-in-out infinite"/>')
    return d


# ── standalone effect overlays (assets/effects) — transparent backgrounds ───────

def fx_fog() -> Doc:
    W, H = 1000, 180
    d = Doc(W, H, "Violet fog", "Transparent overlay: two layers of violet fog drifting at different speeds.")
    d.add(el.fog(d, W, 80, 70, seed=8, dur=60, opacity=.26, color="#9C7FD6", name="fxFogA"),
          el.fog(d, W, 120, 60, seed=9, dur=38, opacity=.22, color="#6D4FB0", name="fxFogB"))
    return d


def fx_particles() -> Doc:
    W, H = 1000, 220
    d = Doc(W, H, "Violet particles", "Transparent overlay: twinkling stars and rising violet motes.")
    d.add(el.stars(d, W, H * .6, 50, seed=3), el.embers(d, W, H, 46, seed=4, rise=200))
    return d


def fx_shadows() -> Doc:
    W, H = 1000, 240
    d = Doc(W, H, "Living shadows", "Transparent overlay: black-violet smoke pooling on the ground, shadow tendrils coiling up.")
    d.add(C.tendrils(d, 190, 236, 7, 170, seed=5, key="fsA"), C.tendrils(d, 810, 236, 7, 170, seed=8, key="fsB"))
    for i, x in enumerate((140, 400, 640, 880)):
        d.add(f'<g transform="translate({x} 228)">{M.smoke(d, 260, 0, seed=20 + i, count=6, key=f"fsSm{i}")}</g>')
    return d


def fx_violet_glow() -> Doc:
    W = H = 520
    d = Doc(W, H, "Violet glow", "Transparent overlay: a breathing violet energy glow with slow rings.")
    core = radial(d, "fgCore", [(0, P.ice, .55), (.18, P.glow, .38), (.5, P.primary, .14), (1, P.primary, 0)])
    d.keyframes("fgBreath", "0%,100%{transform:scale(.92);opacity:.75}50%{transform:scale(1.06);opacity:1}")
    d.keyframes("fgSpin", "to{transform:rotate(360deg)}")
    rnd = random.Random(6)
    d.keyframes("fgMote", "0%{transform:translateY(0);opacity:0}25%{opacity:1}100%{transform:translateY(-90px);opacity:0}")
    motes = "".join(f'<circle cx="{n(260 + rnd.uniform(-120, 120))}" cy="{n(300 + rnd.uniform(-60, 90))}" r="{n(rnd.uniform(.8, 2))}" '
                    f'fill="{rnd.choice([P.ice, P.glow])}" style="animation:fgMote {n(rnd.uniform(3, 6))}s ease-out {n(-rnd.uniform(0, 6))}s infinite"/>'
                    for _ in range(24))
    d.add(f'<circle cx="260" cy="260" r="250" fill="{core}" style="transform-box:fill-box;transform-origin:center;animation:fgBreath 6s ease-in-out infinite"/>',
          f'<g style="transform-origin:260px 260px;animation:fgSpin 40s linear infinite"><circle cx="260" cy="260" r="150" fill="none" '
          f'stroke="{P.glow}" stroke-width=".8" stroke-dasharray="2 9" opacity=".6"/></g>',
          f'<g style="transform-origin:260px 260px;animation:fgSpin 26s linear infinite reverse"><circle cx="260" cy="260" r="112" fill="none" '
          f'stroke="{P.ice}" stroke-width=".7" stroke-dasharray="18 8 3 8" opacity=".45"/></g>', motes)
    return d


def fx_bats() -> Doc:
    W, H = 1000, 200
    d = Doc(W, H, "Bats", "Transparent overlay: a flight of bats crossing a faint violet moon-glow.")
    halo = radial(d, "fbHalo", [(0, "#50199A", .45), (1, "#020203", 0)], .5, .5, .6)
    d.add(f'<ellipse cx="500" cy="100" rx="420" ry="90" fill="{halo}"/>', el.bat_swarm(d, W, 24, 176, 9, seed=12, name="fxB"))
    return d
