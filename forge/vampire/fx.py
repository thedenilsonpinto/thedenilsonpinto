"""Text effects: SMIL typewriter with exact per-glyph widths."""
from __future__ import annotations


from .core import Doc, n
from .palette import P
from .text import char_stops, face, text_use


def typewriter(doc: Doc, lines: list[str], x: float, y: float, size: float, font: str = "serif_i",
               fill: str | None = None, cps: float = 16, hold: float = 2.6, erase_cps: float = 38,
               gap: float = .35, caret: str | None = None, anchor: str = "start", key: str = "tw") -> str:
    """Types each line, holds, erases, then the next — forever. Uses SMIL
    <animate calcMode="discrete"> on clip rects, so every step lands exactly
    on a glyph boundary (CSS steps() can't do that with proportional fonts)."""
    fill = fill or P.text
    caret = caret or P.glow
    f = face(font)
    asc, desc = f.ascent * size / f.upem, size * .32
    plans, T = [], 0.0
    for ln in lines:
        stops = [0.0] + char_stops(ln, font, size)
        t_type, t_erase = len(ln) / cps, len(ln) / erase_cps
        plans.append((ln, stops, T, t_type, t_erase))
        T += t_type + hold + t_erase + gap
    parts, caret_vals, caret_times = [], [], []
    for i, (ln, stops, t0, tt, te) in enumerate(plans):
        w = stops[-1]
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        vals, times = ["0"], [0.0]
        for k, sx in enumerate(stops):                       # typing
            times.append((t0 + tt * k / max(1, len(stops) - 1)) / T)
            vals.append(n(sx + (1 if k else 0), 1))
        for k in range(len(stops) - 1, -1, -1):              # erasing
            times.append((t0 + tt + hold + te * (len(stops) - 1 - k) / max(1, len(stops) - 1)) / T)
            vals.append(n(stops[k], 1))
        times.append(1.0)
        vals.append("0")
        # keyTimes must increase; nudge duplicates
        fixed, last = [], -1.0
        for t in times:
            t = max(t, last + 1e-4)
            fixed.append(min(t, 1.0))
            last = t
        fixed[-1] = 1.0
        cid = f"{key}C{i}"
        base = n(w + 4, 1) if i == 0 else "0"      # static frame (no SMIL): the first line, fully shown
        doc.defs(cid, f'<clipPath id="{cid}"><rect x="{n(x0 - 2)}" y="{n(y - asc - 6)}" height="{n(asc + desc + 12)}" width="{base}">'
                      f'<animate attributeName="width" dur="{n(T, 2)}s" repeatCount="indefinite" calcMode="discrete" '
                      f'keyTimes="{";".join(n(t, 4) for t in fixed)}" values="{";".join(vals)}"/></rect></clipPath>')
        txt, _ = text_use(doc, ln, x0, y, size, font, fill=fill)
        parts.append(f'<g clip-path="url(#{cid})">{txt}</g>')
        caret_times += fixed[1:-1]
        caret_vals += [n(x0 - 2 + float(v) + 3, 1) for v in vals[1:-1]]
    ct, cv, last = [0.0], [caret_vals[0]], 0.0
    for t, v in zip(caret_times, caret_vals):
        t = max(t, last + 1e-4)
        ct.append(min(t, .9999))
        cv.append(v)
        last = t
    ct.append(1.0)
    cv.append(cv[0])
    doc.keyframes("twBlink", "0%,49%{opacity:1}50%,100%{opacity:0}")
    parts.append(f'<rect y="{n(y - asc - 2)}" width="{n(max(2, size * .08))}" height="{n(asc + desc + 2)}" fill="{caret}" '
                 f'style="animation:twBlink 1s steps(1) infinite"><animate attributeName="x" dur="{n(T, 2)}s" repeatCount="indefinite" '
                 f'calcMode="discrete" keyTimes="{";".join(n(t, 4) for t in ct)}" values="{";".join(cv)}"/></rect>')
    return "".join(parts)
