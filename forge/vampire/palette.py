"""Colours — the Midnight AI Lab palette: black + dark violet + deep purple.
`configure()` re-skins everything from the README config block.
No red, bright blue, cyan, orange or gold anywhere (forge/validate.py enforces it)."""
from __future__ import annotations


def _rgb(h: str):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, round(v))):02X}" for v in rgb)


def mix(a: str, b: str, t: float) -> str:
    """Blend colour a toward b by t (0..1)."""
    ra, rb = _rgb(a), _rgb(b)
    return hexc([x + (y - x) * t for x, y in zip(ra, rb)])


class Palette(dict):
    __getattr__ = dict.__getitem__


P = Palette()


def configure(primary="#7C3AED", secondary="#241137", accent="#6D28D9", glow="#8B5CF6", ice="#C4B5FD"):
    P.clear()
    P.update(
        # night: black → deep violet (from the brief)
        bg0="#020203", bg1="#050507", bg2="#0B0712", bg3="#12091C", bg4="#1A0D26",
        line="#1E1230", line2="#2A1A40",
        navy="#12091C", navy2=secondary,
        # violet energy
        primary=primary, deep=mix(primary, "#020203", .45), accent=accent, glow=glow, ice=ice,
        lining=mix(primary, "#020203", .6),
        # ink
        text="#F5F3FF", text2="#B9AED6", muted="#7D7394", dim="#463E57",
        silver="#D6D2E2", steel="#8D86A3", iron="#3A3448",
        # the vampire: moonlit skin, black hair, black coat
        skin="#D9D2E6", skin2="#A89CBD", skin3="#5E5270",
        hair="#050407", hair2="#171220", streak="#2E2440",
        coat="#07060A", coat2="#0D0A13", coat3="#030204",
    )
    return P


configure()
