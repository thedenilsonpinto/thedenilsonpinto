"""SVG document builder: defs/CSS de-duplication, ids, compact numbers."""
from __future__ import annotations

import math
from xml.sax.saxutils import escape as _esc


def n(v: float, d: int = 1) -> str:
    """Compact number formatting (keeps files small)."""
    if isinstance(v, int):
        return str(v)
    r = round(float(v), d)
    if r == int(r):
        return str(int(r))
    s = f"{r:.{d}f}".rstrip("0").rstrip(".")
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return "0" if s in ("-0", "", "-") else s


def esc(s: str) -> str:
    return _esc(str(s), {'"': "&quot;"})


def attrs(**kw) -> str:
    """Render keyword args as SVG attributes (underscores become dashes)."""
    out = []
    for k, v in kw.items():
        if v is None or v is False:
            continue
        k = k.rstrip("_").replace("_", "-")
        if k == "href":
            pass
        out.append(f'{k}="{esc(n(v) if isinstance(v, float) else v)}"')
    return (" " + " ".join(out)) if out else ""


_TOK = __import__("re").compile(r"[MLHVCSQTAZmlhvcsqtaz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "Z": 0}


def compact_path(d: str, prec: int = 1) -> str:
    """Absolute path data → relative commands with minimal separators (~35% smaller).
    Rounding is done on absolute coordinates, so there is no drift."""
    toks = _TOK.findall(d)
    if not toks or any(t in "mlhvcsqtaA" for t in toks if t.isalpha()):
        return d
    out, i = [], 0
    cx = cy = sx = sy = 0.0
    R = lambda v: round(float(v), prec)
    cmd = None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == "Z":
                out.append("z")
                cx, cy = sx, sy
                continue
        k = _ARGS[cmd]
        vals = [R(v) for v in toks[i:i + k]]
        i += k
        if cmd == "H":
            out += ["h", vals[0] - cx]; cx = vals[0]
        elif cmd == "V":
            out += ["v", vals[0] - cy]; cy = vals[0]
        else:
            rel = []
            for j in range(0, k, 2):
                rel += [vals[j] - cx, vals[j + 1] - cy]
            out += [cmd.lower()] + rel
            cx, cy = vals[-2], vals[-1]
            if cmd == "M":
                sx, sy = cx, cy
                cmd = "L"
    res, prev = [], ""
    for t in out:
        if isinstance(t, str):
            res.append(t); prev = t; continue
        s_ = n(round(t, prec), prec)
        if prev and not prev.isalpha():
            if s_.startswith("-") or (s_.startswith(".") and "." in prev):
                pass
            else:
                res.append(" ")
        res.append(s_); prev = s_
    return "".join(res)


def pts(points, d: int = 1) -> str:
    return " ".join(f"{n(x, d)},{n(y, d)}" for x, y in points)


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


class Doc:
    """One SVG file. Collects <defs>, CSS rules and body fragments."""

    def __init__(self, w: float, h: float, title: str, desc: str = ""):
        self.w, self.h = w, h
        self.title, self.desc = title, desc
        self._defs: dict[str, str] = {}
        self._css: dict[str, str] = {}
        self.body: list[str] = []
        self._ids: dict[str, int] = {}
        self.glyph_defs: dict[str, str] = {}   # filled by text.py

    # ids ------------------------------------------------------------------
    def uid(self, prefix: str = "x") -> str:
        i = self._ids.get(prefix, 0)
        self._ids[prefix] = i + 1
        return f"{prefix}{i if i else ''}"

    # defs / css -------------------------------------------------------------
    def defs(self, key: str, svg: str) -> str:
        """Add a <defs> child once (keyed). Returns the key for convenience."""
        if key not in self._defs:
            self._defs[key] = svg
        return key

    def css(self, key: str, rule: str) -> None:
        if key not in self._css:
            self._css[key] = rule

    def keyframes(self, name: str, frames: str) -> str:
        self.css("@kf-" + name, f"@keyframes {name}{{{frames}}}")
        return name

    def add(self, *frags: str) -> None:
        self.body.extend(f for f in frags if f)

    # render -----------------------------------------------------------------
    def render(self) -> str:
        css = "".join(self._css.values())
        css += "@media (prefers-reduced-motion:reduce){*{animation:none!important}.rv{opacity:1!important}}"
        defs = "".join(self._defs.values()) + "".join(self.glyph_defs.values())
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(self.w)} {n(self.h)}" '
            f'width="{n(self.w)}" height="{n(self.h)}" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc or self.title)}</desc>'
        )
        return head + f"<style>{css}</style>" + (f"<defs>{defs}</defs>" if defs else "") + "".join(self.body) + "</svg>"

    def save(self, path) -> int:
        from pathlib import Path
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = self.render()
        p.write_text(data, encoding="utf-8")
        return len(data.encode("utf-8"))


# ── Reusable paint servers & filters ───────────────────────────────────────────

def linear(doc: Doc, key: str, stops, x1=0, y1=0, x2=0, y2=1, units=None) -> str:
    """stops: [(offset, color, opacity?), ...] → returns url(#key)."""
    s = "".join(
        f'<stop offset="{n(o, 3)}" stop-color="{c}"' + (f' stop-opacity="{n(a, 3)}"' if len(st) > 2 and (a := st[2]) != 1 else "") + "/>"
        for st in stops for (o, c) in [st[:2]]
    )
    u = f' gradientUnits="{units}"' if units else ""
    doc.defs(key, f'<linearGradient id="{key}" x1="{n(x1, 3)}" y1="{n(y1, 3)}" x2="{n(x2, 3)}" y2="{n(y2, 3)}"{u}>{s}</linearGradient>')
    return f"url(#{key})"


def radial(doc: Doc, key: str, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, units=None) -> str:
    s = "".join(
        f'<stop offset="{n(o, 3)}" stop-color="{c}"' + (f' stop-opacity="{n(a, 3)}"' if len(st) > 2 and (a := st[2]) != 1 else "") + "/>"
        for st in stops for (o, c) in [st[:2]]
    )
    u = f' gradientUnits="{units}"' if units else ""
    f = (f' fx="{n(fx, 3)}"' if fx is not None else "") + (f' fy="{n(fy, 3)}"' if fy is not None else "")
    doc.defs(key, f'<radialGradient id="{key}" cx="{n(cx, 3)}" cy="{n(cy, 3)}" r="{n(r, 3)}"{f}{u}>{s}</radialGradient>')
    return f"url(#{key})"


def glow_filter(doc: Doc, key: str, blur: float = 4, strength: int = 1, color: str | None = None) -> str:
    """Soft outer glow that keeps the source crisp on top."""
    col = (f'<feFlood flood-color="{color}"/><feComposite in2="b" operator="in" result="b"/>' if color else "")
    merges = "".join('<feMergeNode in="b"/>' for _ in range(strength))
    doc.defs(key, (
        f'<filter id="{key}" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">'
        f'<feGaussianBlur in="SourceGraphic" stdDeviation="{n(blur)}" result="b"/>{col}'
        f'<feMerge>{merges}<feMergeNode in="SourceGraphic"/></feMerge></filter>'
    ))
    return f"url(#{key})"


def blur_filter(doc: Doc, key: str, blur: float = 6) -> str:
    doc.defs(key, f'<filter id="{key}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{n(blur)}"/></filter>')
    return f"url(#{key})"
