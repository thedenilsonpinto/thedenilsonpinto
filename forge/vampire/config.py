"""Reads the MIDNIGHT AI LAB CONFIG block at the top of README.md.

Edit the values there (not here); these are only the defaults.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # repo root
README = ROOT / "README.md"
STATE = ROOT / "forge" / ".summon-state.json"      # last applied config + README fingerprint

DEFAULTS = {
    "GITHUB_USERNAME": "thedenilsonpinto",
    "DISPLAY_NAME": "DENILSON PINTO B",
    "TITLE": "AI ENGINEER",
    "SPECIALTIES": "Machine Learning • LLMs • Generative AI",
    "SPECIALTIES_2": "Data Science • Software Development",
    "TAGLINE": "Building intelligent systems beyond the ordinary.",
    "TAGLINE_2": "AI, data and intelligent applications — built after dark.",
    "STATUS": "FINAL YEAR  •  BUILDING FLASHDROP",
    "EMAIL": "thedenilsonpinto@gmail.com",
    "LINKEDIN_URL": "https://linkedin.com/in/b-denilsonpinto",
    "RESUME_ANALYZER_DEMO": "https://smart-ai-resume-analyzer-pro-thedenilsonpinto.streamlit.app/",
    "CYBER_DETECTIVE_DEMO": "https://ai-cyber-detective-thedenilsonpinto.streamlit.app/",
    "TECHNOVA_SITE": "https://thedenilsonpinto.github.io/iste.csice.edu.in/",
    "FLASHDROP_BUILT": "",
    "FLASHDROP_IN_PROGRESS": "",
    "PRIMARY_COLOR": "#7C3AED",
    "SECONDARY_COLOR": "#241137",
    "ACCENT_COLOR": "#6D28D9",
    "GLOW_COLOR": "#8B5CF6",
    "LAVENDER_COLOR": "#C4B5FD",
}

# may be left empty on purpose (empty = hide that button / nothing marked yet)
OPTIONAL = {"EMAIL", "LINKEDIN_URL", "RESUME_ANALYZER_DEMO", "CYBER_DETECTIVE_DEMO", "TECHNOVA_SITE",
            "FLASHDROP_BUILT", "FLASHDROP_IN_PROGRESS"}
COLORS = ("PRIMARY_COLOR", "SECONDARY_COLOR", "ACCENT_COLOR", "GLOW_COLOR", "LAVENDER_COLOR")
URLS = ("LINKEDIN_URL", "RESUME_ANALYZER_DEMO", "CYBER_DETECTIVE_DEMO", "TECHNOVA_SITE")

BLOCK_RE = re.compile(r"<!--(?:(?!-->).)*?MIDNIGHT (?:AI LAB|CORE) CONFIG.*?-->", re.S)
LINE_RE = re.compile(r"^[ \t]*([A-Z][A-Z0-9_]+)[ \t]*=[ \t]*(.*?)[ \t]*$", re.M)


def modules(value: str) -> list[str]:
    """'FlashHub, FlashSend' → ['FlashHub', 'FlashSend'] (validated against the module list)."""
    from .data import FLASHDROP
    known = {m.lower(): m for m in FLASHDROP["modules"]}
    out = []
    for part in filter(None, (p.strip() for p in value.split(","))):
        if part.lower() not in known:
            raise SystemExit(f"config: unknown FlashDrop module {part!r} (use: {', '.join(FLASHDROP['modules'])})")
        out.append(known[part.lower()])
    return out


def read(readme: Path = README) -> dict:
    cfg = dict(DEFAULTS)
    if readme.exists():
        m = BLOCK_RE.search(readme.read_text(encoding="utf-8"))
        if m:
            for k, v in LINE_RE.findall(m.group(0)):
                if k in cfg and (v or k in OPTIONAL):
                    cfg[k] = v
    for k in COLORS:
        v = cfg[k].strip()
        if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", v):
            raise SystemExit(f"config: {k} must be a 6-digit hex colour, got {v!r}")
        cfg[k] = "#" + v.lstrip("#").upper()
    for k in URLS:
        if cfg[k] and not re.fullmatch(r"https://\S+", cfg[k]):
            raise SystemExit(f"config: {k} must be an https:// URL (or empty), got {cfg[k]!r}")
    if cfg["EMAIL"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", cfg["EMAIL"]):
        raise SystemExit(f"config: EMAIL doesn't look like an email address: {cfg['EMAIL']!r}")
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", cfg["GITHUB_USERNAME"]):
        raise SystemExit(f"config: GITHUB_USERNAME looks wrong: {cfg['GITHUB_USERNAME']!r}")
    cfg["_BUILT"] = modules(cfg["FLASHDROP_BUILT"])
    cfg["_IN_PROGRESS"] = [m for m in modules(cfg["FLASHDROP_IN_PROGRESS"]) if m not in cfg["_BUILT"]]
    return cfg


def block(cfg: dict | None = None) -> str:
    """A fresh config comment block (used when README.md has none)."""
    cfg = cfg or DEFAULTS
    w = max(len(k) for k in DEFAULTS)
    lines = "\n".join(f"{k:<{w}} = {cfg[k]}".rstrip() for k in DEFAULTS)
    return ("<!--\n  MIDNIGHT AI LAB CONFIG  ·  edit a value, commit, and the \"Summon the Midnight AI Lab\" workflow\n"
            "  rebuilds every SVG and this README. Leave optional links empty to hide their buttons.\n"
            "  FLASHDROP_BUILT / FLASHDROP_IN_PROGRESS: comma-separated module names, e.g. FlashHub, FlashSend\n\n"
            f"{lines}\n-->")


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def save_state(cfg: dict) -> None:
    STATE.write_text(json.dumps({k: v for k, v in cfg.items() if not k.startswith("_")}, indent=2) + "\n")
