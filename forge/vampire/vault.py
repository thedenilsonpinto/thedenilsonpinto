"""Sector 04 — the Project Vault: header, six verified repository cards, link buttons.

Every card shows only what the repository itself contains (see data.PROJECTS).
Links live in README.md as separate buttons: SVGs shown through <img> can't be clicked.
"""
from __future__ import annotations

import math
import random

from . import elements as el
from . import chamber as C
from . import mascot as M
from .core import Doc, linear, n, radial
from .data import PROJECTS
from .hud import panel, scanline, status_pill, title_bar
from .midnight import badge
from .ornament import diamond
from .palette import P
from .sigils import sigil
from .text import measure, text_path, text_use


def hexagon(cx: float, cy: float, r: float) -> str:
    return "M" + "L".join(f"{n(cx + r * math.cos(math.radians(60 * i - 90)))} {n(cy + r * math.sin(math.radians(60 * i - 90)))}"
                          for i in range(6)) + "Z"


# ── header ────────────────────────────────────────────────────────────────────

def projects_header() -> Doc:
    """Scene 07 — Project Commander: the vampire directs six floating project interfaces."""
    W, H = 1000, 430
    d = Doc(W, H, "The Command Room — verified repositories",
            "Chamber 04, the command room: " + ", ".join(p["name"] for p in PROJECTS)
            + ". Six public repositories; every card below links to real code. Scene: the vampire commands floating project panels.")
    under, over = panel(d, W, H, "pv", 20, grid_on=False, glow_at=(.3, .6))
    d.add(under, '<g clip-path="url(#pvClip)">')
    d.add(C.chamber(d, W, H, "pvC", windows=[(92, 36, 150, 300, C.VIEW_TOWERS)], floor_y=392, pillars=(300,)))
    tb, _ = title_bar(d, 360, 52, "04", "THE COMMAND ROOM", "PROJECT VAULT", 34, key="pvTb")
    sub, _ = text_use(d, "Six public repositories — every card below links to its real code.", 360, 146, 14.5, "ui5", fill=P.text2)
    d.add(tb, sub)
    # six floating project interfaces
    d.keyframes("pvFloat", "0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}")
    d.keyframes("pvScan", "0%{transform:translateY(0)}100%{transform:translateY(62px)}")
    pg = linear(d, "pvPanel", [(0, P.glow, .16), (1, "#12091C", .85)], 0, 0, 0, 1)
    for i, pj in enumerate(PROJECTS):
        col, row = i % 3, i // 3
        x, y = 360 + col * 204, 178 + row * 112
        lb, _ = text_use(d, pj["short"], x + 58, y + 34, 12, "ui6", tracking=.18, fill=P.text)
        ix, _ = text_use(d, f"04.{i + 1}", x + 58, y + 52, 8.5, "mono", fill=P.ice)
        kd, _ = text_use(d, pj["kind"], x + 180, y + 52, 7.5, "ui6", anchor="end", tracking=.16, fill=P.text2)
        ix += kd
        d.add(f'<g style="animation:pvFloat {5 + i % 3}s ease-in-out {-i * .8:.1f}s infinite">'
              f'<rect x="{x}" y="{y}" width="190" height="96" rx="8" fill="{pg}" stroke="{P.glow}" stroke-opacity=".6" stroke-width=".9"/>'
              f'<rect x="{x + 12}" y="{y + 14}" width="36" height="36" rx="7" fill="#12091C" stroke="{P.ice}" stroke-opacity=".6"/>'
              + sigil(pj["icon"], x + 30, y + 32, .62, P.ice, 1.5) + lb + ix
              + "".join(f'<rect x="{x + 12}" y="{y + 66 + k * 8}" width="{[150, 118, 136][k]}" height="3" rx="1.5" fill="{P.glow}" opacity=".35"/>' for k in range(3))
              + f'<rect x="{x + 1}" y="{y + 1}" width="188" height="10" fill="{P.ice}" opacity=".08" style="animation:pvScan 3.6s linear {-i * .6:.1f}s infinite"/>'
              + "</g>")
    # the commander
    ax, ay, sc = 150, H - 30, .76
    fx, fy = M.palm("commander", 1, 30)
    tip = (ax + fx * sc, ay + fy * sc)
    beam = linear(d, "pvBeam", [(0, P.ice, .9), (1, P.glow, .05)], 0, 0, 1, 0)
    d.add(f'<path d="M{n(tip[0])} {n(tip[1])}Q{n(tip[0] + 60)} {n(tip[1] - 30)} 358 250" fill="none" stroke="{beam}" stroke-width="2"/>'
          f'<circle cx="{n(tip[0])}" cy="{n(tip[1])}" r="4.5" fill="{P.ice}" filter="url(#mvGlow)"/>')
    d.add(f'<g transform="translate({ax} {ay}) scale({sc})">{M.aura(d, 120, 240, -250)}{M.figure(d, "commander")}'
          f'{M.smoke(d, 260, -4, seed=11, key="pvSm")}</g>')
    d.add(C.vignette(d, W, H, "pvV", .45), "</g>", over)
    return d


# ── holo previews (local 300 × 248 window) ──────────────────────────────────────

def prev_resume(d: Doc) -> str:
    o = [f'<rect x="30" y="28" width="126" height="172" rx="7" fill="#1C0D2E" stroke="{P.glow}" stroke-opacity=".55"/>',
         f'<rect x="46" y="44" width="56" height="7" rx="3" fill="{P.glow}"/><rect x="46" y="56" width="82" height="4" rx="2" fill="#572B91"/>']
    for i, w in enumerate([92, 84, 70, 88, 60, 90, 76, 52, 86, 66]):
        yy = 74 + i * 11.5
        o.append(f'<rect x="46" y="{n(yy)}" width="{36 if i in (3, 7) else w}" height="{5 if i in (3, 7) else 4}" rx="2" '
                 f'fill="{P.accent if i in (3, 7) else "#3B1C63"}"/>')
    d.keyframes("rvHit", "0%,100%{opacity:.25}50%{opacity:1}")
    for k, (x, yy, w) in enumerate(((50, 97, 30), (92, 131, 26), (60, 166, 34))):     # detected skills
        o.append(f'<rect x="{x}" y="{yy - 3}" width="{w}" height="9" rx="3" fill="none" stroke="{P.glow}" style="animation:rvHit 2.4s {k * .8:.1f}s infinite"/>')
    sg = linear(d, "rvScanG", [(0, P.glow, 0), (1, P.glow, .35)], 0, 0, 0, 1)
    d.keyframes("rvScan", "0%,100%{transform:translateY(0)}50%{transform:translateY(160px)}")
    o.append(f'<g style="animation:rvScan 4s ease-in-out infinite"><rect x="26" y="18" width="134" height="12" fill="{sg}"/>'
             f'<rect x="26" y="30" width="134" height="2.4" fill="{P.glow}"/></g>')
    circ = 2 * math.pi * 38
    d.keyframes("rvGauge", f"0%,8%{{stroke-dashoffset:{n(circ)}}}60%,100%{{stroke-dashoffset:{n(circ * .24)}}}")
    ats, _ = text_use(d, "ATS", 228, 86, 17, "ui6", anchor="middle", tracking=.1, fill=P.text)
    scl, _ = text_use(d, "SCORE", 228, 101, 8, "ui6", anchor="middle", tracking=.3, fill=P.text2)
    o.append(f'<circle cx="228" cy="82" r="38" fill="#130920" stroke="#2D164A" stroke-width="8"/>'
             f'<circle cx="228" cy="82" r="38" fill="none" stroke="{P.glow}" stroke-width="8" stroke-linecap="round" '
             f'stroke-dasharray="{n(circ)}" transform="rotate(-90 228 82)" style="animation:rvGauge 4s ease-in-out infinite"/>' + ats + scl)
    d.keyframes("rvBar", "0%,10%{transform:scaleX(.08)}55%,100%{transform:scaleX(1)}")
    for k, (lb, w) in enumerate((("SKILL", 44), ("MATCH", 34), ("READY", 40))):
        yy = 146 + k * 22
        t, _ = text_use(d, lb, 186, yy + 7, 8, "ui6", tracking=.2, fill=P.text2)
        o.append(t + f'<rect x="226" y="{yy}" width="50" height="7" rx="3.5" fill="#2D164A"/>'
                 f'<rect x="226" y="{yy}" width="{w}" height="7" rx="3.5" fill="{P.glow}" style="transform-box:fill-box;transform-origin:left;'
                 f'animation:rvBar 4s ease-out {k * .3:.1f}s infinite"/>')
    pdf, _ = text_use(d, "PDF REPORT", 62, 229, 9, "ui6", tracking=.26, fill=P.glow)
    o.append(f'<rect x="30" y="214" width="126" height="22" rx="11" fill="#211037" stroke="{P.accent}" stroke-opacity=".7"/>'
             + sigil("doc", 46, 225, .36, P.glow, 1.3) + pdf)
    return "".join(o)


def prev_cyber(d: Doc) -> str:
    cx, cy, R = 150, 110, 90
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#511D96" stroke-opacity=".8"/>' for r in (R, R * .66, R * .33)]
    o.append(f'<path d="M{cx - R} {cy}H{cx + R}M{cx} {cy - R}V{cy + R}" stroke="#371463"/>')
    d.keyframes("cySweep", "to{transform:rotate(360deg)}")
    wedge = lambda a0, a1: (f'M{cx} {cy}L{n(cx + R * math.cos(math.radians(a0)))} {n(cy + R * math.sin(math.radians(a0)))}'
                            f'A{R} {R} 0 0 1 {n(cx + R * math.cos(math.radians(a1)))} {n(cy + R * math.sin(math.radians(a1)))}Z')
    o.append(f'<g style="transform-origin:{cx}px {cy}px;animation:cySweep 4s linear infinite">'
             f'<path d="{wedge(-50, 0)}" fill="{P.glow}" opacity=".07"/><path d="{wedge(-22, 0)}" fill="{P.glow}" opacity=".12"/>'
             f'<path d="M{cx} {cy}L{cx + R} {cy}" stroke="{P.glow}" stroke-width="1.6"/></g>')
    d.keyframes("cyBlip", "0%,100%{opacity:.15}12%{opacity:1}40%{opacity:.4}")
    for k, (x, yy, lb) in enumerate(((98, 64, "PHISHING"), (212, 84, "OTP THEFT"), (112, 164, "FAKE JOB"), (204, 152, "LOTTERY"))):
        t, _ = text_use(d, lb, x + (9 if x < cx else -9), yy + 3, 8, "ui6", anchor="start" if x < cx else "end", tracking=.18, fill=P.text2)
        o.append(f'<g style="animation:cyBlip 4s {k:.0f}s infinite"><circle cx="{x}" cy="{yy}" r="4.5" fill="{P.ice}"/>'
                 f'<circle cx="{x}" cy="{yy}" r="9" fill="none" stroke="{P.glow}"/></g>' + t)
    o.append(f'<circle cx="{cx}" cy="{cy}" r="22" fill="#140921" stroke="{P.glow}" stroke-width="1.4"/>' + sigil("shield", cx, cy, .9, P.glow, 1.6))
    rl, _ = text_use(d, "RISK LEVEL", 30, 228, 8.5, "ui6", tracking=.26, fill=P.text2)
    o.append(rl)
    shades = ["#371168", "#50199A", P.primary, P.accent, P.glow]
    for k, c in enumerate(shades):
        o.append(f'<rect x="{106 + k * 34}" y="221" width="30" height="8" rx="2" fill="{c}" opacity=".85"/>')
    d.keyframes("cyRisk", "0%,100%{transform:translateX(0)}50%{transform:translateX(136px)}")
    o.append(f'<path d="M110 215L116 215L113 219Z" fill="{P.ice}" style="animation:cyRisk 5s ease-in-out infinite"/>')
    return "".join(o)


def prev_interview(d: Doc) -> str:
    o = []
    d.keyframes("ivRing", "0%{transform:scale(1);opacity:.7}100%{transform:scale(1.7);opacity:0}")
    for k in range(2):
        o.append(f'<circle cx="68" cy="84" r="38" fill="none" stroke="{P.glow}" style="transform-box:fill-box;transform-origin:center;'
                 f'animation:ivRing 2.4s ease-out {k * 1.2:.1f}s infinite"/>')
    o.append(f'<circle cx="68" cy="84" r="38" fill="#211037" stroke="{P.glow}" stroke-width="1.6"/>' + sigil("mic", 68, 84, 1.25, P.glow, 1.8))
    d.keyframes("ivWave", "0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}")
    rnd = random.Random(7)
    for k in range(20):
        h = rnd.uniform(14, 54)
        o.append(f'<rect x="{126 + k * 7.4:.1f}" y="{n(84 - h / 2)}" width="3.6" height="{n(h)}" rx="1.8" fill="{P.glow if k % 3 else P.ice}" '
                 f'style="transform-box:fill-box;transform-origin:center;animation:ivWave {rnd.uniform(.7, 1.3):.2f}s ease-in-out {rnd.uniform(0, .8):.2f}s infinite"/>')
    d.keyframes("ivQ", "0%,6%{opacity:0}12%,90%{opacity:1}96%,100%{opacity:0}")
    d.keyframes("ivA", "0%,40%{opacity:0}46%,90%{opacity:1}96%,100%{opacity:0}")
    q, _ = text_use(d, "Q", 44, 169, 11, "ui6", anchor="middle", fill="#020203")
    a, _ = text_use(d, "A", 256, 213, 11, "ui6", anchor="middle", fill="#020203")
    o.append(f'<g class="rv" style="opacity:0;animation:ivQ 7s infinite"><rect x="24" y="148" width="176" height="34" rx="10" fill="#261240" stroke="{P.accent}"/>'
             f'<circle cx="44" cy="165" r="10" fill="{P.glow}"/>{q}<rect x="62" y="158" width="118" height="4" rx="2" fill="#572B91"/>'
             f'<rect x="62" y="168" width="78" height="4" rx="2" fill="#572B91"/></g>')
    o.append(f'<g class="rv" style="opacity:0;animation:ivA 7s infinite"><rect x="100" y="192" width="176" height="34" rx="10" fill="#371168" stroke="{P.glow}" stroke-opacity=".7"/>'
             f'<circle cx="256" cy="209" r="10" fill="{P.ice}"/>{a}<rect x="116" y="202" width="118" height="4" rx="2" fill="#B48CEC"/>'
             f'<rect x="116" y="212" width="90" height="4" rx="2" fill="#B48CEC"/></g>')
    lb, _ = text_use(d, "VOICE AI INTERVIEWER", 126, 138, 8.5, "ui6", tracking=.26, fill=P.text2)
    o.append(lb)
    return "".join(o)


def prev_vision(d: Doc) -> str:
    sky = linear(d, "viSky", [(0, "#371168"), (1, "#140921")], 0, 0, 0, 1)
    o = [f'<rect x="24" y="24" width="152" height="120" rx="6" fill="{sky}" stroke="{P.glow}" stroke-opacity=".5"/>',
         f'<circle cx="140" cy="54" r="14" fill="#E3D1FD" opacity=".9"/>',
         f'<path d="M24 144L62 96L84 118L112 84L150 126L176 108L176 144Z" fill="#24123C"/>',
         f'<path d="M24 144L48 122L70 136L96 116L128 138L152 128L176 140L176 144Z" fill="#1A0D2B"/>']
    el.bat_defs(d)
    o.append('<use href="#bat0" transform="translate(84 62) scale(.9)"/>')
    d.keyframes("viBox", "0%,100%{transform:scale(1);opacity:.7}50%{transform:scale(1.08);opacity:1}")
    br = "M60 48V40H68M100 40H108V48M108 76V84H100M68 84H60V76"
    o.append(f'<path d="{br}" fill="none" stroke="{P.ice}" stroke-width="2" style="transform-box:fill-box;transform-origin:center;animation:viBox 2s ease-in-out infinite"/>')
    d.keyframes("viBar", "0%,12%{transform:scaleX(.05)}60%,100%{transform:scaleX(1)}")
    for k, w in enumerate((76, 42, 20)):
        yy = 36 + k * 34
        t, _ = text_use(d, f"TOP-{k + 1}", 192, yy, 8.5, "ui6", tracking=.2, fill=P.glow if k == 0 else P.text2)
        o.append(t + f'<rect x="192" y="{yy + 7}" width="84" height="8" rx="4" fill="#2D164A"/>'
                 f'<rect x="192" y="{yy + 7}" width="{w}" height="8" rx="4" fill="{P.glow if k == 0 else P.accent}" '
                 f'style="transform-box:fill-box;transform-origin:left;animation:viBar 4s ease-out {k * .25:.2f}s infinite"/>')
    layers = [(44, (176, 196, 216)), (108, (170, 186, 202, 218)), (172, (176, 196, 216)), (236, (196,))]
    d.keyframes("viNet", "to{stroke-dashoffset:-20}")
    links = []
    for (x0, ys0), (x1, ys1) in zip(layers, layers[1:]):
        links += [f"M{x0} {y0}L{x1} {y1}" for y0 in ys0 for y1 in ys1]
    o.append(f'<path d="{"".join(links)}" stroke="{P.glow}" stroke-width=".7" stroke-opacity=".55" stroke-dasharray="3 7" '
             f'style="animation:viNet 1.2s linear infinite"/>')
    o += [f'<circle cx="{x}" cy="{yy}" r="4.5" fill="#211037" stroke="{P.glow}" stroke-width="1.2"/>' for x, ys in layers for yy in ys]
    t, _ = text_use(d, "MOBILENETV2  ·  IMAGENET", 150, 240, 8.5, "ui6", anchor="middle", tracking=.24, fill=P.text2)
    o.append(t)
    return "".join(o)


def prev_chatbot(d: Doc) -> str:
    title, _ = text_use(d, "CODEORBIT CHATBOT", 50, 38, 9.5, "ui6", tracking=.2, fill=P.text)
    d.keyframes("cbDot", "0%,100%{opacity:.3}50%{opacity:1}")
    o = [f'<rect x="16" y="18" width="268" height="30" rx="9" fill="#261240" stroke="{P.accent}" stroke-opacity=".6"/>',
         f'<circle cx="33" cy="33" r="9" fill="#211037" stroke="{P.glow}"/>' + sigil("chat", 33, 33, .36, P.glow, 1.2) + title,
         f'<circle cx="268" cy="33" r="4" fill="{P.glow}" style="animation:cbDot 1.6s infinite"/>']
    bubbles = [("bot", 16, 60, 150, 26, None, (104, 60)), ("user", 176, 94, 108, 26, "What is ML?", None),
               ("bot", 16, 128, 196, 40, None, (150, 120, 70)), ("user", 150, 176, 134, 26, "What time is it?", None),
               ("dots", 16, 212, 56, 24, None, None)]
    for k, (who, x, yy, w, h, txt, bars) in enumerate(bubbles):
        a = 4 + k * 13
        d.keyframes(f"cbIn{k}", f"0%,{a}%{{opacity:0;transform:translateY(6px)}}{a + 4}%,88%{{opacity:1;transform:translateY(0)}}95%,100%{{opacity:0}}")
        if who == "user":
            t, _ = text_use(d, txt, x + w - 12, yy + h / 2 + 4, 11, "ui5", anchor="end", fill="#020203")
            inner = f'<rect x="{x}" y="{yy}" width="{w}" height="{h}" rx="11" fill="{P.accent}"/>' + t
        elif who == "bot":
            inner = f'<rect x="{x}" y="{yy}" width="{w}" height="{h}" rx="11" fill="#271340" stroke="{P.glow}" stroke-opacity=".45"/>'
            inner += "".join(f'<rect x="{x + 12}" y="{yy + 9 + i * 10}" width="{bw}" height="4" rx="2" fill="#B48CEC" opacity=".85"/>' for i, bw in enumerate(bars))
        else:
            d.keyframes("cbType", "0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}")
            inner = (f'<rect x="{x}" y="{yy}" width="{w}" height="{h}" rx="11" fill="#271340" stroke="{P.glow}" stroke-opacity=".45"/>'
                     + "".join(f'<circle cx="{x + 16 + i * 12}" cy="{yy + 12}" r="3" fill="{P.glow}" style="animation:cbType .9s {i * .15:.2f}s infinite"/>' for i in range(3)))
        o.append(f'<g class="rv" style="opacity:0;animation:cbIn{k} 11s infinite">{inner}</g>')
    return "".join(o)


def prev_technova(d: Doc) -> str:
    ban = linear(d, "tnBan", [(0, "#371168"), (1, "#130920")], 0, 0, 1, 1)
    tn, _ = text_path("TECHNOVA 2K26", 150, 86, 17, "cinzel9", anchor="middle", tracking=.06, fill=P.text)
    sub, _ = text_use(d, "NATIONAL LEVEL SYMPOSIUM", 150, 102, 7.5, "ui6", anchor="middle", tracking=.3, fill=P.glow)
    o = [f'<rect x="16" y="16" width="268" height="218" rx="10" fill="#180C28" stroke="{P.glow}" stroke-opacity=".6"/>',
         f'<path d="M16 42H284" stroke="#511D96"/>',
         "".join(f'<circle cx="{30 + i * 11}" cy="29" r="3.2" fill="{c}"/>' for i, c in enumerate((P.glow, P.accent, "#572B91"))),
         f'<rect x="70" y="22" width="196" height="14" rx="7" fill="#261240"/><rect x="82" y="27" width="96" height="4" rx="2" fill="#572B91"/>',
         f'<rect x="28" y="52" width="244" height="62" rx="6" fill="{ban}" stroke="{P.accent}" stroke-opacity=".5"/>', tn, sub]
    shimmer = linear(d, "tnSh", [(0, "#FFFFFF", 0), (.5, "#FFFFFF", .16), (1, "#FFFFFF", 0)], 0, 0, 1, 0)
    d.defs("tnBanClip", '<clipPath id="tnBanClip"><rect x="28" y="52" width="244" height="62" rx="6"/></clipPath>')
    d.keyframes("tnSweep", "0%{transform:translateX(-80px)}60%,100%{transform:translateX(300px)}")
    o.append(f'<g clip-path="url(#tnBanClip)"><rect x="0" y="52" width="60" height="62" fill="{shimmer}" style="animation:tnSweep 4s ease-in-out infinite"/></g>')
    # poster
    pg = linear(d, "tnPoster", [(0, "#50199A"), (1, "#180C28")], 0, 0, 0, 1)
    o.append(f'<rect x="28" y="124" width="100" height="98" rx="5" fill="{pg}" stroke="{P.accent}" stroke-opacity=".5"/>'
             f'<circle cx="78" cy="152" r="16" fill="none" stroke="{P.glow}" stroke-width="1.4"/>' + sigil("calendar", 78, 152, .5, P.glow, 1.3)
             + "".join(f'<rect x="{42 if i else 48}" y="{178 + i * 9}" width="{72 if i else 60}" height="4" rx="2" fill="#C4B5FD" opacity="{.8 if i == 0 else .4}"/>' for i in range(4)))
    # registration QR (decorative pattern, not a real code)
    rnd = random.Random(26)
    qx, qy, c = 140, 124, 5.5
    cells = []
    for r in range(11):
        for cc in range(11):
            finder = (r < 3 and cc < 3) or (r < 3 and cc > 7) or (r > 7 and cc < 3)
            if finder or rnd.random() < .45:
                cells.append(f"M{n(qx + 4 + cc * c)} {n(qy + 4 + r * c)}h{c}v{c}h-{c}z")
    reg, _ = text_use(d, "REGISTER", 173, 214, 7.5, "ui6", anchor="middle", tracking=.28, fill=P.text2)
    o.append(f'<rect x="{qx}" y="{qy}" width="68" height="68" rx="5" fill="#F5F3FF"/><path d="{"".join(cells)}" fill="#020203"/>' + reg)
    # event photos
    d.keyframes("tnPh", "0%,100%{opacity:.45}50%{opacity:1}")
    for i in range(3):
        o.append(f'<rect x="220" y="{124 + i * 34}" width="52" height="28" rx="4" fill="#371168" stroke="{P.glow}" stroke-opacity=".5" '
                 f'style="animation:tnPh 3s {i * .6:.1f}s infinite"/>' + sigil("image", 246, 138 + i * 34, .42, P.glow, 1.1))
    return "".join(o)


PREVIEWS = {"resume-analyzer": prev_resume, "cyber-detective": prev_cyber, "interview-guide": prev_interview,
            "ai-vision": prev_vision, "chatbot": prev_chatbot, "technova": prev_technova}


# ── cards ─────────────────────────────────────────────────────────────────────

def tech_row(d: Doc, x: float, y: float, items, max_w: float) -> str:
    for size in (13, 12.5, 12, 11.5, 11):
        h = round(size * 2.3)
        widths = [measure(it, "ui5", size) + h + 18 for it in items]
        if sum(widths) + 8 * (len(items) - 1) <= max_w:
            break
    out, bx = [], x
    for it, w in zip(items, widths):
        b, _ = badge(d, bx, y, it, h=h, size=size)
        out.append(b)
        bx += w + 8
    return "".join(out)


def project_card(p: dict, idx: int, user: str, live: bool) -> Doc:
    W, H = 1000, 316 + (18 if p.get("org") else 0)
    desc = (f"{p['name']} — {p['tagline']}. " + (p.get("org", "") + ". " if p.get("org") else "")
            + "Features: " + "; ".join(p["features"]) + ". Tech: " + ", ".join(p["tech"]) + f". Repository: github.com/{user}/{p['repo']}.")
    d = Doc(W, H, f"{p['name']} — project 04.{idx}", desc)
    under, over = panel(d, W, H, "pc", 20, glow_at=(.16, .5))
    d.add(under, '<g clip-path="url(#pcClip)">')
    # holo window
    wx, ww, wh = 26, 300, 248
    wy = (H - wh) // 2
    wg = linear(d, "pcWin", [(0, "#1F0F33"), (1, "#0C0614")], 0, 0, 0, 1)
    d.defs("pcWinClip", f'<clipPath id="pcWinClip"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14"/></clipPath>')
    d.add(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="{wg}"/>',
          f'<g clip-path="url(#pcWinClip)"><g transform="translate({wx} {wy})">{PREVIEWS[p["key"]](d)}'
          f'{scanline(d, ww, wh, 6, "pcScan")}</g></g>',
          f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="none" stroke="{P.glow}" stroke-opacity=".7" stroke-width="1.4"/>')
    # right column
    x0, mw = 360, 606
    k, _ = text_use(d, f"04.{idx}  •  {p['kind']}  •  PUBLIC REPO", x0, 58, 11.5, "ui6", tracking=.3, fill=P.glow)
    d.add(k)
    if live and p.get("demo_label"):
        pill, _ = status_pill(d, 966, 40, p["demo_label"], anchor="end")
        d.add(pill)
    size = 28
    while measure(p["title"], "cinzel9", size, .05) > mw and size > 18:
        size -= .5
    tp, _ = text_path(p["title"], x0, 96, size, "cinzel9", tracking=.05)
    dd = tp[len('<path d="'):-3]
    ice = linear(d, "pcIce", [(0, "#FFFFFF"), (.6, "#E7D8FD"), (1, "#CDB4F3")], 0, 96 - size * .75, 0, 96, units="userSpaceOnUse")
    d.defs("pcBlur", '<filter id="pcBlur" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>')
    repo, _ = text_use(d, f"github.com/{user}/{p['repo']}", x0, 121, 11.5, "mono", fill=P.accent)
    d.add(f'<path d="{dd}" fill="{P.primary}" opacity=".5" filter="url(#pcBlur)"/><path d="{dd}" fill="{ice}"/>', repo)
    tg, _ = text_use(d, p["tagline"], x0, 150, 15.5, "ui5", fill=P.text)
    d.add(tg)
    fy = 188
    if p.get("org"):
        og, _ = text_use(d, p["org"], x0, 172, 13.5, "ui5", fill=P.text2)
        d.add(og)
        fy = 202
    for i, f in enumerate(p["features"]):
        fx, yy = x0 + (i % 2) * 306, fy + (i // 2) * 23
        fs = 13.5
        while measure(f, "ui5", fs) > 284 and fs > 11:
            fs -= .5
        t, _ = text_use(d, f, fx + 14, yy, fs, "ui5", fill=P.text2)
        d.add(diamond(fx + 3, yy - 4.5, 3.2, P.glow), t)
    d.add(tech_row(d, x0, H - 60, p["tech"], mw))
    d.add("</g>", over)
    return d
