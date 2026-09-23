"""Chambers I: the Shadow Chamber (about), the AI Laboratory (mission), the Data Chamber (skills)."""
from __future__ import annotations

import json
import math
from pathlib import Path

from . import chamber as C
from . import mascot as M
from .core import Doc, linear, n, radial
from .data import MISSION, PROFILE, SKILL_ICONS, SKILLS, title_case
from .hud import flow_chips, panel, status_pill, title_bar
from .palette import P
from .sigils import sigil
from .text import measure, text_path, text_use, wrap

ICONS = json.loads((Path(__file__).resolve().parents[1] / "data" / "brand_icons.json").read_text())


def icon(slug: str, cx: float, cy: float, size: float = 16, color: str | None = None) -> str:
    color = color or P.glow
    if slug.startswith("sigil:"):
        return sigil(slug[6:], cx, cy, size / 32, color, 1.5)
    s = size / 24
    return f'<path transform="translate({n(cx - size / 2)} {n(cy - size / 2)}) scale({n(s, 4)})" d="{ICONS[slug]["path"]}" fill="{color}"/>'


def badge(doc: Doc, x: float, y: float, label: str, h: float = 34, size: float = 14.5) -> tuple[str, float]:
    slug = SKILL_ICONS.get(label, "sigil:spark")
    w = measure(label, "ui5", size) + h + 18
    g = linear(doc, "mbG", [(0, "#1A0D26", .95), (1, "#08050D", .95)], 0, 0, 0, 1)
    t, _ = text_use(doc, label, x + h + 6, y + h / 2 + size * .36, size, "ui5", fill=P.text)
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{h}" rx="7" fill="{g}" stroke="#3B1D66" stroke-width="1"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{h}" height="{h}" rx="7" fill="#1A0D26"/>'
            + icon(slug, x + h / 2, y + h / 2, 17) + t), w


def dossier_field(doc: Doc, x: float, y: float, label: str, value: str, w: float, ic: str) -> str:
    lt, _ = text_use(doc, label, x + 44, y - 7, 10.5, "ui6", tracking=.3, fill=P.ice)
    vs = 17.5
    while measure(value, "ui5", vs) > w - 50 and vs > 12:
        vs -= .5
    vt, _ = text_use(doc, value, x + 44, y + 15, vs, "ui5", fill=P.text)
    return (f'<rect x="{n(x)}" y="{n(y - 16)}" width="32" height="32" rx="7" fill="#12091C" stroke="#3B1D66"/>' + sigil(ic, x + 16, y, .55, P.glow, 1.4)
            + lt + vt + f'<rect x="{n(x + 44)}" y="{n(y + 25)}" width="{n(w - 44)}" height="1" fill="#2A1A40"/>')


def glass(doc: Doc, x: float, y: float, w: float, h: float, key: str = "gl", r: float = 12) -> str:
    """Black glass slab with an extremely thin violet edge."""
    g = linear(doc, key, [(0, "#12091C", .9), (1, "#050507", .92)], 0, 0, 1, 1)
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{r}" fill="{g}" stroke="{P.glow}" stroke-opacity=".45" stroke-width=".8"/>'
            f'<path d="M{n(x + r)} {n(y + .5)}H{n(x + w * .45)}" stroke="{P.ice}" stroke-opacity=".5" stroke-width=".8"/>')


# ── CHAMBER 01 · SHADOW CHAMBER (about) — Scene 02 "Shadow King" ─────────────────

def about() -> Doc:
    W, H = 1000, 580
    d = Doc(W, H, "The Shadow Chamber — about Denilson Pinto B",
            f"{PROFILE['name']}, {title_case(PROFILE['title'])}. {PROFILE['summary']} Education: {PROFILE['degree']}, "
            f"{PROFILE['college']} (final year, 2027). Scene: the Midnight AI Vampire commands black-violet shadows in a dark castle chamber.")
    under, over = panel(d, W, H, "ab", 20, grid_on=False, glow_at=(.2, .4))
    d.add(under, '<g clip-path="url(#abClip)">')
    d.add(C.chamber(d, W, H, "abC", windows=[(52, 40, 190, 400, C.VIEW_MOON)], floor_y=528, pillars=(22, 350),
                    candles=((318, 520, .9),)))
    ax, ay, sc = 210, 540, .98
    hx, hy = M.palm("shadow", 1, 10)
    td = C.tendrils(d, hx, hy, 9, 175, seed=4, key="abTd")
    d.add(f'<g transform="translate({ax} {ay}) scale({sc})">{M.aura(d, 120, 240, -250, 1.1)}{M.smoke(d, 260, -4, seed=2, key="abSm")}'
          f'{M.figure(d, "shadow", {"back": td})}</g>')
    d.add(C.vignette(d, W, H, "abV", .6))
    x0 = 420
    tb, y = title_bar(d, x0, 58, "", "", "THE ENGINEER", 34, key="abTb", kicker="// CHAMBER 01  •  THE SHADOW CHAMBER")
    d.add(glass(d, x0 - 16, 118, 562, 432, "abGl"), tb)
    nm, _ = text_path(PROFILE["name"], x0 + 8, y + 58, 27, "cinzel9", tracking=.06, fill=P.text)
    rl, _ = text_use(d, PROFILE["headline"], x0 + 8, y + 84, 14, "ui5", tracking=.03, fill=P.ice)
    d.add(nm, rl)
    yy = y + 122
    d.add(f'<rect x="{x0 + 8}" y="{n(yy - 20)}" width="2" height="56" fill="{P.glow}"/>')
    for i, ln in enumerate(wrap(PROFILE["summary"], "serif_i", 20, 520)):
        t, _ = text_use(d, ln, x0 + 22, yy + i * 26, 20, "serif_i", fill=P.text)
        d.add(t)
    rows = [("brain", "FOCUS", PROFILE["specialties"]), ("book", "EDUCATION", "B.Tech AI & Data Science"),
            ("calendar", "STATUS", "Final Year Student · 2027"), ("tower", "CAMPUS", PROFILE["college"]),
            ("send", "CURRENT BUILD", "FlashDrop — final year project"), ("code", "CORE STACK", "Python · NLP · ML · GenAI")]
    for i, (ic, lb, v) in enumerate(rows):
        cx = x0 + 8 + (i % 2) * 272
        cy = yy + 96 + (i // 2) * 64
        d.add(dossier_field(d, cx, cy, lb, v, 256, ic))
    d.add("</g>", over)
    return d


# ── CHAMBER 02 · AI LABORATORY (current mission) — Scene 03 "AI Master" ──────────

def ai_lab() -> Doc:
    W, H = 1000, 560
    d = Doc(W, H, "The AI Laboratory — current mission",
            "Current mission: FlashDrop, final year project, in development. Secondary focus: " + ", ".join(MISSION["secondary"])
            + ". Scene: the vampire summons floating holographic AI interfaces — a neural network, embeddings and code.")
    under, over = panel(d, W, H, "ai", 20, grid_on=False, glow_at=(.25, .45))
    d.add(under, '<g clip-path="url(#aiClip)">')
    d.add(C.chamber(d, W, H, "aiC", windows=[(170, 30, 150, 300, C.VIEW_TOWERS)], floor_y=520, pillars=(24, 444)))
    ax, ay, sc = 244, 530, .92
    d.add(f'<g transform="translate({ax} {ay}) scale({sc})">{M.aura(d, 130, 240, -250, 1.2)}{M.figure(d, "holo")}'
          f'{M.smoke(d, 240, -4, seed=6, key="aiSm")}</g>')
    # holograms around his raised hands
    lx, ly = M.palm("holo", -1, 8)
    rx, ry = M.palm("holo", 1, 8)
    L = (ax + lx * sc, ay + ly * sc)
    R = (ax + rx * sc, ay + ry * sc)
    d.keyframes("aiFloat", "0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}")
    d.add(f'<g style="animation:aiFloat 6s ease-in-out infinite">{C.neural_panel(d, 34, 142, 118, 104, "aiN1", (3, 4, 3), "NEURAL NET")}</g>',
          f'<g style="animation:aiFloat 7s ease-in-out -2s infinite">{C.neural_panel(d, 338, 150, 112, 96, "aiN2", (2, 4, 4, 2), "INFERENCE")}</g>',
          f'<g style="animation:aiFloat 8s ease-in-out -4s infinite">' + C.code_panel(d, 36, 318, 128, 74, [
              ("tokens = embed(text)", P.ice), ("out = model(tokens)", P.text2), ("return generate(out)", P.glow)], "aiCp", 8.2) + "</g>")
    beam = linear(d, "aiBeam", [(0, P.ice, .8), (1, P.glow, 0)], 0, 0, 1, 0)
    d.add(f'<path d="M{n(L[0])} {n(L[1])}L152 194" stroke="{beam}" stroke-width="1.4" opacity=".8"/>'
          f'<path d="M{n(R[0])} {n(R[1])}L338 198" stroke="{P.glow}" stroke-width="1.4" opacity=".7"/>')
    d.add(C.vignette(d, W, H, "aiV", .5))
    x0 = 486
    tb, y = title_bar(d, x0, 58, "", "", "AI LABORATORY", 34, key="aiTb", kicker="// CHAMBER 02  •  CURRENT MISSION")
    d.add(tb)
    card_y = y + 28
    g = linear(d, "aiCard", [(0, "#1A0D26", .95), (1, "#08050D", .95)], 0, 0, 1, 1)
    d.add(f'<rect x="{x0}" y="{card_y}" width="474" height="158" rx="12" fill="{g}" stroke="{P.glow}" stroke-opacity=".55" stroke-width=".9"/>')
    lb, _ = text_use(d, "PRIMARY OBJECTIVE", x0 + 22, card_y + 30, 11, "ui6", tracking=.32, fill=P.ice)
    nm, _ = text_path(MISSION["primary"], x0 + 22, card_y + 74, 38, "cinzel9", tracking=.08, fill=P.text)
    d.add(lb, nm, sigil("send", x0 + 432, card_y + 58, 1.1, P.glow, 1.6))
    px = x0 + 22
    for tag in MISSION["primary_tags"]:
        pill, w = status_pill(d, px, card_y + 94, tag, color=P.ice if tag == "IN DEVELOPMENT" else P.glow, size=10.5)
        d.add(pill)
        px += w + 10
    sub, _ = text_use(d, "Cross-platform file transfer · Android • iOS • Windows • macOS", x0 + 22, card_y + 142, 12.5, "ui5", fill=P.text2)
    d.add(sub)
    sl, _ = text_use(d, "SECONDARY FOCUS", x0, card_y + 196, 11, "ui6", tracking=.32, fill=P.ice)
    chips, _ = flow_chips(d, x0, card_y + 208, MISSION["secondary"], 480, size=14, h=30, row_h=38)
    d.add(sl, chips, "</g>", over)
    return d


# ── CHAMBER 05 · DATA CHAMBER (skills) — Scene 06 "Data Sorcerer" + digital clones ──

CLONES = [("AI", -1, 400), ("ML", -1, 270), ("LLM", 0, 0), ("DATA", 1, 270), ("DEV", 1, 400)]


def skills() -> Doc:
    W, H = 1000, 760
    names = "; ".join(f"{c}: {', '.join(items)}" for c, items in SKILLS)
    d = Doc(W, H, "The Data Chamber — skills",
            f"Skills: {names}. Scene: the vampire pulls streams of violet data between his hands while five translucent clones "
            "stand for AI, ML, LLM, Data and Development.")
    under, over = panel(d, W, H, "sk", 20, grid_on=False, glow_at=(.5, .35))
    d.add(under, '<g clip-path="url(#skClip)">')
    d.add(C.chamber(d, W, H, "skC", windows=[(420, 96, 160, 300, C.VIEW_MOONL)], floor_y=440, pillars=(160, 840), stars=False))
    tb, _ = title_bar(d, W / 2, 52, "", "", "SKILL MATRIX", 34, anchor="middle", key="skTb", kicker="// CHAMBER 05  •  THE DATA CHAMBER")
    d.add(tb)
    cx, fy = 500, 452
    # clones (POWER 09): translucent copies standing behind him, each carrying a discipline
    stand = M.symbol(d, "stand")          # drawn once, reused by every clone
    for lab, side, dx in CLONES:
        if side == 0:
            continue
        x = cx + side * dx
        s = .5 if dx > 200 else .56
        d.add(C.clone(d, stand, x, fy - 20, s, .42, "skCl"))
        t, _ = text_use(d, lab, x, fy + 2, 11, "ui6", anchor="middle", tracking=.3, fill=P.ice)
        d.add(t)
    d.add(C.clone(d, stand, cx - 52, fy - 6, .72, .34, "skCl"))       # LLM: an echo stepping out of him
    lt, _ = text_use(d, "LLM", cx - 118, 196, 11, "ui6", anchor="middle", tracking=.3, fill=P.ice)
    d.add(lt, f'<path d="M{cx - 100} 192H{cx - 72}" stroke="{P.ice}" stroke-width=".8" opacity=".6"/>')
    # the sorcerer, data flowing between his hands
    sc = .72
    lx, ly = M.palm("sorcerer", -1, 12)
    rx, ry = M.palm("sorcerer", 1, 12)
    A, B = (cx + lx * sc, fy + ly * sc), (cx + rx * sc, fy + ry * sc)
    d.add(f'<g transform="translate({cx} {fy}) scale({sc})">{M.aura(d, 150, 250, -250, 1.3)}{M.figure(d, "sorcerer")}'
          f'{M.smoke(d, 280, -2, seed=9, key="skSm")}</g>')
    d.add(C.data_stream(d, A[0], A[1], B[0], B[1], 150, 30, "skDs1", 3),
          C.data_stream(d, A[0], A[1], 170, 520, -40, 12, "skDs2", 4),
          C.data_stream(d, B[0], B[1], 830, 520, -40, 12, "skDs3", 5))
    # skill panels (the chamber's shelves)
    def column(x, y, w, title, items, key):
        body, bx, by = [], x + 16, y + 46
        for it in items:
            bw = measure(it, "ui5", 13.5) + 52
            if bx + bw > x + w - 12 and bx > x + 16:
                bx, by = x + 16, by + 42
            b, _ = badge(d, bx, by, it, h=33, size=13.5)
            body.append(b)
            bx += bw + 8
        hgt = by - y + 48
        t, _ = text_use(d, title, x + 18, y + 30, 11.5, "ui6", tracking=.3, fill=P.ice)
        return glass(d, x, y, w, hgt, key) + t + "".join(body)

    y0 = 490
    d.add(column(28, y0, 306, SKILLS[0][0], SKILLS[0][1], "skG1"), column(347, y0, 306, SKILLS[1][0], SKILLS[1][1], "skG2"),
          column(666, y0, 306, SKILLS[2][0], SKILLS[2][1], "skG3"))
    note, _ = text_use(d, "SOURCED FROM MY RESUME & PUBLIC REPOSITORIES", W / 2, H - 22, 10, "ui6", anchor="middle", tracking=.28, fill=P.muted)
    d.add(note, "</g>", over)
    return d
