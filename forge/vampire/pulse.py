"""Sector 09 — GitHub Pulse: header panel + the live cards rendered from REAL data.

The numbers come only from github_pulse.py (GitHub GraphQL API, run by the
"GitHub Pulse" Action). Until the first run, placeholder cards say so — no fake stats.
"""
from __future__ import annotations

import datetime as dt
import math

from . import elements as el
from . import chamber as C
from . import mascot as M
from .core import Doc, glow_filter, linear, n
from .hud import panel, title_bar
from .ornament import diamond
from .palette import P
from .sigils import sigil
from .text import measure, text_path, text_use


def fmt(v: int) -> str:
    return f"{v:,}"


def _stamp(doc: Doc, data: dict, W: float, y: float, full: bool = True) -> str:
    txt = (f"UPDATED {data['generated_at']}  •  SOURCE: GITHUB GRAPHQL API  •  @{data['login']}" if full
           else f"UPDATED {data['generated_at']}")
    t, _ = text_use(doc, txt, W / 2, y, 9.5, "ui6", anchor="middle", tracking=.26, fill=P.dim)
    return t


def _kicker(doc: Doc, text: str, x: float, y: float, anchor: str = "middle") -> str:
    t, _ = text_use(doc, text, x, y, 11, "ui6", anchor=anchor, tracking=.34, fill=P.glow)
    return t


# ── header (built by summon.py) ────────────────────────────────────────────────

def pulse_header() -> Doc:
    """Scene 10 — GitHub Guardian: the vampire overlooks a glowing contribution-style grid (decorative)."""
    W, H = 1000, 400
    d = Doc(W, H, "The Digital Observatory — GitHub pulse",
            "Chamber 09: live GitHub activity. The cards below are generated from the GitHub API every night by a GitHub Action; "
            "nothing is estimated. Scene: in a dark observatory the vampire overlooks a decorative contribution-style grid.")
    under, over = panel(d, W, H, "gp", 20, grid_on=False, glow_at=(.5, .7))
    d.add(under, '<g clip-path="url(#gpClip)">')
    d.add(C.chamber(d, W, H, "gpC", floor_y=362, fog=False))
    # the observatory dome: arcs, constellations, a slow sweep
    d.keyframes("gpDome", "to{transform:rotate(360deg)}")
    d.add(el.stars(d, W, 260, 70, seed=91, avoid=[(360, 30, 960, 160)]),
          "".join(f'<ellipse cx="500" cy="420" rx="{r}" ry="{n(r * .7)}" fill="none" stroke="{P.glow}" stroke-width=".7" opacity="{op}"/>'
                  for r, op in ((560, .22), (470, .16), (380, .12))),
          f'<g style="transform-origin:500px 420px;animation:gpDome 90s linear infinite" opacity=".5">'
          + "".join(f'<path d="M500 420L{n(500 + 600 * math.cos(math.radians(a)))} {n(420 + 420 * math.sin(math.radians(a)))}" '
                    f'stroke="{P.glow}" stroke-width=".5" stroke-dasharray="2 10"/>' for a in range(180, 361, 20)) + "</g>")
    tb, _ = title_bar(d, 380, 52, "09", "THE DIGITAL OBSERVATORY", "GITHUB PULSE", 34, key="gpTb")
    sub, _ = text_use(d, "Live numbers from the GitHub API, refreshed every night by a GitHub Action.", 380, 146, 14.5, "ui5", fill=P.text2)
    d.add(tb, sub)
    # the floating contribution-style grid (POWER 08 — decorative, not data)
    gx, gy = 392, 186
    d.add(f'<rect x="{gx - 16}" y="{gy - 16}" width="{24 * 23 + 20}" height="{7 * 14 + 30}" rx="10" fill="#12091C" fill-opacity=".7" '
          f'stroke="{P.glow}" stroke-opacity=".45" stroke-width=".8"/>', C.contrib_grid(d, gx, gy, 38, 7, 11, 3, "gpG", 9))
    cap, _ = text_use(d, "DECORATIVE  •  THE REAL CALENDAR IS BELOW", gx - 8, gy + 7 * 14 + 30, 9.5, "ui6", tracking=.26, fill=P.muted)
    d.add(cap)
    for i, (x, y) in enumerate(((gx - 58, gy + 14), (gx - 84, gy + 70), (gx - 50, gy + 124))):   # between him and the grid
        d.add(f'<g transform="translate({x} {y})" opacity=".85" style="animation:gpLive {2 + i}s ease-in-out infinite">'
              + sigil("layers" if i != 1 else "code", 0, 0, .45, P.ice, 1.2) + "</g>")
    d.keyframes("gpLive", "0%,100%{opacity:.35}50%{opacity:1}")
    # the guardian, hands behind his back
    ax, fy, sc = 172, H - 30, .72
    d.add(f'<g transform="translate({ax} {fy}) scale({sc})">{M.aura(d, 120, 240, -250)}{M.figure(d, "guardian")}'
          f'{M.smoke(d, 260, -4, seed=21, key="gpSm")}</g>')
    d.add(el.fog(d, W, H - 16, 44, seed=13, dur=50, opacity=.14, color="#9C7FD6", name="gpFog"), C.vignette(d, W, H, "gpV", .4), "</g>", over)
    return d


# ── live cards (built by github_pulse.py) ───────────────────────────────────────

def stats(data: dict) -> Doc:
    W, H = 1000, 236
    tiles = [("pulse", fmt(data["contributions_year"]), "CONTRIBUTIONS", "last 12 months"),
             ("code", fmt(data["commits_year"]), "COMMITS", "last 12 months"),
             ("send", fmt(data["prs_year"]), "PULL REQUESTS", "last 12 months"),
             ("target", fmt(data["issues_year"]), "ISSUES", "last 12 months"),
             ("spark", fmt(data["stars"]), "STARS EARNED", "public repos"),
             ("layers", fmt(data["repos"]), "PUBLIC REPOS", f"{fmt(data['followers'])} followers")]
    d = Doc(W, H, "GitHub statistics",
            "GitHub stats for @" + data["login"] + ": " + "; ".join(f"{b} {a} ({c})" for _, a, b, c in tiles) + ".")
    under, over = panel(d, W, H, "st", 18, glow_at=(.5, .1))
    d.add(under, '<g clip-path="url(#stClip)">')
    tw, gap = 150, 11
    x0 = (W - 6 * tw - 5 * gap) / 2
    d.keyframes("stRise", "0%{opacity:0;transform:translateY(8px)}100%{opacity:1;transform:translateY(0)}")
    g = linear(d, "stT", [(0, "#26123E"), (1, "#0F0718")], 0, 0, 0, 1)
    for i, (ic, val, lab, sub) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        d.add(f'<g class="rv" style="opacity:0;animation:stRise .8s ease-out {i * .12:.2f}s forwards">'
              f'<rect x="{n(x)}" y="26" width="{tw}" height="170" rx="12" fill="{g}" stroke="#511D96"/>'
              f'<rect x="{n(x + 24)}" y="26" width="{tw - 48}" height="2" fill="{P.glow}"/>'
              f'<circle cx="{n(x + tw / 2)}" cy="62" r="19" fill="#211037" stroke="{P.accent}" stroke-opacity=".7"/>'
              + sigil(ic, x + tw / 2, 62, .6, P.glow, 1.5))
        size = 32
        while measure(val, "cinzel9", size) > tw - 16:
            size -= 1
        t1, _ = text_path(val, x + tw / 2, 122, size, "cinzel9", anchor="middle", fill=P.text)
        t2, _ = text_use(d, lab, x + tw / 2, 150, 10.5, "ui6", anchor="middle", tracking=.22, fill=P.glow)
        t3, _ = text_use(d, sub, x + tw / 2, 172, 12, "ui5", anchor="middle", fill=P.text2)
        d.add(t1, t2, t3, "</g>")
    d.add(_stamp(d, data, W, 220), "</g>", over)
    return d


def streak(data: dict) -> Doc:
    W, H = 490, 330
    cur, lng = data["streak_current"], data["streak_longest"]
    d = Doc(W, H, "Contribution streak", f"Current streak {cur} days; longest streak {lng} days; "
            f"{fmt(data['contributions_total'])} contributions since {data['first_year']}.")
    under, over = panel(d, W, H, "sr", 18, glow_at=(.5, .4))
    d.add(under, '<g clip-path="url(#srClip)">', _kicker(d, "CONTRIBUTION STREAK", W / 2, 40))
    cx, cy, r = W / 2, 146, 64
    frac = min(1.0, cur / max(1, lng)) if lng else 0
    circ = 2 * math.pi * r
    ring = linear(d, "srRing", [(0, P.ice), (1, P.primary)], 0, 0, 1, 1)
    d.keyframes("srDraw", f"from{{stroke-dashoffset:{n(circ)}}}to{{stroke-dashoffset:{n(circ * (1 - frac))}}}")
    d.add(f'<circle cx="{n(cx)}" cy="{cy}" r="{r}" fill="#130920" stroke="#2D164A" stroke-width="10"/>'
          f'<circle cx="{n(cx)}" cy="{cy}" r="{r}" fill="none" stroke="{ring}" stroke-width="10" stroke-linecap="round" '
          f'stroke-dasharray="{n(circ)}" stroke-dashoffset="{n(circ * (1 - frac))}" transform="rotate(-90 {n(cx)} {cy})" '
          f'style="animation:srDraw 1.6s ease-out"/>')
    t, _ = text_path(fmt(cur), cx, cy + 14, 44 if cur < 1000 else 34, "cinzel9", anchor="middle", fill=P.text)
    t2, _ = text_use(d, "CURRENT STREAK", cx, cy + 96, 11, "ui6", anchor="middle", tracking=.3, fill=P.glow)
    rng = data.get("streak_current_range") or "no contributions today — yet"
    t3, _ = text_use(d, rng, cx, cy + 118, 12.5, "ui5", anchor="middle", fill=P.text2)
    d.add(t, t2, t3)
    for sx, val, lab, sub in ((-1, fmt(data["contributions_total"]), "ALL-TIME", f"since {data['first_year']}"),
                              (1, fmt(lng), "LONGEST", data.get("streak_longest_range") or "—")):
        x = cx + sx * 172
        v, _ = text_path(val, x, 154, 28 if len(val) < 7 else 22, "cinzel9", anchor="middle", fill=P.text)
        lb, _ = text_use(d, lab, x, 180, 10.5, "ui6", anchor="middle", tracking=.3, fill=P.glow)
        ss = 11.5
        while measure(sub, "ui5", ss) > 130 and ss > 8.5:
            ss -= .5
        s_, _ = text_use(d, sub, x, 199, ss, "ui5", anchor="middle", fill=P.text2)
        d.add(v, lb, s_)
    d.add(_stamp(d, data, W, H - 18, full=False), "</g>", over)
    return d


def languages(data: dict) -> Doc:
    W, H = 490, 330
    langs = data["languages"][:6]
    d = Doc(W, H, "Top languages", "Top languages by code size in public, non-fork repositories: "
            + ", ".join(f"{lg['name']} {lg['pct']:.1f}%" for lg in langs) + ".")
    under, over = panel(d, W, H, "lg", 18, glow_at=(.5, .4))
    d.add(under, '<g clip-path="url(#lgClip)">', _kicker(d, "TOP LANGUAGES", W / 2, 40))
    shades = [P.glow, P.ice, P.accent, P.primary, "#50199A", "#684A8F"]
    if not langs:
        t, _ = text_use(d, "No public code found yet.", W / 2, 170, 16, "ui5", anchor="middle", fill=P.text2)
        d.add(t, "</g>", over)
        return d
    x, bx, bw = 36, 36, W - 72
    d.defs("lgBar", f'<clipPath id="lgBar"><rect x="{bx}" y="62" width="{bw}" height="14" rx="7"/></clipPath>')
    segs = []
    for i, lg in enumerate(langs):
        w = bw * lg["pct"] / 100
        segs.append(f'<rect x="{n(x)}" y="62" width="{n(max(w, .5))}" height="14" fill="{shades[i]}"/>')
        x += w
    d.add(f'<rect x="{bx}" y="62" width="{bw}" height="14" rx="7" fill="#2D164A"/><g clip-path="url(#lgBar)">{"".join(segs)}</g>')
    for i, lg in enumerate(langs):
        col, row = i % 2, i // 2
        lx, ly = 40 + col * 214, 118 + row * 58
        name = lg["name"]
        ns = 17
        while measure(name, "ui5", ns) > 120 and ns > 11:
            ns -= .5
        t1, _ = text_use(d, name, lx + 22, ly, ns, "ui5", fill=P.text)
        t2, _ = text_use(d, f"{lg['pct']:.1f}%", lx + 190, ly, 14, "mono7", anchor="end", fill=P.text2)
        d.add(diamond(lx + 6, ly - 5.5, 6, shades[i]), t1, t2,
              f'<rect x="{lx + 22}" y="{ly + 12}" width="168" height="3" rx="1.5" fill="#2D164A"/>'
              f'<rect x="{lx + 22}" y="{ly + 12}" width="{n(max(2, 168 * lg["pct"] / 100))}" height="3" rx="1.5" fill="{shades[i]}"/>')
    d.add(_stamp(d, data, W, H - 18, full=False), "</g>", over)
    return d


LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def calendar(data: dict) -> Doc:
    weeks = data["calendar"]           # list of weeks, each a list of {date, count, level}
    cs, gap = 13.5, 3.2
    W, H = 1000, 250
    gx = (W - (len(weeks) * (cs + gap) - gap)) / 2 + 12
    total = data["contributions_year"]
    d = Doc(W, H, "Contribution calendar", f"{fmt(total)} contributions in the last 12 months (GitHub contribution calendar for @{data['login']}).")
    under, over = panel(d, W, H, "cc", 18, glow_at=(.5, .2))
    d.add(under, '<g clip-path="url(#ccClip)">')
    colors = ["#180B27", "#371168", "#50199A", P.primary, P.glow]
    k, _ = text_path(f"{fmt(total)} CONTRIBUTIONS", 40, 46, 20, "cinzel9", tracking=.06, fill=P.text)
    k2, _ = text_use(d, "in the last 12 months", 40, 67, 13, "ui5", fill=P.text2)
    d.add(k, k2)
    months, last_m, y0, cells = [], None, 94, []
    for wi, wk in enumerate(weeks):
        for day in wk:
            date = dt.date.fromisoformat(day["date"])
            wd = (date.weekday() + 1) % 7            # Sunday = row 0
            lv = LEVELS.get(day.get("level", "NONE"), 0)
            x, y = gx + wi * (cs + gap), y0 + wd * (cs + gap)
            cells.append(f'<rect x="{n(x)}" y="{n(y)}" width="{cs}" height="{cs}" rx="3" fill="{colors[lv]}"/>')
            if date.day <= 7 and wd == 0 and date.month != last_m:
                months.append((x, date.strftime("%b").upper()))
                last_m = date.month
    d.add("".join(cells))
    for x, m in months:
        t, _ = text_use(d, m, x, y0 - 10, 10, "ui6", tracking=.12, fill=P.muted)
        d.add(t)
    for r, lab in ((1, "MON"), (3, "WED"), (5, "FRI")):
        t, _ = text_use(d, lab, gx - 10, y0 + r * (cs + gap) + 10, 9.5, "ui6", anchor="end", tracking=.1, fill=P.dim)
        d.add(t)
    if weeks and weeks[-1]:
        last = weeks[-1][-1]
        date = dt.date.fromisoformat(last["date"])
        wd = (date.weekday() + 1) % 7
        x, y = gx + (len(weeks) - 1) * (cs + gap) + cs / 2, y0 + wd * (cs + gap) + cs / 2
        d.keyframes("ccPing", "0%{transform:scale(.6);opacity:.9}100%{transform:scale(2.6);opacity:0}")
        d.add(f'<circle cx="{n(x)}" cy="{n(y)}" r="7" fill="none" stroke="{P.glow}" stroke-width="1.5" '
              f'style="transform-box:fill-box;transform-origin:center;animation:ccPing 2s ease-out infinite"/>')
    lx = W - 40 - 5 * (cs + 4) - 70
    lt, _ = text_use(d, "LESS", lx, 64, 9.5, "ui6", tracking=.2, fill=P.muted)
    d.add(lt, "".join(f'<rect x="{n(lx + 40 + i * (cs + 4))}" y="52" width="{cs}" height="{cs}" rx="3" fill="{c}"/>' for i, c in enumerate(colors)))
    mt, _ = text_use(d, "MORE", lx + 40 + 5 * (cs + 4) + 6, 64, 9.5, "ui6", tracking=.2, fill=P.muted)
    d.add(mt, _stamp(d, data, W, H - 14), "</g>", over)
    return d


def placeholder(title: str, what: str, W: float = 1000, H: float = 200) -> Doc:
    """Shown until the GitHub Pulse workflow runs for the first time. No fake numbers."""
    d = Doc(W, H, f"{title} — awaiting first run", f"{what} will appear after the 'GitHub Pulse' GitHub Action runs.")
    under, over = panel(d, W, H, "ph", 18, glow_at=(.5, .5))
    d.add(under)
    d.keyframes("phSpin", "to{transform:rotate(360deg)}")
    wide = W > 600
    cx, cy = (74, H / 2) if wide else (W / 2, 96)
    d.add(f'<g style="transform-origin:{n(cx)}px {n(cy)}px;animation:phSpin 6s linear infinite">'
          f'<circle cx="{n(cx)}" cy="{n(cy)}" r="27" fill="none" stroke="{P.glow}" stroke-width="2" stroke-dasharray="6 6"/></g>'
          + sigil("pulse", cx, cy, .72, P.glow, 1.6))
    if wide:
        t1, _ = text_path(title.upper(), 124, H / 2 - 6, 20, "cinzel9", tracking=.06, fill=P.text)
        t2, _ = text_use(d, f"Awaiting the first GitHub Pulse run — {what} will appear here.", 124, H / 2 + 20, 14, "ui5", fill=P.text2)
    else:
        t1, _ = text_path(title.upper(), W / 2, 160, 18, "cinzel9", anchor="middle", tracking=.06, fill=P.text)
        t2, _ = text_use(d, "Awaiting the first GitHub Pulse run.", W / 2, 186, 13.5, "ui5", anchor="middle", fill=P.text2)
    d.add(t1, t2, over)
    return d
