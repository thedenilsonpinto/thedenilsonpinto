"""Remaining chambers of the Midnight AI Lab.

Scene 13 Power Awakening (prologue) · Scene 11 Void Walker + Scene 12 Teleportation (transitions)
Scene 04 Coder (midnight terminal) · Scene 15 Final Guardian (castle gate / contact)
Scene 14 Silhouette (dark exit / footer). Same original vampire (mascot.py) in every one.
"""
from __future__ import annotations

import math
import random

from . import chamber as C
from . import elements as el
from . import mascot as M
from .backdrop import image
from .core import Doc, glow_filter, linear, n, radial
from .data import TERMINAL, title_case
from .hud import panel, title_bar
from .midnight import glass, icon
from .ornament import diamond
from .palette import P
from .text import measure, text_path, text_use, wrap

CHAMBERS = ["SHADOW CHAMBER", "AI LABORATORY", "PORTAL CHAMBER", "COMMAND ROOM", "DATA CHAMBER", "TIME CHAMBER",
            "ANCIENT LIBRARY", "DIGITAL OBSERVATORY", "CODE CRYPT", "CASTLE GATE"]


def burst(doc: Doc, x: float, y: float, r: float = 150, key: str = "bu", seed: int = 3) -> str:
    """Violet energy exploding softly outward: bloom, shockwave rings, rays, rising motes."""
    rnd = random.Random(seed)
    bloom = radial(doc, key + "B", [(0, P.ice, .8), (.2, P.glow, .5), (.55, P.primary, .2), (1, P.primary, 0)])
    doc.keyframes(key + "W", "0%{transform:scale(.25);opacity:.9}100%{transform:scale(1.35);opacity:0}")
    doc.keyframes(key + "R", "to{transform:rotate(360deg)}")
    doc.keyframes(key + "M", "0%{transform:translate(0,0);opacity:0}20%{opacity:1}100%{transform:translate(var(--dx),-120px);opacity:0}")
    rays = "".join(f'<path d="M{n(x)} {n(y)}L{n(x + r * 1.3 * math.cos(math.radians(a - 1.4)))} {n(y + r * 1.3 * math.sin(math.radians(a - 1.4)))}'
                   f'L{n(x + r * 1.3 * math.cos(math.radians(a + 1.4)))} {n(y + r * 1.3 * math.sin(math.radians(a + 1.4)))}Z"/>'
                   for a in range(0, 360, 15))
    rings = "".join(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="none" stroke="{P.glow}" stroke-width="1.4" '
                    f'style="transform-box:fill-box;transform-origin:center;animation:{key}W 4.8s ease-out {k * 1.6:.1f}s infinite;opacity:0"/>'
                    for k in range(3))
    motes = "".join(f'<circle cx="{n(x + rnd.uniform(-r, r) * .8)}" cy="{n(y + rnd.uniform(-r, r) * .6)}" r="{n(rnd.uniform(.8, 2.2))}" '
                    f'fill="{rnd.choice([P.ice, P.glow, "#FFFFFF"])}" style="--dx:{n(rnd.uniform(-30, 30))}px;'
                    f'animation:{key}M {n(rnd.uniform(3, 6))}s ease-out {n(-rnd.uniform(0, 6))}s infinite"/>' for _ in range(26))
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r * 1.5)}" fill="{bloom}"/>'
            f'<g fill="{P.ice}" opacity=".16" style="transform-origin:{n(x)}px {n(y)}px;animation:{key}R 60s linear infinite">{rays}</g>'
            + rings + motes)


# ── PROLOGUE · Scene 13 "Power Awakening" ──────────────────────────────────────

def awakening() -> Doc:
    W, H = 1000, 360
    d = Doc(W, H, "Prologue — the guardian awakens",
            "Prologue of the Midnight AI Lab: an original vampire guardian awakens in the great hall, violet energy "
            "bursting around him. Chambers ahead: " + ", ".join(c.title() for c in CHAMBERS) + ".")
    under, over = panel(d, W, H, "aw", 20, grid_on=False, glow_at=(.22, .5))
    d.add(under, '<g clip-path="url(#awClip)">')
    d.add(C.chamber(d, W, H, "awC", windows=[(92, 36, 128, 270, C.VIEW_TOWERS), (300, 36, 128, 270, C.VIEW_MOON)],
                    floor_y=318, pillars=(40, 262, 470), fog=False))
    ax, ay, sc = 262, 334, .6
    d.add(f'<g transform="translate({ax} {ay}) scale({sc})">{burst(d, 0, -300, 190, "awB")}'
          f'{M.aura(d, 130, 250, -260, 1.4)}{M.figure(d, "awaken")}{M.smoke(d, 320, -4, seed=9, key="awSm")}</g>')
    d.add(el.fog(d, W, H - 24, 50, seed=33, dur=50, opacity=.16, color="#9C7FD6", name="awFog"), C.vignette(d, W, H, "awV", .5))
    x0 = 520
    tb, y = title_bar(d, x0, 56, "", "", "THE MIDNIGHT AI LAB", 32, key="awTb", kicker="// PROLOGUE  •  POWER AWAKENING")
    d.add(tb)
    body = ("An original guardian keeps this castle. Every chamber below holds a part of my work — "
            "AI, data and software, built after dark.")
    for i, ln in enumerate(wrap(body, "ui5", 14.5, 440)):
        t, _ = text_use(d, ln, x0, y + 38 + i * 22, 14.5, "ui5", fill=P.text2)
        d.add(t)
    cy = y + 38 + 3 * 22 + 8
    lab, _ = text_use(d, "CHAMBERS AHEAD", x0, cy, 10.5, "ui6", tracking=.32, fill=P.ice)
    d.add(lab)
    bx, by = x0, cy + 14
    for i, name in enumerate(CHAMBERS):
        w = measure(name, "ui6", 9.5, .2) + 24
        if bx + w > x0 + 446:
            bx, by = x0, by + 30
        t, _ = text_use(d, name, bx + 12, by + 15.5, 9.5, "ui6", tracking=.2, fill=P.text)
        d.add(f'<rect x="{n(bx)}" y="{n(by)}" width="{n(w)}" height="22" rx="11" fill="#12091C" stroke="{P.glow}" '
              f'stroke-opacity=".45" stroke-width=".8"/>', t)
        bx += w + 6
    d.add("</g>", over)
    return d


# ── TRANSITIONS · Scene 11 "Void Walker" + Scene 12 "Teleportation" ────────────

def corridor(doc: Doc, W: float, H: float, vx: float, vy: float, key: str = "co") -> str:
    """One-point-perspective castle corridor: receding pointed arches, floor lines, violet fog at the end."""
    o = [f'<rect width="{n(W)}" height="{n(H)}" fill="#050507"/>']
    far = radial(doc, key + "F", [(0, P.ice, .55), (.18, P.glow, .35), (.55, P.primary, .10), (1, P.primary, 0)])
    o.append(f'<ellipse cx="{n(vx)}" cy="{n(vy)}" rx="{n(W * .32)}" ry="{n(H * .8)}" fill="{far}"/>')
    for k in range(7, 0, -1):
        t = k / 7
        w, h = 60 + (W * .95 - 60) * t ** 1.6, 44 + (H * 1.35 - 44) * t ** 1.6
        x, y = vx - w / 2, vy + h * .26 - h * .74
        ap = C.arch_path(x, y, w, h)
        op = .25 + .75 * t
        o.append(f'<path d="{ap}" fill="none" stroke="#12091C" stroke-width="{n(4 + 22 * t ** 2)}" opacity="{n(op, 2)}"/>'
                 f'<path d="{ap}" fill="none" stroke="{P.glow}" stroke-width="{n(.5 + t)}" opacity="{n(.12 + .3 * (1 - t), 2)}"/>')
    fl = linear(doc, key + "L", [(0, "#12091C", 0), (1, "#020203", .95)], 0, 0, 0, 1)
    o.append(f'<path d="M0 {n(H)}L{n(vx - 30)} {n(vy + 40)}L{n(vx + 30)} {n(vy + 40)}L{n(W)} {n(H)}Z" fill="{fl}"/>')
    o.append("".join(f'<path d="M{n(vx + (i - 4) * 8)} {n(vy + 40)}L{n(vx + (i - 4) * 160)} {n(H)}" stroke="{P.glow}" stroke-width=".5" opacity=".12"/>'
                     for i in range(9)))
    return "".join(o)


def void_walker(next_label: str = "THE PORTAL CHAMBER") -> Doc:
    W, H = 1000, 230
    d = Doc(W, H, "Passage — the void walker", f"Transition: the vampire walks out of the violet fog along a castle corridor toward {next_label.title()}.")
    d.defs("vwClip", f'<clipPath id="vwClip"><rect width="{W}" height="{H}" rx="18"/></clipPath>')
    d.add(f'<g clip-path="url(#vwClip)">', corridor(d, W, H, 560, 96, "vw"))
    d.add(el.fog(d, W, 150, 70, seed=4, dur=36, opacity=.22, color="#9C7FD6", name="vwFogA"))
    d.keyframes("vwStep", "0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}")
    d.add(f'<g transform="translate(560 214) scale(.36)"><g style="animation:vwStep 1.2s ease-in-out infinite">'
          f'{M.aura(d, 130, 250, -250, 1.2)}{M.figure(d, "walk")}</g>{M.smoke(d, 320, -4, seed=14, key="vwSm")}</g>')
    d.add(el.fog(d, W, 210, 50, seed=5, dur=26, opacity=.2, color="#6D4FB0", name="vwFogB"), C.vignette(d, W, H, "vwV", .7))
    k, _ = text_use(d, "// PASSAGE  •  VOID WALKER", 44, 44, 10.5, "ui6", tracking=.32, fill=P.ice)
    t, _ = text_use(d, f"TO {next_label}", 44, 68, 15, "ui6", tracking=.22, fill=P.text)
    d.add(k, t, diamond(34, 40.5, 3.4, P.glow), "</g>")
    d.add(f'<rect x=".6" y=".6" width="{W - 1.2}" height="{H - 1.2}" rx="17.5" fill="none" stroke="{P.glow}" stroke-opacity=".35"/>')
    return d


def teleport(next_label: str = "THE TIME CHAMBER") -> Doc:
    W, H = 1000, 230
    d = Doc(W, H, "Passage — void teleportation",
            f"Transition: the vampire dissolves into black-violet particles and reappears further on, toward {next_label.title()}.")
    d.defs("tpClip", f'<clipPath id="tpClip"><rect width="{W}" height="{H}" rx="18"/></clipPath>')
    bg = radial(d, "tpBg", [(0, "#1A0D26"), (.6, "#07050B"), (1, "#020203")], .5, .6, .8)
    d.add(f'<g clip-path="url(#tpClip)"><rect width="{W}" height="{H}" fill="{bg}"/>',
          el.stars(d, W, H * .7, 40, seed=61, avoid=[(24, 24, 330, 90)]))
    # departure: the figure dissolves to the right
    fx, fy, sc = 360, 222, .4
    mid, parts = C.dissolve(d, W, H, fx - 110, fx + 60, "tpD")
    fig = M.symbol(d, "final", rim=True)
    d.add(f'<g mask="url(#{mid})"><g transform="translate({fx} {fy}) scale({sc})">{M.aura(d, 120, 240, -250, 1.2)}{fig}</g></g>', parts)
    # the particle stream crossing the void
    d.defs("tpPath", f'<path id="tpPath" d="M{fx + 40} 130Q{(fx + 700) / 2} 40 700 128"/>')
    rnd = random.Random(8)
    d.add("".join(f'<circle r="{n(rnd.uniform(.8, 2.4))}" fill="{rnd.choice([P.glow, P.ice, P.primary])}">'
                  f'<animateMotion dur="{n(rnd.uniform(2.2, 3.6), 2)}s" begin="{n(-rnd.uniform(0, 3.6), 2)}s" repeatCount="indefinite">'
                  f'<mpath href="#tpPath"/></animateMotion></circle>' for _ in range(40)))
    # arrival: a translucent copy re-forming
    d.keyframes("tpForm", "0%,100%{opacity:.18}50%{opacity:.5}")
    d.add(f'<g style="animation:tpForm 4s ease-in-out infinite">'
          + C.clone(d, fig, 720, fy, sc, .55, "tpC") + "</g>")
    d.add(el.fog(d, W, H - 10, 50, seed=8, dur=30, opacity=.18, color="#6D4FB0", name="tpFog"), C.vignette(d, W, H, "tpV", .6))
    k, _ = text_use(d, "// PASSAGE  •  VOID TELEPORTATION", 44, 44, 10.5, "ui6", tracking=.32, fill=P.ice)
    t, _ = text_use(d, f"TO {next_label}", 44, 68, 15, "ui6", tracking=.22, fill=P.text)
    d.add(k, t, diamond(34, 40.5, 3.4, P.glow), "</g>")
    d.add(f'<rect x=".6" y=".6" width="{W - 1.2}" height="{H - 1.2}" rx="17.5" fill="none" stroke="{P.glow}" stroke-opacity=".35"/>')
    return d


# ── CHAMBER 10 · THE CODE CRYPT — Scene 04 "Coder" + the midnight terminal ─────

def _vis(t_on: float, T: float) -> str:
    """SMIL: hidden until t_on, visible until the loop resets. Without SMIL it simply stays visible."""
    return (f'<animate attributeName="opacity" dur="{n(T, 2)}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{t_on / T:.4f};{(T - .25) / T:.4f}" values="0;1;0"/>')


def terminal(user: str = "denilson", host: str = "midnight-lab") -> Doc:
    W, H = 1000, 480
    lines = TERMINAL
    d = Doc(W, H, "The Code Crypt — midnight terminal",
            f"A terminal session on {host}: " + "; ".join(f"{cmd} → {' '.join(out)}" for cmd, out in lines)
            + ". Scene: the vampire codes at a black workstation, floating code windows lit violet around him.")
    under, over = panel(d, W, H, "tm", 20, grid_on=False, glow_at=(.78, .45))
    d.add(under, '<g clip-path="url(#tmClip)">')
    d.add(C.chamber(d, W, H, "tmC", windows=[(716, 30, 150, 300, C.VIEW_TOWERS)], floor_y=430, pillars=(640, 968), fog=False))
    # the workstation: high-backed chair, the coder, floating code, a black desk
    cx = 792
    chair = linear(d, "tmChair", [(0, "#1A0D26"), (1, "#050507")], 0, 0, 1, 0)
    d.add(f'<path d="M{cx - 58} 360L{cx - 58} 176Q{cx - 58} 118 {cx} 96Q{cx + 58} 118 {cx + 58} 176L{cx + 58} 360Z" fill="{chair}" '
          f'stroke="{P.glow}" stroke-opacity=".35"/>'
          f'<path d="M{cx} 96L{cx} 84" stroke="{P.glow}" stroke-width="1.4" opacity=".6"/>')
    code = [("def summon(model):", P.ice), ("  embed = encode(q)", P.text2), ("  return model(embed)", P.text2)]
    code2 = [("# flashdrop · pair()", P.muted), ("scan → pair → send", P.ice)]
    d.add(C.code_panel(d, 640, 140, 132, 74, code, "tmP1", 8.5), C.code_panel(d, 846, 214, 124, 58, code2, "tmP2", 8.5))
    screen = radial(d, "tmScreen", [(0, P.glow, .35), (1, P.glow, 0)])
    d.add(f'<ellipse cx="{cx}" cy="330" rx="120" ry="60" fill="{screen}"/>')
    d.add(f'<g transform="translate({cx} 610) scale(.78)">{M.aura(d, 120, 230, -250, .9)}{M.figure(d, "coder")}</g>')
    desk = linear(d, "tmDesk", [(0, "#12091C"), (1, "#020203")], 0, 0, 0, 1)
    d.keyframes("tmKey", "0%,100%{opacity:.3}50%{opacity:1}")
    keys = "".join(f'<rect x="{n(cx - 70 + c * 14 + r * 4)}" y="{n(378 + r * 7)}" width="11" height="4.2" rx="1" fill="{P.glow}" '
                   f'style="animation:tmKey {n(1 + (c * 7 + r * 3) % 5 * .23)}s {n((c * 3 + r) % 7 * .17)}s infinite"/>'
                   for r in range(3) for c in range(10))
    d.add(f'<path d="M{cx - 88} 372L{cx + 88} 372L{cx + 100} 400L{cx - 100} 400Z" fill="{P.glow}" opacity=".10" stroke="{P.glow}" stroke-opacity=".6"/>',
          keys,
          f'<path d="M{cx - 170} 398H{cx + 190}L{cx + 210} 480H{cx - 190}Z" fill="{desk}"/>'
          f'<path d="M{cx - 170} 398H{cx + 190}" stroke="{P.glow}" stroke-width="1.2" opacity=".7"/>')
    # title + the terminal session
    tb, _ = title_bar(d, 56, 54, "", "", "MIDNIGHT TERMINAL", 32, key="tmTb", kicker="// CHAMBER 10  •  THE CODE CRYPT")
    d.add(tb)
    tx, ty, tw, th = 56, 128, 560, 316
    tg = linear(d, "tmWin", [(0, "#12091C", .96), (1, "#050507", .96)], 0, 0, 0, 1)
    ttl, _ = text_use(d, f"{user}@{host}: ~", tx + tw / 2, ty + 20, 11, "mono", anchor="middle", fill=P.text2)
    d.add(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{tg}" stroke="{P.glow}" stroke-opacity=".6" stroke-width="1"/>'
          f'<path d="M{tx} {ty + 32}H{tx + tw}" stroke="{P.line2}"/>'
          + "".join(f'<circle cx="{tx + 20 + i * 16}" cy="{ty + 16}" r="5" fill="{c}"/>' for i, c in enumerate((P.glow, P.primary, P.dim)))
          + ttl)
    size, lh = 14, 21
    cw = measure("M", "mono", size)
    prompt = f"{user}@{host}"
    T, t, y = 17.0, .6, ty + 60
    body = []
    for cmd, out in lines + [("", [])]:
        p1, w1 = text_use(d, prompt, tx + 20, y, size, "mono", fill=P.glow)
        p2, w2 = text_use(d, ":~$", tx + 20 + w1, y, size, "mono", fill=P.text2)
        body.append(f'<g>{p1}{p2}{_vis(t, T)}</g>')
        cx0 = tx + 20 + w1 + w2 + cw
        if not cmd:
            d.keyframes("tmBlink", "0%,49%{opacity:1}50%,100%{opacity:0}")
            body.append(f'<g><rect x="{n(cx0)}" y="{n(y - size * .8)}" width="{n(cw * .9)}" height="{n(size * 1.05)}" fill="{P.glow}" '
                        f'style="animation:tmBlink 1s steps(1) infinite"/>{_vis(t, T)}</g>')
            break
        c_t, _ = text_use(d, cmd, cx0, y, size, "mono", fill=P.text)
        step = .085
        times = [0.0] + [(t + .25 + k * step) / T for k in range(len(cmd) + 1)] + [(T - .25) / T]
        vals = ["0"] + [n(k * cw + (2 if k else 0)) for k in range(len(cmd) + 1)] + ["0"]
        cid = d.uid("tmCl")
        d.defs(cid, f'<clipPath id="{cid}"><rect x="{n(cx0 - 1)}" y="{n(y - size)}" height="{n(size * 1.4)}" width="{vals[-2]}">'
                    f'<animate attributeName="width" dur="{n(T, 2)}s" repeatCount="indefinite" calcMode="discrete" '
                    f'keyTimes="{";".join(f"{v:.4f}" for v in times)}" values="{";".join(vals)}"/></rect></clipPath>')
        body.append(f'<g clip-path="url(#{cid})">{c_t}</g>')
        t_out = t + .25 + len(cmd) * step + .35
        y += lh
        for o_ in out:
            ot, _ = text_use(d, o_, tx + 20, y, size, "mono", fill=P.ice)
            body.append(f'<g>{ot}{_vis(t_out, T)}</g>')
            y += lh
        t = t_out + .9
    d.add("".join(body))
    d.add(C.vignette(d, W, H, "tmV", .35), "</g>", over)
    return d


# ── CHAMBER 11 · THE CASTLE GATE — Scene 15 "Final Guardian" (contact) ─────────

def contact(user: str, linkedin: str, email: str) -> Doc:
    W, H = 1000, 470
    li = linkedin.rstrip("/").split("linkedin.com/")[-1]
    rows = [("github", "GITHUB", f"github.com/{user}")] + ([("sigil:network", "LINKEDIN", f"linkedin.com/{li}")] if linkedin else []) \
        + ([("sigil:mail", "EMAIL", email)] if email else [])
    names = {"GITHUB": "GitHub", "LINKEDIN": "LinkedIn", "EMAIL": "Email"}
    d = Doc(W, H, "The Castle Gate — contact",
            "Contact channels: " + "; ".join(f"{names[a]}: {b}" for _, a, b in rows) + ". Use the buttons below to open them. "
            "Scene: the vampire guards a massive gothic doorway, black fog rolling out beneath a violet moon.")
    under, over = panel(d, W, H, "ct", 20, grid_on=False, glow_at=(.25, .4))
    d.add(under, '<g clip-path="url(#ctClip)">')
    d.add(C.chamber(d, W, H, "ctC", floor_y=428, fog=False))
    # the massive doorway, the painted gate and path beyond it
    gx, gy, gw, gh = 70, 34, 330, 400
    ap = C.arch_path(gx, gy, gw, gh)
    d.defs("ctDoor", f'<clipPath id="ctDoor"><path d="{ap}"/></clipPath>')
    moon = radial(d, "ctMoon", [(0, P.ice, .5), (.3, P.glow, .2), (1, P.glow, 0)])
    d.add(f'<g clip-path="url(#ctDoor)">{image(d, "port", gx, gy, gw, gh, box=(160, 380, 880, 1300), px=1.2, key="ctGate", bright=.85)}'
          f'<circle cx="{gx + gw * .5}" cy="{gy + 70}" r="160" fill="{moon}"/>'
          f'{el.fog(d, gw * 2, gy + gh - 40, 90, seed=19, dur=44, opacity=.3, color="#9C7FD6", name="ctFogIn")}</g>')
    stone = linear(d, "ctStone", [(0, "#1A0D26"), (1, "#07050B")], 0, 0, 1, 0)
    d.add(f'<path d="{ap}" fill="none" stroke="{stone}" stroke-width="26"/>'
          f'<path d="{ap}" fill="none" stroke="#050309" stroke-width="10" transform="translate(0 0)"/>'
          f'<path d="{ap}" fill="none" stroke="{P.glow}" stroke-width="1.2" opacity=".6"/>'
          f'<path d="{C.arch_path(gx + 16, gy + 16, gw - 32, gh - 16)}" fill="none" stroke="{P.glow}" stroke-width=".6" opacity=".3"/>')
    # the guardian in the doorway, facing you
    ax, ay, sc = gx + gw / 2, 452, .78
    d.add(f'<g transform="translate({ax} {ay}) scale({sc})">{M.aura(d, 130, 250, -250, 1.1)}{M.figure(d, "final")}'
          f'{M.smoke(d, 360, -4, seed=31, key="ctSm")}</g>')
    d.add(el.fog(d, W, H - 30, 70, seed=37, dur=48, opacity=.2, color="#9C7FD6", name="ctFog"), C.vignette(d, W, H, "ctV", .45))
    # channels
    x0 = 452
    tb, _ = title_bar(d, x0, 56, "", "", "TRANSMISSION", 34, key="ctTb", kicker="// CHAMBER 11  •  THE CASTLE GATE")
    sub, _ = text_use(d, "The gate is open — reach me on any channel below.", x0, 146, 15, "ui5", fill=P.text2)
    d.add(tb, sub)
    d.keyframes("ctBar", "0%,100%{opacity:.3}50%{opacity:1}")
    for i, (ic, lab, val) in enumerate(rows):
        y = 178 + i * 76
        lt, _ = text_use(d, lab, x0 + 74, y + 26, 10.5, "ui6", tracking=.3, fill=P.ice)
        vs = 17
        while measure(val, "ui5", vs) > 330 and vs > 12:
            vs -= .5
        vt, _ = text_use(d, val, x0 + 74, y + 48, vs, "ui5", fill=P.text)
        ok, _ = text_use(d, "OPEN", x0 + 440, y + 38, 10, "ui6", anchor="end", tracking=.3, fill=P.text2)
        bars = "".join(f'<rect x="{x0 + 448 + k * 7}" y="{y + 40 - 6 - k * 5}" width="4" height="{6 + k * 5}" rx="1.5" fill="{P.glow}" '
                       f'style="animation:ctBar 1.6s {k * .2 + i * .3:.1f}s infinite"/>' for k in range(4))
        d.add(glass(d, x0, y, 500, 62, f"ctG{i}"),
              f'<circle cx="{x0 + 36}" cy="{y + 31}" r="20" fill="#12091C" stroke="{P.glow}" stroke-opacity=".7"/>'
              + icon(ic, x0 + 36, y + 31, 18, P.ice) + lt + vt + ok + bars)
    d.add("</g>", over)
    return d


# ── THE DARK EXIT — Scene 14 "Silhouette" (footer) ────────────────────────────

def footer(name: str = "DENILSON PINTO B", title: str = "AI ENGINEER",
           closing: str = "AI, data and intelligent applications — built after dark.") -> Doc:
    W, H = 1000, 360
    d = Doc(W, H, "The dark exit", f"{name} — {title_case(title)}. {closing} The vampire's silhouette waits in the fog: "
            "only his violet eyes, the rim of moonlight and the gemstone at his throat still glow.")
    d.defs("ftClip", f'<clipPath id="ftClip"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    d.add(f'<g clip-path="url(#ftClip)"><rect width="{W}" height="{H}" fill="#020203"/>')
    d.add(image(d, "land", 0, 0, W, H, box=(168, 0, 1497, 760), px=1, key="ftBg", mirror=True, bright=.32, blur=1.2))
    shade = radial(d, "ftShade", [(0, "#020203", .1), (.7, "#020203", .75), (1, "#020203", .95)], .5, .55, .7)
    d.add(f'<rect width="{W}" height="{H}" fill="{shade}"/>')
    moon = radial(d, "ftMoon", [(0, P.ice, .45), (.25, P.glow, .2), (1, P.glow, 0)])
    d.keyframes("ftMoonK", "0%,100%{opacity:.6}50%{opacity:1}")
    back = radial(d, "ftBack", [(0, P.ice, .7), (.22, P.glow, .45), (.6, P.primary, .12), (1, P.primary, 0)])
    d.add(f'<circle cx="500" cy="212" r="170" fill="{moon}" style="animation:ftMoonK 8s ease-in-out infinite"/>',
          f'<ellipse cx="500" cy="262" rx="120" ry="110" fill="{back}" style="animation:ftMoonK 8s ease-in-out infinite"/>',
          el.bat_swarm(d, W, 150, 300, 6, seed=21, name="ftB", scale=(.3, .7)))
    d.add(f'<g transform="translate(500 {H - 26}) scale(.44)">{M.figure(d, "final", silhouette=True)}'
          f'{M.smoke(d, 420, -4, seed=41, key="ftSm")}</g>')
    d.add(el.fog(d, W, H - 40, 90, seed=51, dur=40, opacity=.26, color="#9C7FD6", name="ftFogA"),
          el.fog(d, W, H - 8, 70, seed=52, dur=26, opacity=.2, color="#6D4FB0", name="ftFogB"))
    k, _ = text_use(d, "// THE DARK EXIT  •  SESSION CLOSED", W / 2, 44, 11, "ui6", anchor="middle", tracking=.34, fill=P.ice)
    tp, _ = text_path("UNTIL THE NEXT MIDNIGHT", W / 2, 90, 32, "cinzel9", anchor="middle", tracking=.08)
    dd = tp[len('<path d="'):-3]
    ice = linear(d, "ftIce", [(0, "#FFFFFF"), (.6, "#EDE7FF"), (1, P.ice)], 0, 66, 0, 90, units="userSpaceOnUse")
    d.defs("ftBlur", '<filter id="ftBlur" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>')
    nm, _ = text_use(d, f"{name}  •  {title}", W / 2, 118, 12, "ui6", anchor="middle", tracking=.34, fill=P.text)
    cl, _ = text_use(d, closing, W / 2, 140, 14, "serif_i", anchor="middle", fill=P.text2)
    d.add(k, f'<path d="{dd}" fill="{P.primary}" opacity=".7" filter="url(#ftBlur)"/><path d="{dd}" fill="{ice}"/>', nm, cl)
    left, _ = text_use(d, "THE MIDNIGHT AI LAB", 44, H - 26, 9.5, "ui6", tracking=.28, fill=P.muted)
    right, _ = text_use(d, "THE GUARDIAN IS WATCHING", W - 44, H - 26, 9.5, "ui6", anchor="end", tracking=.28, fill=P.muted)
    d.add(left, right, "</g>")
    d.add(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="19.5" fill="none" stroke="{P.glow}" stroke-opacity=".45"/>')
    return d
