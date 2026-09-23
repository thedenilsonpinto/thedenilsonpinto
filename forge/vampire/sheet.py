"""The Midnight AI Vampire — master character sheet, scene roster, and one transparent
character file per scene (assets/vampire/<scene>/).

Everything is drawn from mascot.py: an ORIGINAL character, not based on any real person
or on any existing character. Each scene file is the same vampire with that chamber's
power, on a transparent background, so he can be reused anywhere.
"""
from __future__ import annotations

import math
import random

from . import chamber as C
from . import mascot as M
from .core import Doc, linear, n, radial
from .flashdrop import portal
from .hero import energy_orb
from .hud import panel, title_bar
from .ornament import diamond
from .palette import P
from .scenes import burst
from .sigils import sigil
from .text import measure, text_use

# number, file under assets/vampire/, scene, power, chamber · README section, pose
SCENES = [
    ("01", "hero/hero.svg", "HERO", "VIOLET ENERGY", "CASTLE ENTRANCE · HERO", "hero"),
    ("02", "about/shadow-king.svg", "SHADOW KING", "POWER 01 · SHADOW MANIPULATION", "SHADOW CHAMBER · ABOUT", "shadow"),
    ("03", "ai/ai-master.svg", "AI MASTER", "POWER 02 · AI HOLOGRAM", "AI LABORATORY · AI / ML", "holo"),
    ("04", "coding/coder.svg", "CODER", "POWER 05 · CODE CONTROL", "CODE CRYPT · TERMINAL", "coder"),
    ("05", "flashdrop/portal-opener.svg", "FLASHDROP PORTAL", "POWER 04 · FILE TELEPORTATION", "PORTAL CHAMBER · FLASHDROP", "portal"),
    ("06", "skills/data-sorcerer.svg", "DATA SORCERER", "POWER 03 · DATA ABSORPTION", "DATA CHAMBER · SKILLS", "sorcerer"),
    ("07", "projects/project-commander.svg", "PROJECT COMMANDER", "POWER 05 · CODE CONTROL", "COMMAND ROOM · PROJECTS", "commander"),
    ("08", "experience/time-keeper.svg", "TIME KEEPER", "POWER 06 · TIME CONTROL", "TIME CHAMBER · EXPERIENCE", "timekeeper"),
    ("09", "education/knowledge-keeper.svg", "KNOWLEDGE KEEPER", "POWER 07 · KNOWLEDGE VISION", "ANCIENT LIBRARY · EDUCATION", "scholar"),
    ("10", "github/github-guardian.svg", "GITHUB GUARDIAN", "POWER 08 · GITHUB ENERGY", "DIGITAL OBSERVATORY · GITHUB", "guardian"),
    ("11", "transitions/void-walker.svg", "VOID WALKER", "POWER 10 · VOID TELEPORTATION", "PASSAGE · TRANSITION", "walk"),
    ("12", "transitions/teleportation.svg", "TELEPORTATION", "POWER 10 · VOID TELEPORTATION", "PASSAGE · TRANSITION", "final"),
    ("13", "hero/power-awakening.svg", "POWER AWAKENING", "VIOLET ENERGY BURST", "GREAT HALL · PROLOGUE", "awaken"),
    ("14", "footer/silhouette.svg", "SILHOUETTE", "SHADOW FORM", "DARK EXIT · FOOTER", "final"),
    ("15", "contact/final-guardian.svg", "FINAL GUARDIAN", "THE GATE IS OPEN", "CASTLE GATE · CONTACT", "final"),
    ("P09", "skills/digital-clones.svg", "DIGITAL CLONES", "POWER 09 · DIGITAL CLONES", "DATA CHAMBER · SKILLS", "stand"),
]
BY_NUM = {s[0]: s for s in SCENES}
CLONE_LABELS = [("AI", -1, 150), ("ML", 1, 150), ("DATA", -1, 272), ("DEV", 1, 272)]


# ── small local effects ─────────────────────────────────────────────────────────

def _fade(doc: Doc, key: str, x0: float, x1: float, y0: float, y1: float) -> str:
    """POWER 10 · a dissolve mask in the figure's own coordinates: solid → gone, left to right."""
    g = linear(doc, key + "G", [(0, "#FFFFFF", 1), (.42, "#FFFFFF", 1), (.8, "#FFFFFF", .12), (1, "#FFFFFF", 0)], 0, 0, 1, 0)
    doc.defs(key, f'<mask id="{key}" maskUnits="userSpaceOnUse" x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}">'
                  f'<rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" fill="{g}"/></mask>')
    return key


def _motes(doc: Doc, key: str, box: tuple, count: int, seed: int, dx: float = 70, dy: float = -36) -> str:
    """Black-violet motes drifting away (the dissolved part of him)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    doc.keyframes(key, f"0%{{transform:translate(0,0);opacity:0}}15%{{opacity:1}}100%{{transform:translate({n(dx)}px,{n(dy)}px);opacity:0}}")
    return "".join(f'<rect x="{n(rnd.uniform(x0, x1))}" y="{n(rnd.uniform(y0, y1))}" width="{n(rnd.uniform(1.6, 4.2))}" '
                   f'height="{n(rnd.uniform(1.6, 4.2))}" fill="{rnd.choice([P.glow, P.ice, "#050309", P.primary])}" '
                   f'style="animation:{key} {n(rnd.uniform(2.5, 5))}s linear {n(-rnd.uniform(0, 5))}s infinite"/>' for _ in range(count))


def _hex(cx: float, cy: float, r: float) -> str:
    return "M" + "L".join(f"{n(cx + r * math.cos(math.radians(60 * i - 90)))} {n(cy + r * math.sin(math.radians(60 * i - 90)))}"
                          for i in range(6)) + "Z"


def _beam(doc: Doc, key: str, a: tuple, b: tuple, bend: float = 0) -> str:
    g = linear(doc, key, [(0, P.ice, .9), (1, P.glow, .1)], a[0], a[1], b[0], b[1], units="userSpaceOnUse")
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - bend
    return (f'<path d="M{n(a[0])} {n(a[1])}Q{n(mx)} {n(my)} {n(b[0])} {n(b[1])}" fill="none" stroke="{g}" stroke-width="2"/>'
            f'<circle cx="{n(a[0])}" cy="{n(a[1])}" r="4.5" fill="{P.ice}" filter="url(#mvGlow)"/>')


# ── the character in each scene (feet at 0,0) → (svg, bbox) ─────────────────────

def character(d: Doc, num: str, k: str) -> tuple[str, tuple]:
    if num == "01":                                   # HERO — power awakens in his raised hand
        px, py = M.palm("hero", 1, 18)
        orb = energy_orb(d, px, py - 18, 15, key=k + "Orb")
        return (M.aura(d, 120, 240, -250) + M.figure(d, "hero", {"front": orb}) + M.smoke(d, 220, -6, seed=5, key=k + "Sm"),
                (-170, -505, 170, 24))
    if num == "02":                                   # SHADOW KING — shadow manipulation
        hx, hy = M.palm("shadow", 1, 10)
        td = C.tendrils(d, hx, hy, 9, 175, seed=4, key=k + "Td")
        return (M.aura(d, 120, 240, -250, 1.1) + M.smoke(d, 220, -4, seed=2, key=k + "Sm") + M.figure(d, "shadow", {"back": td}),
                (-170, -505, 330, 24))
    if num == "03":                                   # AI MASTER — AI holograms
        (lx, ly), (rx, ry) = M.palm("holo", -1, 8), M.palm("holo", 1, 8)
        d.keyframes(k + "F", "0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}")
        holo = (f'<g style="animation:{k}F 6s ease-in-out infinite">{C.neural_panel(d, -270, -512, 120, 98, k + "N", (3, 4, 3), "NEURAL NET")}</g>'
                f'<g style="animation:{k}F 7s ease-in-out -2s infinite">' + C.code_panel(d, 150, -500, 126, 72, [
                    ("tokens = embed(text)", P.ice), ("out = model(tokens)", P.text2), ("return generate(out)", P.glow)], k + "Cp", 8) + "</g>"
                + _beam(d, k + "Bl", (lx, ly), (-190, -414), 20) + _beam(d, k + "Br", (rx, ry), (200, -428), 20))
        return (M.aura(d, 130, 240, -250, 1.2) + M.figure(d, "holo") + holo + M.smoke(d, 220, -4, seed=6, key=k + "Sm"),
                (-278, -520, 284, 24))
    if num == "04":                                   # CODER — code control at the black workstation
        d.keyframes(k + "K", "0%,100%{opacity:.3}50%{opacity:1}")
        keys = "".join(f'<rect x="{n(-66 + c * 13.4 + r * 3)}" y="{n(-236 + r * 6.4)}" width="10.4" height="3.8" rx="1" fill="{P.glow}" '
                       f'style="animation:{k}K {n(1 + (c * 7 + r * 3) % 5 * .23)}s {n((c * 3 + r) % 7 * .17)}s infinite"/>'
                       for r in range(3) for c in range(10))
        board = (f'<path d="M-76-240L76-240L88-212L-88-212Z" fill="{P.glow}" opacity=".12" stroke="{P.glow}" stroke-opacity=".6"/>' + keys)
        code = (C.code_panel(d, -222, -478, 134, 74, [("def summon(model):", P.ice), ("  embed = encode(q)", P.text2),
                                                      ("  return model(embed)", P.text2)], k + "P1", 8.5)
                + C.code_panel(d, 92, -430, 128, 60, [("# flashdrop · pair()", P.muted), ("scan → pair → send", P.ice)], k + "P2", 8.5))
        return (M.aura(d, 120, 230, -250, .9) + code + M.figure(d, "coder", {"front": board}) + M.smoke(d, 220, -4, seed=7, key=k + "Sm"),
                (-230, -500, 228, 24))
    if num == "05":                                   # FLASHDROP PORTAL — file teleportation
        hx, hy = M.palm("portal", 1, 16)
        cx, cy, r = 292, -356, 44
        bg = linear(d, k + "Bm", [(0, P.ice, .9), (1, P.glow, .15)], 0, 0, 1, 0)
        files = "".join(f'<g transform="translate({n(cx + 70 * math.cos(math.radians(a)))} {n(cy + 70 * math.sin(math.radians(a)))})">'
                        f'<path d="M-9-7H-3L-1-4.5H9V7H-9Z" fill="#12091C" stroke="{P.ice}" stroke-width="1"/></g>' for a in (200, 300))
        fx = (f'<path d="M{n(hx)} {n(hy - 3)}L{cx - r + 8} {cy - 26}L{cx - r + 8} {cy + 26}L{n(hx)} {n(hy + 3)}Z" fill="{bg}" opacity=".5"/>'
              f'<circle cx="{n(hx)}" cy="{n(hy)}" r="7" fill="{P.ice}" opacity=".85" filter="url(#mvGlow)"/>' + portal(d, cx, cy, r) + files)
        return (M.aura(d, 120, 240, -250, 1.2) + M.figure(d, "portal") + fx + M.smoke(d, 220, -4, seed=3, key=k + "Sm"),
                (-170, -505, 356, 24))
    if num == "06":                                   # DATA SORCERER — data absorption
        (lx, ly), (rx, ry) = M.palm("sorcerer", -1, 12), M.palm("sorcerer", 1, 12)
        fx = (C.data_stream(d, lx, ly, rx, ry, 300, 26, k + "D1", 3) + C.data_stream(d, lx, ly, -262, -8, -40, 10, k + "D2", 4)
              + C.data_stream(d, rx, ry, 262, -8, -40, 10, k + "D3", 5))
        return (M.aura(d, 150, 250, -250, 1.3) + M.figure(d, "sorcerer") + fx + M.smoke(d, 240, -2, seed=9, key=k + "Sm"),
                (-278, -510, 278, 24))
    if num == "07":                                   # PROJECT COMMANDER — code control over the vault
        tx, ty = M.palm("commander", 1, 30)
        cx, cy = 292, -380
        d.keyframes(k + "R", "to{transform:rotate(360deg)}")
        glyph = (f'<path d="{_hex(cx, cy, 40)}" fill="#12091C" fill-opacity=".85" stroke="{P.glow}" stroke-width="1.4"/>'
                 f'<path d="{_hex(cx, cy, 31)}" fill="none" stroke="{P.ice}" stroke-width=".8" opacity=".6"/>'
                 f'<g style="transform-origin:{cx}px {cy}px;animation:{k}R 16s linear infinite"><circle cx="{cx}" cy="{cy}" r="52" fill="none" '
                 f'stroke="{P.glow}" stroke-width=".8" stroke-dasharray="3 7" opacity=".7"/></g>' + sigil("layers", cx, cy, .9, P.ice, 1.6))
        return (M.aura(d, 120, 240, -250) + M.figure(d, "commander") + _beam(d, k + "B", (tx, ty), (cx - 44, cy + 14), 30) + glyph
                + M.smoke(d, 220, -4, seed=11, key=k + "Sm"), (-170, -505, 350, 24))
    if num == "08":                                   # TIME KEEPER — time control
        px, py = M.palm("timekeeper", 1, 10)
        return (M.aura(d, 120, 240, -250) + M.figure(d, "timekeeper") + C.clock(d, px, py - 54, 30, k + "Clk")
                + M.smoke(d, 220, -4, seed=13, key=k + "Sm"), (-170, -510, 200, 24))
    if num == "09":                                   # KNOWLEDGE KEEPER — knowledge vision
        bx, by = M.palm("scholar", 1, 2)
        return (M.aura(d, 120, 240, -250, 1.1) + M.figure(d, "scholar") + C.floating_book(d, bx, by + 14, 1.35, k + "Bk")
                + M.smoke(d, 220, -4, seed=15, key=k + "Sm"), (-170, -548, 170, 24))
    if num == "10":                                   # GITHUB GUARDIAN — decorative GitHub energy grid behind him
        gx, gy = -133, -342
        grid = (f'<rect x="{gx - 10}" y="{gy - 10}" width="286" height="118" rx="8" fill="#050507" fill-opacity=".7" stroke="{P.glow}" '
                f'stroke-opacity=".45" stroke-width=".8"/>' + C.contrib_grid(d, gx, gy, 19, 7, 11, 3, k + "G", 9))
        return (grid + M.aura(d, 120, 240, -250) + M.figure(d, "guardian") + M.smoke(d, 220, -4, seed=21, key=k + "Sm"),
                (-170, -505, 170, 24))
    if num == "11":                                   # VOID WALKER — out of the fog
        d.keyframes(k + "St", "0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}")
        return (M.aura(d, 130, 250, -250, 1.2) + f'<g style="animation:{k}St 1.2s ease-in-out infinite">{M.figure(d, "walk")}</g>'
                + M.smoke(d, 240, -4, seed=14, key=k + "Sm") + _motes(d, k + "Mo", (-120, -300, 120, -20), 26, 5, 0, -60),
                (-180, -505, 180, 24))
    if num == "12":                                   # TELEPORTATION — dissolving into the void
        mid = _fade(d, k + "Fd", -80, 70, -520, 30)
        return (f'<g mask="url(#{mid})">{M.aura(d, 120, 240, -250, 1.2)}{M.symbol(d, "final", rim=True)}</g>'
                + _motes(d, k + "Mo", (-10, -470, 100, -30), 80, 12), (-170, -505, 230, 24))
    if num == "13":                                   # POWER AWAKENING — the energy bursts out of him
        return (burst(d, 0, -300, 150, k + "Bu") + M.aura(d, 130, 250, -260, 1.4) + M.figure(d, "awaken")
                + M.smoke(d, 260, -4, seed=9, key=k + "Sm"), (-240, -528, 240, 24))
    if num == "14":                                   # SILHOUETTE — only the eyes and the gem stay lit
        back = radial(d, k + "Bk", [(0, P.ice, .7), (.22, P.glow, .45), (.6, P.primary, .12), (1, P.primary, 0)])
        d.keyframes(k + "Bp", "0%,100%{opacity:.6}50%{opacity:1}")
        return (f'<ellipse cx="0" cy="-300" rx="170" ry="236" fill="{back}" style="animation:{k}Bp 8s ease-in-out infinite"/>'
                + M.figure(d, "final", silhouette=True) + M.smoke(d, 260, -4, seed=41, key=k + "Sm"), (-176, -538, 176, 24))
    if num == "15":                                   # FINAL GUARDIAN — at the castle gate
        return (M.aura(d, 130, 250, -250, 1.1) + M.symbol(d, "final", rim=True) + M.smoke(d, 240, -4, seed=31, key=k + "Sm"),
                (-170, -505, 170, 24))
    if num == "P09":                                  # POWER 09 · DIGITAL CLONES — AI / ML / LLM / DATA / DEV
        ghost = M.symbol(d, "stand")
        o = []
        for lab, side, dx in CLONE_LABELS:
            s = .78 if dx < 200 else .66
            o.append(C.clone(d, ghost, side * dx, -12, s, .42, k + "Cl"))
            t, _ = text_use(d, lab, side * dx, 10, 13, "ui6", anchor="middle", tracking=.3, fill=P.ice)
            o.append(t)
        echo = C.clone(d, ghost, -56, -4, .92, .34, k + "Cl")
        t, _ = text_use(d, "LLM", -118, -470, 13, "ui6", anchor="middle", tracking=.3, fill=P.ice)
        return ("".join(o) + echo + t + M.aura(d, 120, 240, -250, 1.1) + M.figure(d, "stand") + M.smoke(d, 300, -4, seed=17, key=k + "Sm"),
                (-330, -505, 330, 30))
    raise KeyError(num)


# ── one transparent SVG per scene ───────────────────────────────────────────────

def scene_asset(num: str) -> Doc:
    _, _, scene, power, where, _ = BY_NUM[num]
    label = "Power 09" if num == "P09" else f"Scene {num}"
    d = Doc(10, 10, f"The Midnight AI Vampire — {label}: {scene.title()}",
            f"Original character on a transparent background. {power.title().replace(' · ', ': ')}. "
            f"Used in the {where.split(' · ')[0].title()} ({where.split(' · ')[1].title()}). Not based on any real person or existing character.")
    svg, (x0, y0, x1, y1) = character(d, num, "va")
    pad = 10
    d.w, d.h = round(x1 - x0 + 2 * pad), round(y1 - y0 + 2 * pad)
    d.add(f'<g transform="translate({n(pad - x0)} {n(pad - y0)})">{svg}</g>')
    return d


# ── master character sheet ──────────────────────────────────────────────────────

def _fit(doc: Doc, text: str, x: float, y: float, size: float, font: str, max_w: float, tracking: float = 0, **kw) -> str:
    while measure(text, font, size, tracking) > max_w and size > 6:
        size -= .25
    t, _ = text_use(doc, text, x, y, size, font, tracking=tracking, **kw)
    return t


CALLOUTS_R = [("BLACK, SLIGHTLY MESSY HAIR", (5, -459)), ("DARK VIOLET GLOWING EYES", (8, -440)),
              ("SHARP JAW, HIGH CHEEKBONES", (11, -416)), ("HIGH STANDING COLLAR", (31, -420)),
              ("VIOLET GEMSTONE  ·  HIS SIGNATURE", (0, -391)), ("SILK CRAVAT + BROCADE VEST", (4, -352)),
              ("SILVER CHAIN, CLASPS + BUTTONS", (12, -331))]
CALLOUTS_L = [("SUBTLY POINTED EARS", (-21, -446)), ("PALE, MOONLIT SKIN", (-11, -426)),
              ("VIOLET MOON RIM LIGHT", (-58, -300)), ("SILVER RING", (-47, -197)),
              ("LONG BLACK GOTHIC COAT", (-44, -120)), ("VIOLET SATIN LINING", (-12, -64))]


def model_sheet() -> Doc:
    W, H = 1000, 790
    d = Doc(W, H, "The Midnight AI Vampire — master character sheet",
            "Master character sheet of the Midnight AI Vampire, the original mascot of this profile: tall, elegant, pale "
            "moonlit skin, black slightly messy hair, dark violet glowing eyes, small fangs, a long black gothic coat with a "
            "high collar, silver details and a violet gemstone at his throat. Four expressions and the black + violet palette. "
            "An original character — not based on any real person or existing character.")
    under, over = panel(d, W, H, "ms", 20, grid_on=True, glow_at=(.3, .5))
    d.add(under, '<g clip-path="url(#msClip)">')
    tb, _ = title_bar(d, 48, 52, "", "", "THE MIDNIGHT AI VAMPIRE", 32, key="msTb", kicker="// MASTER CHARACTER SHEET  •  ORIGINAL CHARACTER")
    sub = _fit(d, "Drawn for this profile — not based on any real person or existing character. One design, every chamber.",
               48, 134, 14, "ui5", 900, fill=P.text2)
    d.add(tb, sub)
    # the master figure, lit from behind by the moon
    fx, fy, s = 300, 740, 1.12
    moon = radial(d, "msMoon", [(0, P.ice, .28), (.3, P.glow, .14), (1, P.glow, 0)])
    d.add(f'<circle cx="{fx - 30}" cy="330" r="250" fill="{moon}"/>',
          f'<ellipse cx="{fx}" cy="{fy + 4}" rx="120" ry="10" fill="#000" opacity=".6"/>',
          f'<g transform="translate({fx} {fy}) scale({s})">{M.aura(d, 130, 250, -250)}{M.figure(d, "stand")}</g>')
    # callouts
    def world(p):
        return fx + p[0] * s, fy + p[1] * s
    o = []
    for side, items, lx in ((1, CALLOUTS_R, 404), (-1, CALLOUTS_L, 196)):
        pts = [world(p) for _, p in items]
        if side > 0:
            ys = [182 + i * 36 for i in range(len(items))]
        else:                                            # left labels sit level with their points, never closer than 30px
            ys, prev = [], -1e9
            for _, py in pts:
                prev = max(prev + 30, py)
                ys.append(prev)
        for (label, _), (px, py), ly in zip(items, pts, ys):
            o.append(f'<path d="M{n(px)} {n(py)}L{n(lx - side * 18)} {n(ly - 4)}H{n(lx - side * 6)}" fill="none" stroke="{P.ice}" '
                     f'stroke-width=".8" opacity=".75"/><circle cx="{n(px)}" cy="{n(py)}" r="2.6" fill="{P.bg0}" stroke="{P.ice}" stroke-width="1.1"/>')
            o.append(_fit(d, label, lx, ly, 10, "ui6", 196 if side > 0 else lx - 30, .2,
                          anchor="start" if side > 0 else "end", fill=P.text))
    d.add("".join(o))
    note = _fit(d, "TALL, ELEGANT BUILD  ·  ~8 HEADS", fx, fy + 30, 9.5, "ui6", 300, .26, anchor="middle", fill=P.muted)
    d.add(note)
    # expressions
    x0, y0 = 632, 176
    lab, _ = text_use(d, "EXPRESSIONS", x0, y0, 10.5, "ui6", tracking=.32, fill=P.ice)
    d.add(lab, f'<rect x="{x0}" y="{y0 + 8}" width="326" height="1" fill="{P.line2}"/>')
    backdrop = radial(d, "msHd", [(0, "#241137", .9), (.7, "#12091C", .6), (1, "#050507", 0)])
    for i, (expr, glow, name) in enumerate((("calm", 1.0, "CALM"), ("smirk", 1.0, "SMIRK"), ("fangs", 1.6, "FANGS"), ("intense", 1.4, "INTENSE"))):
        cx, cy = x0 + 80 + (i % 2) * 168, y0 + 110 + (i // 2) * 196
        head = M.head_ref(d, expr, glow)
        d.add(f'<circle cx="{cx}" cy="{cy - 26}" r="74" fill="{backdrop}"/>'
              f'<g transform="translate({cx} {cy + 22}) scale(1.75)"><g filter="{M.rim_filter(d, 1.75)}">{head}</g></g>')
        t, _ = text_use(d, name, cx, cy + 70, 10, "ui6", anchor="middle", tracking=.3, fill=P.text)
        d.add(t)
    # palette
    py0 = 600
    lab, _ = text_use(d, "PALETTE  ·  BLACK + VIOLET ONLY", x0, py0, 10.5, "ui6", tracking=.32, fill=P.ice)
    d.add(lab, f'<rect x="{x0}" y="{py0 + 8}" width="326" height="1" fill="{P.line2}"/>')
    sw = [P.bg0, P.bg1, P.bg3, P.bg4, P.navy2, P.accent, P.primary, P.glow, P.ice, P.text]
    for i, c in enumerate(sw):
        x, y = x0 + (i % 5) * 66, py0 + 22 + (i // 5) * 62
        t, _ = text_use(d, c.upper(), x + 28, y + 50, 8.5, "mono", anchor="middle", fill=P.text2)
        d.add(f'<rect x="{x}" y="{y}" width="56" height="34" rx="6" fill="{c}" stroke="{P.glow}" stroke-opacity=".35" stroke-width=".8"/>', t)
    d.add("</g>", over)
    return d


# ── the scene roster: the same vampire in all 15 scenes (+ the clones) ─────────

def roster() -> Doc:
    cols, cw, ch = 4, 230, 292
    W = 40 + cols * cw
    H = 150 + math.ceil(len(SCENES) / cols) * ch + 24
    d = Doc(W, H, "The Midnight AI Vampire — scene roster",
            "The same original vampire in all fifteen scenes of the profile, each with the power of its chamber: "
            + "; ".join(f"{('Power 09' if a == 'P09' else 'scene ' + a)} {c.title()} ({e.split(' · ')[1].title()})" for a, _, c, _, e, _ in SCENES) + ".")
    under, over = panel(d, W, H, "rs", 20, grid_on=False, glow_at=(.5, .1))
    d.add(under, '<g clip-path="url(#rsClip)">')
    tb, _ = title_bar(d, W / 2, 52, "", "", "ONE CHARACTER  ·  FIFTEEN SCENES", 30, anchor="middle", key="rsTb",
                      kicker="// SCENE ROSTER  •  THE SAME VAMPIRE IN EVERY CHAMBER")
    d.add(tb)
    cell_bg = linear(d, "rsCell", [(0, "#12091C", .85), (1, "#050507", .9)], 0, 0, 0, 1)
    halo = radial(d, "rsHalo", [(0, "#3A126D", .5), (1, "#020203", 0)])
    for i, (num, _, scene, power, where, _) in enumerate(SCENES):
        x, y = 20 + (i % cols) * cw, 138 + (i // cols) * ch
        d.add(f'<rect x="{x + 6}" y="{y + 6}" width="{cw - 12}" height="{ch - 12}" rx="12" fill="{cell_bg}" stroke="{P.glow}" '
              f'stroke-opacity=".28" stroke-width=".8"/>', f'<ellipse cx="{x + cw / 2}" cy="{y + 120}" rx="100" ry="110" fill="{halo}"/>')
        svg, (bx0, by0, bx1, by1) = character(d, num, f"r{i}")
        base = y + ch - 70
        sc = min(.44, (cw - 22) / (bx1 - bx0), (base - y - 16) / (-by0))
        cx = x + cw / 2 - sc * (bx0 + bx1) / 2
        cid = f"rsC{i}"
        d.defs(cid, f'<clipPath id="{cid}"><rect x="{x + 6}" y="{y + 6}" width="{cw - 12}" height="{ch - 12}" rx="12"/></clipPath>')
        d.add(f'<g clip-path="url(#{cid})"><g transform="translate({n(cx)} {n(base)}) scale({n(sc, 3)})">{svg}</g></g>')
        tag, _ = text_use(d, num, x + 20, y + 32, 15, "cinzel9", fill=P.glow, tracking=.04)
        d.add(tag)
        d.add(_fit(d, scene, x + cw / 2, base + 22, 11, "ui6", cw - 28, .2, anchor="middle", fill=P.text),
              _fit(d, power, x + cw / 2, base + 38, 8.6, "ui6", cw - 28, .16, anchor="middle", fill=P.ice),
              _fit(d, where, x + cw / 2, base + 53, 8.6, "ui5", cw - 28, .06, anchor="middle", fill=P.muted))
    d.add("</g>", over)
    return d
