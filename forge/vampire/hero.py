"""Scene 01 — HERO · the castle entrance.

Your castle painting fills the panel; the Midnight AI Vampire stands on the path in front
of the violet moon with violet energy gathering above his raised hand. Name, title and the
typed taglines sit over the darkened side of the painting.
"""
from __future__ import annotations

import random

from . import elements as el
from . import mascot as M
from .backdrop import image
from .core import Doc, linear, n, radial
from .data import title_case
from .fx import typewriter
from .hud import brackets, status_pill
from .ornament import diamond
from .palette import P
from .text import measure, text_path, text_use

W, H = 1000, 660


def neon_name(doc: Doc, text: str, x: float, y: float, size: float, key: str) -> tuple[str, float]:
    tp, w = text_path(text, x, y, size, "cinzel9", tracking=.05)
    d = tp[len('<path d="'):-3]
    ice = linear(doc, f"{key}I", [(0, "#FFFFFF"), (.55, "#EDE7FF"), (1, P.ice)], 0, y - size * .72, 0, y, units="userSpaceOnUse")
    doc.defs(f"{key}F", f'<filter id="{key}F" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="{n(size * .12)}"/></filter>')
    doc.keyframes("heroFlicker", "0%,18%,22%,24%,53%,57%,100%{opacity:.85}20%,23%,55%{opacity:.35}")
    return (f'<path d="{d}" fill="{P.primary}" filter="url(#{key}F)" style="animation:heroFlicker 8s infinite"/>'
            f'<path d="{d}" fill="{ice}"/>'), w


def energy_orb(doc: Doc, x: float, y: float, r: float = 14, key: str = "hrOrb", seed: int = 4) -> str:
    """Violet energy gathering above an open palm: core, rings, orbiting motes."""
    core = radial(doc, key + "C", [(0, "#FFFFFF", .95), (.25, P.ice, .9), (.6, P.glow, .55), (1, P.primary, 0)])
    doc.keyframes(key + "P", "0%,100%{transform:scale(.9);opacity:.8}50%{transform:scale(1.12);opacity:1}")
    doc.keyframes(key + "S", "to{transform:rotate(360deg)}")
    doc.keyframes(key + "M", "0%{transform:translateY(0);opacity:0}25%{opacity:1}100%{transform:translateY(-38px);opacity:0}")
    rnd = random.Random(seed)
    motes = "".join(f'<circle cx="{n(x + rnd.uniform(-r, r))}" cy="{n(y + rnd.uniform(-r * .4, r))}" r="{n(rnd.uniform(.8, 1.8))}" '
                    f'fill="{rnd.choice([P.ice, P.glow, "#FFFFFF"])}" style="animation:{key}M {n(rnd.uniform(2.2, 4.2))}s ease-out '
                    f'{n(-rnd.uniform(0, 4))}s infinite"/>' for _ in range(14))
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 2.6)}" fill="{core}" opacity=".45"/>'
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{core}" style="transform-box:fill-box;transform-origin:center;'
            f'animation:{key}P 2.8s ease-in-out infinite"/>'
            f'<g style="transform-origin:{n(x)}px {n(y)}px;animation:{key}S 9s linear infinite">'
            f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r * 1.9)}" ry="{n(r * .55)}" fill="none" stroke="{P.ice}" stroke-width=".9" opacity=".7" stroke-dasharray="3 5"/></g>'
            f'<g style="transform-origin:{n(x)}px {n(y)}px;animation:{key}S 14s linear infinite reverse">'
            f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(r * 1.4)}" ry="{n(r * 1.9)}" fill="none" stroke="{P.glow}" stroke-width=".7" opacity=".55" stroke-dasharray="2 6"/></g>'
            + motes)


def hero(name_lines=("DENILSON", "PINTO B"), title="AI ENGINEER",
         specialties=("Machine Learning • LLMs • Generative AI", "Data Science • Software Development"),
         taglines=("Building intelligent systems beyond the ordinary.", "AI, data and intelligent applications — built after dark."),
         status="FINAL YEAR  •  BUILDING FLASHDROP") -> Doc:
    full = " ".join(name_lines)
    d = Doc(W, H, f"{full} — {title_case(title)}",
            f"{full}, {title_case(title)} — {' • '.join(specialties)}. {taglines[0]} The Midnight AI Vampire, an original "
            "character, stands before a gothic castle under a violet moon, violet energy rising from his raised hand.")
    d.defs("hrClip", f'<clipPath id="hrClip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    d.add(f'<rect width="{W}" height="{H}" rx="22" fill="{P.bg0}"/><g clip-path="url(#hrClip)">')
    # the castle painting — mirrored so the moon rises behind him on the right
    d.add(image(d, "land", 0, 0, W, H, box=(168, 0, 1497, 878), px=1.2, key="hrBg", mirror=True, bright=.9))
    shade = linear(d, "hrShade", [(0, "#020203", .92), (.42, "#020203", .72), (.62, "#020203", .12), (1, "#020203", 0)], 0, 0, 1, 0)
    floor = linear(d, "hrFloor", [(0, "#020203", 0), (.7, "#020203", .35), (1, "#020203", .9)], 0, 0, 0, 1)
    d.add(f'<rect width="{W}" height="{H}" fill="{shade}"/><rect width="{W}" height="{H}" fill="{floor}"/>')
    # moonlight bloom behind the vampire
    cx, cy = 742, 160
    bloom = radial(d, "hrBloom", [(0, P.ice, .38), (.35, P.glow, .16), (1, P.glow, 0)])
    d.keyframes("hrMoon", "0%,100%{opacity:.75}50%{opacity:1}")
    d.add(f'<circle cx="{cx}" cy="{cy}" r="230" fill="{bloom}" style="animation:hrMoon 7s ease-in-out infinite"/>')
    d.add(el.bat_swarm(d, W, 40, 280, 7, seed=13, name="hrBat", scale=(.35, .8)))
    # the vampire
    ax, ay, sc = 742, H - 18, 1.1
    px, py = M.palm("hero", 1, 18)
    orb = energy_orb(d, px, py - 18, 15)
    d.add(f'<g transform="translate({ax} {ay}) scale({sc})">{M.aura(d, 120, 240, -250)}'
          f'{M.figure(d, "hero", {"front": orb})}{M.smoke(d, 300, -6, seed=5, key="hrSmoke")}</g>')
    d.add(el.fog(d, W, H - 40, 90, seed=11, dur=55, opacity=.22, color="#9C7FD6", name="hrFogA"),
          el.fog(d, W, H - 8, 60, seed=12, dur=38, opacity=.2, color="#6D4FB0", name="hrFogB"),
          el.embers(d, W, H, 34, seed=7, rise=300))
    # ── text column ──
    x = 56
    kick, _ = text_use(d, "THE MIDNIGHT AI LAB  //  EST. AFTER DARK", x + 14, 96, 12.5, "ui6", tracking=.32, fill=P.ice)
    d.add(diamond(x + 3, 91.5, 4.5, P.glow), kick)
    size = 80
    while max(measure(t, "cinzel9", size, .05) for t in name_lines) > 470:
        size -= 1
    l1, _ = neon_name(d, name_lines[0], x, 176, size, "hn1")
    l2, _ = neon_name(d, name_lines[1], x, 176 + size * 1.02, size, "hn2")
    d.add(l1, l2)
    ty = 176 + size * 1.02 + 56
    tt, _ = text_use(d, title, x + 2, ty, 30, "ui6", tracking=.3, fill=P.ice)
    d.defs("hrTitleF", '<filter id="hrTitleF" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>')
    tglow, _ = text_use(d, title, x + 2, ty, 30, "ui6", tracking=.3, fill=P.primary)
    d.add(f'<g filter="url(#hrTitleF)" opacity=".9">{tglow}</g>', tt)
    sp1, _ = text_use(d, specialties[0], x + 2, ty + 36, 19, "ui5", tracking=.03, fill=P.text)
    sp2, _ = text_use(d, specialties[1], x + 2, ty + 62, 17, "ui5", tracking=.03, fill=P.text2)
    line = linear(d, "hrLine", [(0, P.glow), (.7, P.primary, .6), (1, P.primary, 0)], 0, 0, 1, 0)
    d.add(sp1, sp2, f'<rect x="{x}" y="{n(ty + 82)}" width="440" height="1.2" fill="{line}"/>', diamond(x, ty + 82.6, 3.2, P.glow))
    ts = 25
    while max(measure(t, "serif_i", ts) for t in taglines) > 450:
        ts -= .5
    d.add(typewriter(d, list(taglines), x + 2, ty + 124, ts, "serif_i", fill=P.text, caret=P.glow, key="hrTw"))
    pill, _ = status_pill(d, x + 2, ty + 150, status)
    d.add(pill)
    hud, _ = text_use(d, "CASTLE ENTRANCE  •  MOON PHASE: FULL  •  SIGNAL STABLE", x + 2, H - 30, 10.5, "ui6", tracking=.26, fill=P.muted)
    d.add(hud, "</g>")
    d.keyframes("hudPulse", "0%,100%{opacity:.55}50%{opacity:1}")
    d.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21.5" fill="none" stroke="{P.glow}" stroke-opacity=".55" '
          f'stroke-width="1.2" style="animation:hudPulse 6s ease-in-out infinite"/>', brackets(W, H, 12, 20, P.glow))
    return d
