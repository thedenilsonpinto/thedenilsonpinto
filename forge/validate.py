#!/usr/bin/env python3
"""Validate the Midnight AI Lab before it goes live (stdlib only).

  python forge/validate.py           # exit 1 on any error

Checks
  • README config block parses (colours, URLs, email, FlashDrop module names)
  • every ./assets/… image in README.md exists; every #anchor has a target
  • README uses only markup GitHub keeps (no style=/class=/script/iframe), tags balanced,
    no '--' inside HTML comments
  • every SVG is well-formed, has a viewBox and <title>, and is GitHub-safe: no <script>,
    no <foreignObject>, no event handlers, no external http(s) references
  • palette guard: black + violet only — no red, orange, gold, cyan or bright blue in any SVG
  • size budget: warns above 200 KB per SVG
"""
from __future__ import annotations

import colorsys
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vampire import config  # noqa: E402

ROOT = config.ROOT
SVG_NS = "{http://www.w3.org/2000/svg}"
errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def check_readme() -> int:
    if not config.README.exists():
        err("README.md is missing")
        return 0
    text = config.README.read_text(encoding="utf-8")
    try:
        config.read()
    except SystemExit as e:
        err(f"config block: {e}")
    if not config.BLOCK_RE.search(text):
        warnings.append("README: no MIDNIGHT AI LAB CONFIG block (defaults are used)")
    refs = re.findall(r'src="\./(assets/[^"]+)"', text)
    for r in refs:
        if not (ROOT / r).exists():
            err(f"README references missing file: {r}")
    live = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    for bad, why in ((r"\sstyle=", "style= is stripped by GitHub"), (r"\sclass=", "class= is stripped by GitHub"),
                     (r"<script", "scripts never run on GitHub"), (r"<iframe", "iframes are not allowed"),
                     (r"#gh-(dark|light)-mode-only", "deprecated theme fragment; use <picture>")):
        if re.search(bad, live):
            err(f"README: {why}")
    for m in re.finditer(r"<!--(.*?)-->", text, re.S):
        if "--" in m.group(1):
            err("README: '--' inside an HTML comment")
    names = set(re.findall(r'<a (?:name|id)="([\w-]+)"', text))
    for t in set(re.findall(r'href="#([\w-]+)"', text)):
        if t not in names:
            err(f"README: link to #{t} has no matching anchor")
    for tag in ("div", "details", "summary", "a", "p", "sub"):
        o, c = len(re.findall(rf"<{tag}[\s>]", live)), len(re.findall(rf"</{tag}>", live))
        if o != c:
            err(f"README: <{tag}> opened {o}× but closed {c}×")
    for m in re.finditer(r'<img\b[^>]*>', live):
        if "alt=" not in m.group(0):
            warnings.append(f"README: image without alt text: {m.group(0)[:70]}")
    return len(refs)


HEX = re.compile(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")


def off_palette(hex6: str) -> bool:
    """The Midnight AI Lab allows neutrals + violets only: a saturated colour must sit in
    the violet/purple hue band (245°–300°). Rejects red, orange, gold, cyan and bright blue."""
    h = hex6 if len(hex6) == 6 else "".join(c * 2 for c in hex6)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    if sat < .18 or light < .05 or light > .97:
        return False
    return not (245 <= hue * 360 <= 300)


def check_svg(path: Path) -> None:
    rel = path.relative_to(ROOT)
    raw = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        err(f"{rel}: not well-formed XML ({e})")
        return
    if root.tag != SVG_NS + "svg":
        err(f"{rel}: root element is not <svg>")
    if "viewBox" not in root.attrib:
        err(f"{rel}: missing viewBox (needed to scale with width=100%)")
    if root.find(SVG_NS + "title") is None:
        warnings.append(f"{rel}: no <title> (accessibility)")
    for el in root.iter():
        tag = el.tag.replace(SVG_NS, "")
        if tag in ("script", "foreignObject", "iframe"):
            err(f"{rel}: <{tag}> is not allowed")
        for k, v in el.attrib.items():
            if k.lower().startswith("on"):
                err(f"{rel}: event handler attribute {k}")
            if k.endswith("href") and v.startswith(("http:", "https:", "//")):
                err(f"{rel}: external reference {v[:60]} (blocked inside README images)")
    if re.search(r"@import|url\((['\"]?)https?:", raw):
        err(f"{rel}: external CSS/font reference (blocked inside README images)")
    text_only = re.sub(r'href="data:[^"]*"', "", raw)          # embedded artwork pixels are exempt
    hot = sorted({h for h in HEX.findall(text_only) if off_palette(h)})
    if hot and "github/snake" not in str(rel).replace("\\", "/"):
        err(f"{rel}: off-palette colours (only black + violet allowed): {', '.join('#' + h for h in hot[:6])}")
    kb = len(raw.encode()) / 1024
    if kb > 200:
        warnings.append(f"{rel}: {kb:.0f} KB (consider simplifying)")


def main() -> None:
    n_refs = check_readme()
    svgs = sorted((ROOT / "assets").rglob("*.svg"))
    for p in svgs:
        check_svg(p)
    total = sum(p.stat().st_size for p in svgs) / 1024
    for w in warnings:
        print("  ⚠ ", w)
    for e in errors:
        print("  ✖ ", e)
    print(f"validate: {len(svgs)} SVGs ({total:.0f} KB) · {n_refs} README images · "
          f"{len(errors)} error(s) · {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
