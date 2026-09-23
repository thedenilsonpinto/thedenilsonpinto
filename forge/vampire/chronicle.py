"""Chambers 06–08: the Time Chamber (experience), the Ancient Library (education), Credentials.

Resume facts only — no invented responsibilities, metrics, grades or issuers.
"""
from __future__ import annotations

import math

from . import chamber as C
from . import elements as el
from . import mascot as M
from .core import Doc, glow_filter, linear, n, radial
from .data import CERTIFICATIONS, EDUCATION, EXPERIENCE, ISSUERS
from .hud import panel, status_pill, title_bar
from .ornament import diamond
from .palette import P
from .sigils import sigil
from .text import measure, text_path, text_use, wrap


def alive(doc: Doc, svg: str) -> str:
    """Subtle breathing loop around the feet (0,0) for a posed figure."""
    doc.keyframes("brth", "0%,100%{transform:scale(1,1)}50%{transform:scale(1.004,1.01)}")
    return f'<g style="animation:brth 5s ease-in-out infinite">{svg}</g>'


def ice_title(doc: Doc, text: str, x: float, y: float, size: float, key: str, font: str = "cinzel9",
              anchor: str = "start", tracking: float = .05) -> tuple[str, float]:
    tp, w = text_path(text, x, y, size, font, anchor=anchor, tracking=tracking)
    d = tp[len('<path d="'):-3]
    ice = linear(doc, key, [(0, "#FFFFFF"), (.6, "#E7D8FD"), (1, "#CDB4F3")], 0, y - size * .75, 0, y, units="userSpaceOnUse")
    doc.defs("itBlur", '<filter id="itBlur" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>')
    return f'<path d="{d}" fill="{P.primary}" opacity=".45" filter="url(#itBlur)"/><path d="{d}" fill="{ice}"/>', w


# ── Sector 06 · Field Log ──────────────────────────────────────────────────────

def experience() -> Doc:
    """Scene 08 — Time Keeper: a floating violet clock above his palm, timeline rings around him."""
    W, H = 1000, 520
    d = Doc(W, H, "The Time Chamber — experience",
            "Experience (2026): " + "; ".join(f"{r} at {c} ({t})" for _, c, r, t in EXPERIENCE)
            + ". Scene: the vampire holds a floating violet clock inside rotating timeline rings.")
    under, over = panel(d, W, H, "ex", 20, grid_on=False, glow_at=(.8, .45))
    d.add(under, '<g clip-path="url(#exClip)">')
    d.add(C.chamber(d, W, H, "exC", windows=[(746, 34, 150, 290, C.VIEW_MOONL)], floor_y=478, pillars=(690, 980)))
    # a giant faint clock face on the wall behind him
    d.keyframes("exWall", "to{transform:rotate(360deg)}")
    d.add(f'<g opacity=".35" style="transform-origin:822px 250px;animation:exWall 120s linear infinite">'
          f'<circle cx="822" cy="250" r="200" fill="none" stroke="{P.glow}" stroke-width=".8" stroke-dasharray="2 12"/>'
          + "".join(f'<path d="M{n(822 + 186 * math.cos(math.radians(a)))} {n(250 + 186 * math.sin(math.radians(a)))}'
                    f'L{n(822 + 172 * math.cos(math.radians(a)))} {n(250 + 172 * math.sin(math.radians(a)))}" stroke="{P.ice}" stroke-width="1.4"/>'
                    for a in range(0, 360, 30)) + "</g>")
    mx, fy, sc = 822, H - 36, .84
    px, py = M.palm("timekeeper", 1, 10)
    ck = C.clock(d, mx + px * sc, fy + py * sc - 42, 28, "exClk")
    d.keyframes("exRing", "to{transform:rotate(360deg)}")
    rings = "".join(f'<g style="transform-origin:{mx}px {fy - 190}px;animation:exRing {sp}s linear infinite{";animation-direction:reverse" if i % 2 else ""}">'
                    f'<ellipse cx="{mx}" cy="{fy - 190}" rx="{rx}" ry="{ry}" fill="none" stroke="{P.glow}" stroke-width=".9" '
                    f'stroke-dasharray="3 9" opacity=".6" transform="rotate({tilt} {mx} {fy - 190})"/>'
                    + "".join(f'<circle cx="{n(mx + rx * math.cos(a))}" cy="{n(fy - 190 + ry * math.sin(a))}" r="3" fill="{P.ice}" '
                              f'transform="rotate({tilt} {mx} {fy - 190})"/>' for a in (i * 1.3, i * 1.3 + 2.4)) + "</g>"
                    for i, (rx, ry, sp, tilt) in enumerate(((150, 40, 30, -12), (170, 52, 44, 10), (130, 30, 22, -4))))
    d.add(rings, f'<g transform="translate({mx} {fy}) scale({sc})">{M.aura(d, 120, 240, -250)}{M.figure(d, "timekeeper")}'
          f'{M.smoke(d, 260, -4, seed=13, key="exSm")}</g>', ck)
    d.add(C.vignette(d, W, H, "exV", .45))
    tb, _ = title_bar(d, 56, 52, "06", "THE TIME CHAMBER", "FIELD LOG", 34, key="exTb")
    d.add(tb)
    # spine
    sx, y0, y1 = 86, 150, 452
    d.keyframes("exRun", f"0%{{transform:translateY(0);opacity:0}}10%{{opacity:1}}90%{{opacity:1}}100%{{transform:translateY({y1 - y0}px);opacity:0}}")
    d.add(f'<path d="M{sx} {y0}V{y1}" stroke="#351263" stroke-width="3"/>'
          f'<path d="M{sx} {y0}V{y1}" stroke="{P.glow}" stroke-width="1.4" stroke-dasharray="2 8" opacity=".7"/>'
          f'<g style="animation:exRun 3.6s ease-in-out infinite"><rect x="{sx - 1.5}" y="{y0}" width="3" height="34" rx="1.5" fill="{P.ice}"/>'
          f'<circle cx="{sx}" cy="{y0 + 34}" r="4" fill="{P.ice}" filter="{glow_filter(d, "exGl", 3, 2)}"/></g>')
    cg = linear(d, "exCard", [(0, "#1A0D26", .93), (1, "#08050D", .93)], 0, 0, 1, 1)
    for i, (yr, co, role, tag) in enumerate(EXPERIENCE):
        cy = 162 + i * 104
        d.add(f'<circle cx="{sx}" cy="{cy + 40}" r="17" fill="#190C2A" stroke="{P.glow}" stroke-width="1.6"/>'
              + sigil("briefcase", sx, cy + 40, .56, P.glow, 1.4),
              f'<path d="M{sx + 17} {cy + 40}H{sx + 38}" stroke="{P.glow}" stroke-width="1.4"/>',
              f'<rect x="{sx + 38}" y="{cy}" width="560" height="84" rx="12" fill="{cg}" stroke="{P.glow}" stroke-opacity=".45" stroke-width=".8"/>',
              f'<rect x="{sx + 38}" y="{cy + 14}" width="3" height="56" rx="1.5" fill="{P.glow}"/>')
        y_t, _ = text_use(d, yr, sx + 58, cy + 26, 12, "ui6", tracking=.3, fill=P.glow)
        nm, _ = ice_title(d, co.upper(), sx + 58, cy + 54, 21, f"exIce{i}")
        rl, _ = text_use(d, role, sx + 58, cy + 74, 14.5, "ui5", fill=P.text)
        pill, pw = status_pill(d, sx + 582, cy + 12, tag.upper() if len(tag) < 12 else "AI & DATA SCIENCE", anchor="end", color=P.accent, size=10)
        cert, _ = text_use(d, "INTERNSHIP CERTIFICATE", sx + 582, cy + 72, 9.5, "ui6", anchor="end", tracking=.24, fill=P.text2)
        d.add(y_t, nm, rl, pill, cert, sigil("award", sx + 582 - measure("INTERNSHIP CERTIFICATE", "ui6", 9.5, .24) - 14, cy + 68, .36, P.glow, 1.2))
    note, _ = text_use(d, "THREE INTERNSHIPS  •  2026", sx + 38, H - 14, 9.5, "ui6", tracking=.26, fill=P.muted)
    d.add(note, "</g>", over)
    return d


# ── CHAMBER 07 · THE ANCIENT LIBRARY (education) — Scene 09 "Knowledge Keeper" ──

def shelves(doc: Doc, x: float, y: float, w: float, h: float, key: str = "shf", seed: int = 3) -> str:
    """Tall library shelves packed with dark book spines."""
    import random
    rnd = random.Random(seed)
    o = [f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="#08050D"/>']
    rows = int(h // 58)
    for r in range(rows):
        by = y + 8 + r * 58
        bx = x + 6
        while bx < x + w - 10:
            bw, bh = rnd.uniform(6, 13), rnd.uniform(34, 48)
            col = rnd.choice(["#12091C", "#1A0D26", "#241137", "#0E0816", "#2E1065"])
            o.append(f'<rect x="{n(bx)}" y="{n(by + 48 - bh)}" width="{n(bw)}" height="{n(bh)}" rx="1" fill="{col}"/>')
            if rnd.random() < .18:
                o.append(f'<rect x="{n(bx + 1)}" y="{n(by + 50 - bh)}" width="{n(bw - 2)}" height="1.2" fill="{P.ice}" opacity=".35"/>')
            bx += bw + rnd.uniform(.5, 2)
        o.append(f'<rect x="{n(x)}" y="{n(by + 48)}" width="{n(w)}" height="6" fill="#1E1230"/>'
                 f'<path d="M{n(x)} {n(by + 48)}H{n(x + w)}" stroke="{P.glow}" stroke-width=".5" opacity=".35"/>')
    return "".join(o)


def education() -> Doc:
    W, H = 1000, 540
    d = Doc(W, H, "The Ancient Library — education",
            "Education: " + "; ".join(f"{deg}{', ' + inst if inst else ''} ({yr.replace(' — ', '–')}, {st.lower()})" for yr, deg, inst, st in EDUCATION)
            + ". Scene: in a gothic library the vampire opens an ancient book whose pages rise as holograms.")
    under, over = panel(d, W, H, "ed", 20, grid_on=False, glow_at=(.2, .5))
    d.add(under, '<g clip-path="url(#edClip)">')
    d.add(C.chamber(d, W, H, "edC", windows=[(128, 40, 120, 250, C.VIEW_MOON)], floor_y=500, fog=False))
    d.add(shelves(d, 0, 20, 112, 480, "edS1", 3), shelves(d, 264, 20, 96, 480, "edS2", 5))
    ax, fy, sc = 190, H - 32, .9
    bx, by = M.palm("scholar", 1, 2)
    bk = C.floating_book(d, ax + bx * sc - 2, fy + by * sc - 12, 1.25, "edBk")
    d.add(f'<g transform="translate({ax} {fy}) scale({sc})">{M.aura(d, 120, 240, -250, 1.1)}{M.figure(d, "scholar")}'
          f'{M.smoke(d, 240, -4, seed=15, key="edSm")}</g>', bk)
    # holographic diagram rising from the book
    hx, hy = ax + bx * sc, fy + by * sc - 110
    d.keyframes("edHolo", "0%,100%{opacity:.5;transform:translateY(0)}50%{opacity:1;transform:translateY(-6px)}")
    d.add(f'<g style="animation:edHolo 5s ease-in-out infinite">'
          f'<circle cx="{n(hx)}" cy="{n(hy)}" r="26" fill="none" stroke="{P.ice}" stroke-width=".8" stroke-dasharray="3 5"/>'
          f'<path d="M{n(hx - 18)} {n(hy + 10)}L{n(hx)} {n(hy - 16)}L{n(hx + 18)} {n(hy + 10)}Z" fill="none" stroke="{P.glow}" stroke-width="1"/>'
          + "".join(f'<circle cx="{n(hx + x)}" cy="{n(hy + y)}" r="2.6" fill="{P.ice}"/>' for x, y in ((-18, 10), (0, -16), (18, 10), (0, 3)))
          + "</g>")
    d.add(el.fog(d, W, H - 30, 60, seed=19, dur=52, opacity=.14, color="#9C7FD6", name="edFog"), C.vignette(d, W, H, "edV", .4))
    tb, _ = title_bar(d, 390, 52, "07", "THE ANCIENT LIBRARY", "THE ARCHIVE", 34, key="edTb")
    d.add(tb)
    cg = linear(d, "edCard", [(0, "#1A0D26", .95), (1, "#050507", .95)], 0, 0, 0, 1)
    for i, (yr, deg, inst, st) in enumerate(EDUCATION):
        x0, y0, w, h = 390 + i * 294, 150, 276, 330
        cx = x0 + w / 2
        arch = f"M{x0} {y0 + h}L{x0} {y0 + 64}Q{x0} {y0 + 10} {cx} {y0}Q{x0 + w} {y0 + 10} {x0 + w} {y0 + 64}L{x0 + w} {y0 + h}Z"
        d.add(f'<path d="{arch}" fill="{cg}" stroke="{P.glow}" stroke-width=".9" stroke-opacity=".6"/>')
        d.add(f'<circle cx="{n(cx)}" cy="{y0 + 52}" r="23" fill="#12091C" stroke="{P.ice}" stroke-width="1" stroke-opacity=".7"/>'
              + sigil("cap" if i == 0 else "code", cx, y0 + 52, .76, P.ice, 1.5))
        pill, _ = status_pill(d, cx, y0 + 86, st, anchor="middle", color=P.ice if i == 0 else P.glow, size=10)
        yt, _ = text_use(d, yr, cx, y0 + 134, 15, "ui6", anchor="middle", tracking=.28, fill=P.ice)
        d.add(pill, yt)
        lines = wrap(deg, "cinzel7", 19, w - 36, .03)
        for k, ln in enumerate(lines):
            t, _ = ice_title(d, ln, cx, y0 + 168 + k * 25, 19, f"edIce{i}", font="cinzel7", anchor="middle", tracking=.03)
            d.add(t)
        ly = y0 + 168 + len(lines) * 25 - 2
        d.add(f'<path d="M{n(cx - 50)} {ly}H{n(cx + 50)}" stroke="{P.glow}" stroke-opacity=".5"/>', diamond(cx, ly, 3, P.glow))
        for k, ln in enumerate(wrap(inst, "ui5", 14, w - 40) if inst else []):
            t, _ = text_use(d, ln, cx, ly + 25 + k * 19, 14, "ui5", anchor="middle", fill=P.text2)
            d.add(t)
    d.add("</g>", over)
    return d


# ── CHAMBER 08 · CREDENTIALS ───────────────────────────────────────────────────

def certifications() -> Doc:
    W, H = 1000, 470
    d = Doc(W, H, "Credentials — certifications",
            "Certifications: " + "; ".join(f"{t}{' — ' + o if o in ISSUERS else ''}" for t, o, _ in CERTIFICATIONS) + ".")
    under, over = panel(d, W, H, "ce", 20, grid_on=False, glow_at=(.82, .45))
    d.add(under, '<g clip-path="url(#ceClip)">')
    d.add(C.chamber(d, W, H, "ceC", floor_y=440, fog=False), shelves(d, 700, 20, 280, 420, "ceS", 9),
          f'<rect x="700" y="20" width="280" height="420" fill="#020203" opacity=".45"/>')
    # sealed certificates floating in front of the shelves
    d.keyframes("ceFloat", "0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}")
    seal = radial(d, "ceSeal", [(0, P.ice), (.45, P.glow), (1, P.primary)], .4, .35, .7)
    for i, (x, y, rot) in enumerate(((770, 150, -8), (840, 190, 5), (790, 270, -3))):
        d.add(f'<g style="animation:ceFloat {5 + i}s ease-in-out {-i * 1.4:.1f}s infinite"><g transform="rotate({rot} {x + 55} {y + 38})">'
              f'<rect x="{x}" y="{y}" width="110" height="76" rx="4" fill="#12091C" stroke="{P.ice}" stroke-opacity=".7"/>'
              + "".join(f'<rect x="{x + 14}" y="{y + 16 + k * 10}" width="{[70, 56, 64][k]}" height="3" rx="1.5" fill="{P.ice}" opacity=".45"/>' for k in range(3))
              + f'<circle cx="{x + 88}" cy="{y + 56}" r="11" fill="{seal}"/>' + sigil("award", x + 88, y + 56, .4, "#12091C", 1.4)
              + "</g></g>")
    tb, _ = title_bar(d, 56, 52, "08", "CERTIFICATIONS", "CREDENTIALS", 34, key="ceTb")
    d.add(tb)
    pg = linear(d, "cePl", [(0, "#1A0D26", .95), (1, "#050507", .95)], 0, 0, 1, 0)
    hexg = radial(d, "ceHex", [(0, "#241137"), (1, "#0B0712")], .5, .4, .7)
    d.keyframes("ceSealP", "0%,100%{opacity:.45}50%{opacity:1}")
    for i, (title, org, ic) in enumerate(CERTIFICATIONS):
        y = 150 + i * 58
        x0, w = 56, 600
        hx = x0 + 30
        hexp = "M" + "L".join(f"{n(hx + 20 * math.cos(math.radians(60 * k - 90)))} {n(y + 25 + 20 * math.sin(math.radians(60 * k - 90)))}" for k in range(6)) + "Z"
        fs = 16
        while measure(title, "ui5", fs) > w - 150 and fs > 12:
            fs -= .5
        t, _ = text_use(d, title, x0 + 64, y + 23, fs, "ui5", fill=P.text)
        o, _ = text_use(d, org.upper(), x0 + 64, y + 41, 10, "ui6", tracking=.28, fill=P.ice)
        d.add(f'<rect x="{x0}" y="{y}" width="{w}" height="50" rx="10" fill="{pg}" stroke="{P.glow}" stroke-opacity=".4" stroke-width=".8"/>'
              f'<path d="{hexp}" fill="{hexg}" stroke="{P.ice}" stroke-opacity=".7" stroke-width="1"/>' + sigil(ic, hx, y + 25, .54, P.ice, 1.4) + t + o
              + f'<g style="animation:ceSealP 3s ease-in-out {i * .4:.1f}s infinite">' + sigil("award", x0 + w - 28, y + 25, .58, P.glow, 1.3) + "</g>")
    d.add(el.fog(d, W, H - 24, 50, seed=29, dur=50, opacity=.12, color="#9C7FD6", name="ceFog"), "</g>", over)
    return d
