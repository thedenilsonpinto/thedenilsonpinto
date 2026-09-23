"""⚡ FlashDrop — the final-year-project centerpiece (3 panels).

Honesty rule: FlashDrop is IN DEVELOPMENT. Module states come from the config
(FLASHDROP_BUILT / FLASHDROP_IN_PROGRESS); anything not listed shows as PLANNED.
"""
from __future__ import annotations

import math
import zlib

from . import elements as el
from . import chamber as C
from . import mascot as M
from .core import Doc, glow_filter, linear, n, radial
from .data import FLASHDROP
from .hud import flow_chips, panel, status_pill, title_bar
from .palette import P
from .sigils import sigil
from .text import text_path, text_use


def device(doc: Doc, kind: str, cx: float, cy: float, label: str, key: str) -> str:
    """Neon device outline with a live FlashDrop transfer screen."""
    scr = linear(doc, "fdScr", [(0, "#371168"), (1, "#140921")], 0, 0, 0, 1)
    doc.keyframes("fdBar", "0%{transform:scaleX(.05)}80%,100%{transform:scaleX(1)}")
    st = f'fill="#0F0718" stroke="{P.glow}" stroke-width="1.6"'
    if kind in ("android", "ios"):
        w, h = 46, 86
        body = (f'<rect x="{n(cx - w/2)}" y="{n(cy - h/2)}" width="{w}" height="{h}" rx="9" {st}/>'
                f'<rect x="{n(cx - w/2 + 4)}" y="{n(cy - h/2 + 8)}" width="{w - 8}" height="{h - 16}" rx="4" fill="{scr}"/>'
                + (f'<circle cx="{n(cx)}" cy="{n(cy - h/2 + 5)}" r="1.6" fill="{P.glow}"/>' if kind == "android" else
                   f'<rect x="{n(cx - 8)}" y="{n(cy - h/2 + 3)}" width="16" height="4" rx="2" fill="{P.glow}"/>'))
        bar_y, bar_w = cy + 18, w - 16
    elif kind == "laptop":
        w, h = 116, 70
        body = (f'<rect x="{n(cx - w/2 + 8)}" y="{n(cy - h/2)}" width="{w - 16}" height="{h - 12}" rx="5" {st}/>'
                f'<rect x="{n(cx - w/2 + 13)}" y="{n(cy - h/2 + 5)}" width="{w - 26}" height="{h - 22}" rx="2" fill="{scr}"/>'
                f'<path d="M{n(cx - w/2)} {n(cy + h/2 - 12)}L{n(cx + w/2)} {n(cy + h/2 - 12)}L{n(cx + w/2 - 6)} {n(cy + h/2 - 3)}L{n(cx - w/2 + 6)} {n(cy + h/2 - 3)}Z" {st}/>')
        bar_y, bar_w = cy + 6, w - 44
    else:  # windows desktop
        w, h = 112, 70
        body = (f'<rect x="{n(cx - w/2)}" y="{n(cy - h/2)}" width="{w}" height="{h - 14}" rx="5" {st}/>'
                f'<rect x="{n(cx - w/2 + 5)}" y="{n(cy - h/2 + 5)}" width="{w - 10}" height="{h - 24}" rx="2" fill="{scr}"/>'
                f'<path d="M{n(cx - 8)} {n(cy + h/2 - 14)}L{n(cx - 10)} {n(cy + h/2 - 2)}L{n(cx + 10)} {n(cy + h/2 - 2)}L{n(cx + 8)} {n(cy + h/2 - 14)}" {st}/>')
        bar_y, bar_w = cy + 2, w - 40
    icon = sigil("doc", cx, cy - (14 if kind in ("android", "ios") else 10), .42, P.ice, 1.3)
    bar = (f'<rect x="{n(cx - bar_w/2)}" y="{n(bar_y)}" width="{n(bar_w)}" height="4" rx="2" fill="#2D164A"/>'
           f'<rect x="{n(cx - bar_w/2)}" y="{n(bar_y)}" width="{n(bar_w)}" height="4" rx="2" fill="{P.glow}" '
           f'style="transform-box:fill-box;transform-origin:left;animation:fdBar 3.2s ease-in-out {zlib.crc32(key.encode()) % 20 / 10:.1f}s infinite"/>')
    t, _ = text_use(doc, label, cx, cy + h / 2 + 22, 11.5, "ui6", anchor="middle", tracking=.3, fill=P.text)
    return body + icon + bar + t


def portal(doc: Doc, cx: float, cy: float, r: float) -> str:
    core = radial(doc, "fdCore", [(0, "#EFEAFF", .95), (.25, P.glow, .75), (.6, P.primary, .35), (1, P.primary, 0)])
    doc.keyframes("fdSpin", "to{transform:rotate(360deg)}")
    doc.keyframes("fdPulse", "0%,100%{transform:scale(.94);opacity:.8}50%{transform:scale(1.05);opacity:1}")
    ticks = "".join(f'<path d="M{n(cx + math.cos(math.radians(a)) * r)} {n(cy + math.sin(math.radians(a)) * r)}L{n(cx + math.cos(math.radians(a)) * (r - (10 if a % 30 else 16)))} {n(cy + math.sin(math.radians(a)) * (r - (10 if a % 30 else 16)))}"/>' for a in range(0, 360, 10))
    drop = "M0 -30C9 -17 17 -7 17 5A17 17 0 0 1 -17 5C-17 -7 -9 -17 0 -30Z"
    bolt = "M3 -14L-8 3L-1 3L-4 17L8 -1L1 -1Z"
    gl = glow_filter(doc, "fdGl", 3, 2)
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 1.35)}" fill="{core}" style="transform-box:fill-box;transform-origin:center;animation:fdPulse 3.6s ease-in-out infinite"/>'
            f'<g style="transform-origin:{n(cx)}px {n(cy)}px;animation:fdSpin 30s linear infinite" fill="none" stroke="{P.glow}" stroke-width="1.6">'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>{ticks}</g>'
            f'<g style="transform-origin:{n(cx)}px {n(cy)}px;animation:fdSpin 12s linear infinite reverse" fill="none" stroke="{P.accent}" stroke-width="2.2" stroke-dasharray="26 14">'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * .72)}"/></g>'
            f'<g transform="translate({n(cx)} {n(cy)})" filter="{gl}"><path d="{drop}" fill="#140921" stroke="{P.glow}" stroke-width="2.2"/><path d="{bolt}" fill="{P.ice}"/></g>')


def flashdrop_hero() -> Doc:
    """Scene 05 — the vampire opens a violet portal; a file leaves the phone and lands on the laptop."""
    W, H = 1000, 700
    d = Doc(W, H, "FlashDrop — final year project (in development)",
            "FlashDrop, my final year project, in development: cross-platform high-speed file sharing between Android, iOS, Windows and macOS "
            "— fast peer-to-peer / local transfer without a cable. Scene: the vampire opens a violet portal and a file travels from an "
            "Android phone through it to a Windows laptop.")
    under, over = panel(d, W, H, "fh", 22, grid_on=False, glow_at=(.62, .6))
    d.add(under, '<g clip-path="url(#fhClip)">')
    d.add(C.chamber(d, W, H, "fhC", floor_y=610, pillars=(420, 980), fog=False))
    # a giant arch behind the portal, the castle painting glowing through it
    pcx, pcy, pr_ = 668, 392, 118
    d.add(C.window(d, pcx - 190, 150, 380, 470, C.VIEW_WIDE, key="fhArch", tracery=False))
    d.add(f'<rect x="{pcx - 190}" y="150" width="380" height="470" fill="#020203" opacity=".45"/>')
    d.add(el.stars(d, W, 300, 40, seed=31, avoid=[(40, 30, 520, 260)]), el.embers(d, W, H, 40, seed=12, rise=320))
    # the portal and its energy tunnel
    tunnel = radial(d, "fhTun", [(0, "#020203", .95), (.55, "#12091C", .8), (.85, P.primary, .25), (1, P.primary, 0)])
    d.add(f'<circle cx="{pcx}" cy="{pcy}" r="{pr_ * .95}" fill="{tunnel}"/>')
    d.keyframes("fhTunR", "to{transform:rotate(360deg)}")
    d.add(f'<g style="transform-origin:{pcx}px {pcy}px;animation:fhTunR 20s linear infinite" fill="none" stroke="{P.glow}" opacity=".5">'
          + "".join(f'<circle cx="{pcx}" cy="{pcy}" r="{n(pr_ * k)}" stroke-width=".8" stroke-dasharray="{n(8 * k)} {n(14 * k)}"/>' for k in (.3, .48, .66))
          + "</g>")
    d.add(portal(d, pcx, pcy, pr_))
    # floating folders / files orbiting the portal
    d.keyframes("fhOrb", "to{transform:rotate(360deg)}")
    files = "".join(f'<g transform="rotate({a} {pcx} {pcy}) translate({n(pcx + pr_ * 1.28)} {pcy}) rotate({-a})">'
                    f'<path d="M-9-7H-3L-1-4.5H9V7H-9Z" fill="#12091C" stroke="{P.ice}" stroke-width="1"/></g>' for a in (20, 110, 200, 290))
    d.add(f'<g style="transform-origin:{pcx}px {pcy}px;animation:fhOrb 26s linear infinite">{files}</g>')
    # device A (phone) → portal → device B (laptop)
    ax_, ay_ = 486, 560
    bx_, by_ = 870, 560
    d.add(device(d, "android", ax_, ay_, "ANDROID", "fdDevA"), device(d, "laptop", bx_, by_ + 6, "WINDOWS", "fdDevB"))
    ex = f"M{ax_} {ay_ - 50}Q{ax_ + 40} {pcy + 20} {pcx - 30} {pcy}Q{pcx + 120} {pcy - 10} {bx_} {by_ - 40}"
    d.defs("fdEx", f'<path id="fdEx" d="{ex}"/>')
    d.keyframes("fdFlow", "to{stroke-dashoffset:-40}")
    d.add(f'<path d="{ex}" fill="none" stroke="{P.glow}" stroke-width="1.6" stroke-dasharray="5 11" opacity=".75" style="animation:fdFlow 1.2s linear infinite"/>')
    file_icon = (f'<g><rect x="-11" y="-14" width="22" height="28" rx="3" fill="#EFEAFF"/><path d="M4 -14L11 -7L4 -7Z" fill="{P.glow}"/>'
                 f'<rect x="-6" y="-2" width="12" height="2" fill="{P.primary}"/><rect x="-6" y="3" width="9" height="2" fill="{P.primary}"/></g>')
    d.add(f'<g>{file_icon}<animateMotion dur="5s" repeatCount="indefinite" keyPoints="0;.45;.55;1" keyTimes="0;.42;.58;1" calcMode="linear"><mpath href="#fdEx"/></animateMotion></g>')
    rnd = __import__("random").Random(8)
    for i in range(14):
        dur = rnd.uniform(3, 5)
        d.add(f'<circle r="{n(rnd.uniform(1, 2.2))}" fill="{rnd.choice([P.ice, P.glow])}"><animateMotion dur="{n(dur, 2)}s" '
              f'begin="{n(-rnd.uniform(0, dur), 2)}s" repeatCount="indefinite"><mpath href="#fdEx"/></animateMotion></circle>')
    exl, _ = text_use(d, "EXAMPLE  ·  ANDROID → WINDOWS", pcx, 640, 11.5, "ui6", anchor="middle", tracking=.28, fill=P.ice)
    exl2, _ = text_use(d, "LARGE FILE  ·  NO CABLE", pcx, 660, 11.5, "ui6", anchor="middle", tracking=.28, fill=P.text2)
    d.add(exl, exl2)
    # the vampire opening the portal
    ax, ay, sc = 170, H - 34, .86
    hx, hy = M.palm("portal", 1, 16)
    beam_x, beam_y = ax + hx * sc, ay + hy * sc
    bg = linear(d, "fhBeam", [(0, P.ice, .9), (1, P.glow, .15)], 0, 0, 1, 0)
    d.add(f'<path d="M{n(beam_x)} {n(beam_y - 3)}L{pcx - pr_ + 10} {pcy - 30}L{pcx - pr_ + 10} {pcy + 30}L{n(beam_x)} {n(beam_y + 3)}Z" fill="{bg}" opacity=".5"/>'
          f'<circle cx="{n(beam_x)}" cy="{n(beam_y)}" r="7" fill="{P.ice}" opacity=".85" filter="url(#mvGlow)"/>')
    d.add(f'<g transform="translate({ax} {ay}) scale({sc})">{M.aura(d, 120, 240, -250, 1.2)}{M.figure(d, "portal")}'
          f'{M.smoke(d, 280, -4, seed=3, key="fhSm")}</g>')
    d.add(el.fog(d, W, H - 40, 70, seed=17, dur=60, opacity=.16, color="#9C7FD6", name="fhFog"), C.vignette(d, W, H, "fhV", .45))
    # title block
    k, _ = text_use(d, "// CHAMBER 03  •  THE PORTAL CHAMBER", 56, 62, 12, "ui6", tracking=.34, fill=P.ice)
    tp, tw = text_path("FLASHDROP", 56, 128, 64, "cinzel9", tracking=.08)
    dd = tp[len('<path d="'):-3]
    ice = linear(d, "fhIce", [(0, "#FFFFFF"), (.55, "#EDE7FF"), (1, P.ice)], 0, 80, 0, 128, units="userSpaceOnUse")
    d.defs("fhBlur", '<filter id="fhBlur" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="9"/></filter>')
    d.add(k, f'<path d="{dd}" fill="{P.primary}" filter="url(#fhBlur)" style="animation:heroFlicker 8s infinite"/><path d="{dd}" fill="{ice}"/>')
    d.keyframes("heroFlicker", "0%,18%,22%,24%,53%,57%,100%{opacity:.9}20%,23%,55%{opacity:.35}")
    p1, w1 = status_pill(d, 58, 150, "FINAL YEAR PROJECT", color=P.glow)
    p2, _ = status_pill(d, 68 + w1, 150, "IN DEVELOPMENT", color=P.ice)
    sub, _ = text_use(d, FLASHDROP["concept"], 58, 206, 19, "ui5", fill=P.text)
    plat, _ = text_use(d, "  •  ".join(FLASHDROP["platforms"]).upper(), 58, 234, 12.5, "ui6", tracking=.3, fill=P.text2)
    d.add(p1, p2, sub, plat)
    d.add("</g>", over)
    return d


STATES = {"BUILT": ("BUILT", "solid"), "IN PROGRESS": ("IN PROGRESS", "pulse"), "PLANNED": ("PLANNED", "dashed")}


def hexagon(cx, cy, r):
    return "M" + "L".join(f"{n(cx + r * math.cos(math.radians(60 * i - 90)))} {n(cy + r * math.sin(math.radians(60 * i - 90)))}" for i in range(6)) + "Z"


def transfer_network(built=(), in_progress=()) -> Doc:
    W, H = 1000, 446
    mods = FLASHDROP["modules"]
    state = lambda m: "BUILT" if m in built else "IN PROGRESS" if m in in_progress else "PLANNED"
    d = Doc(W, H, "FlashDrop module map", "FlashDrop modules and their status: " + "; ".join(f"{m} — {state(m).lower()}" for m in mods)
            + ". Example flow: Android to Windows, large file, no cable.")
    under, over = panel(d, W, H, "fn", 20, glow_at=(.42, .55))
    d.add(under, '<g clip-path="url(#fnClip)">')
    tb, _ = title_bar(d, 56, 52, "03", "ARCHITECTURE", "MODULE MAP", 30, key="fnTb")
    d.add(tb)
    hub, others = mods[0], mods[1:]
    hx, hy = 330, 262
    icons = {"FlashHub": "hub", "FlashSend": "send", "FlashReceive": "receive", "FlashGroup": "group", "FlashCloud": "cloud", "FlashAI": "brain"}
    d.keyframes("fnFlow", "to{stroke-dashoffset:-36}")
    d.keyframes("fnPulse", "0%,100%{opacity:.45}50%{opacity:1}")
    pos = [(hx + 200 * math.cos(math.radians(a)), hy + 118 * math.sin(math.radians(a))) for a in (-150, -90, -30, 30, 150)]
    for (mx, my) in pos:
        d.add(f'<path d="M{hx} {hy}L{n(mx)} {n(my)}" stroke="{P.deep}" stroke-width="2"/>'
              f'<path d="M{hx} {hy}L{n(mx)} {n(my)}" stroke="{P.glow}" stroke-width="1.6" stroke-dasharray="5 13" style="animation:fnFlow 1.4s linear infinite"/>')

    def node(m, cx, cy, r, side=False):
        st = state(m)
        g = radial(d, "fnHex", [(0, "#371168"), (1, "#130920")], .5, .4, .7)
        dash = ' stroke-dasharray="5 4"' if st == "PLANNED" else ""
        anim = ' style="animation:fnPulse 1.8s ease-in-out infinite"' if st == "IN PROGRESS" else ""
        col = P.glow if st != "PLANNED" else P.accent
        if side:   # label beside the node (keeps the vertical spoke clear)
            t, _ = text_use(d, m, cx + r + 14, cy - 2, 13.5, "ui6", tracking=.08, fill=P.text)
            s, _ = text_use(d, STATES[st][0], cx + r + 14, cy + 16, 9.5, "ui6", tracking=.3, fill=col)
        else:
            t, _ = text_use(d, m, cx, cy + r + 20, 13.5, "ui6", anchor="middle", tracking=.08, fill=P.text)
            s, _ = text_use(d, STATES[st][0], cx, cy + r + 38, 9.5, "ui6", anchor="middle", tracking=.3, fill=col)
        return (f'<path d="{hexagon(cx, cy, r)}" fill="{g}" stroke="{col}" stroke-width="1.8"{dash}{anim}/>'
                + sigil(icons[m], cx, cy, r / 30, P.glow, 1.6) + t + s)

    for i, (m, (mx, my)) in enumerate(zip(others, pos)):
        d.add(node(m, mx, my, 30, side=(i == 1)))
    d.add(node(hub, hx, hy, 44))
    # example flow on the right
    x0 = 640
    d.add(f'<rect x="{x0}" y="112" width="322" height="270" rx="14" fill="#180C28" stroke="#511D96"/>')
    et, _ = text_use(d, "EXAMPLE TRANSFER", x0 + 22, 142, 11.5, "ui6", tracking=.32, fill=P.glow)
    d.add(et)
    steps = [("phone", "Android", "source device"), ("send", "FlashSend  →  FlashReceive", "peer-to-peer / local network"),
             ("monitor", "Windows", "destination device"), ("doc", "Large file · no cable", "design goal")]
    for i, (ic, a, b) in enumerate(steps):
        yy = 180 + i * 50
        ta, _ = text_use(d, a, x0 + 66, yy + 2, 15.5, "ui5", fill=P.text)
        tb2, _ = text_use(d, b, x0 + 66, yy + 21, 11.5, "ui4", fill=P.text2)
        d.add(f'<circle cx="{x0 + 38}" cy="{yy + 4}" r="16" fill="#261240" stroke="{P.accent}"/>' + sigil(ic, x0 + 38, yy + 4, .5, P.glow, 1.4) + ta + tb2)
        if i < 3:
            d.add(f'<path d="M{x0 + 38} {yy + 22}L{x0 + 38} {yy + 34}" stroke="{P.glow}" stroke-width="1.4" stroke-dasharray="2 3"/>')
    lg, _ = text_use(d, "SOLID = BUILT   •   PULSING = IN PROGRESS   •   DASHED = PLANNED", 330, H - 26, 10, "ui6", anchor="middle", tracking=.24, fill=P.muted)
    d.add(lg, "</g>", over)
    return d


def qr_matrix(data: str):
    import qrcode
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(data)
    q.make(fit=True)
    return q.get_matrix()


def qr_transfer(url: str) -> Doc:
    W, H = 1000, 340
    d = Doc(W, H, "FlashDrop pairing flow", "FlashDrop pairing flow (design direction): scan a QR code, pair devices peer-to-peer over Wi-Fi / local network, "
            "then transfer. Technology direction: " + ", ".join(FLASHDROP["direction"]) + f". The QR code on this card opens {url}.")
    under, over = panel(d, W, H, "fq", 20, glow_at=(.2, .5))
    d.add(under, '<g clip-path="url(#fqClip)">')
    # real QR code (opens your GitHub profile)
    m = qr_matrix(url)
    size, qx, qy = 190, 56, 72
    cell = size / len(m)
    cells = "".join(f"M{n(qx + c * cell, 2)} {n(qy + r * cell, 2)}h{n(cell, 2)}v{n(cell, 2)}h{n(-cell, 2)}z" for r, row in enumerate(m) for c, v in enumerate(row) if v)
    d.keyframes("fqScan", f"0%,100%{{transform:translateY(0)}}50%{{transform:translateY({size - 4}px)}}")
    d.add(f'<rect x="{qx - 14}" y="{qy - 14}" width="{size + 28}" height="{size + 28}" rx="12" fill="#F5F3FF"/>'
          f'<path d="{cells}" fill="#020203"/>'
          f'<rect x="{qx - 14}" y="{qy}" width="{size + 28}" height="3" fill="{P.glow}" opacity=".85" style="animation:fqScan 3s ease-in-out infinite"/>'
          f'<rect x="{qx - 20}" y="{qy - 20}" width="{size + 40}" height="{size + 40}" rx="16" fill="none" stroke="{P.glow}" stroke-width="1.6"/>')
    cap, _ = text_use(d, "SCAN → GITHUB PROFILE", qx + size / 2, qy + size + 42, 10.5, "ui6", anchor="middle", tracking=.3, fill=P.text2)
    d.add(cap)
    tb, _ = title_bar(d, 330, 52, "03", "DESIGN DIRECTION", "PAIRING FLOW", 30, key="fqTb")
    d.add(tb)
    steps = [("qr", "01  SCAN", "QR-based device pairing"), ("hub", "02  PAIR", "P2P over Wi-Fi / LAN"), ("send", "03  TRANSFER", "send ⇄ receive, no cable")]
    d.keyframes("fqStep", "0%,28%{opacity:1}34%,100%{opacity:.35}")
    for i, (ic, a, b) in enumerate(steps):
        x = 330 + i * 214
        d.add(f'<g style="animation:fqStep 6s {i * 2}s infinite;opacity:.35">'
              f'<rect x="{x}" y="138" width="196" height="92" rx="12" fill="#180C28" stroke="{P.glow}" stroke-opacity=".8"/>'
              + sigil(ic, x + 34, 184, .8, P.glow, 1.6))
        ta, _ = text_use(d, a, x + 62, 176, 15, "ui6", tracking=.14, fill=P.text)
        b2 = b.replace("⇄", "↔")
        tb3, _ = text_use(d, b2, x + 62, 198, 11.5, "ui4", fill=P.text2)
        d.add(ta, tb3, "</g>")
        if i < 2:
            d.add(f'<path d="M{x + 200} 184L{x + 212} 184" stroke="{P.glow}" stroke-width="2"/>')
    dl, _ = text_use(d, "TECHNOLOGY DIRECTION", 330, 262, 11, "ui6", tracking=.32, fill=P.glow)
    chips, _ = flow_chips(d, 330, 274, FLASHDROP["direction"], 640, size=13.5, h=30, row_h=38)
    d.add(dl, chips, "</g>", over)
    return d
