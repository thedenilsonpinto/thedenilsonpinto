#!/usr/bin/env python3
"""Summon the Midnight AI Lab — rebuild every SVG and the README from the config block.

  pip install -r forge/requirements.txt
  python forge/summon.py                    # rebuild all assets + README.md
  python forge/summon.py --only projects    # rebuild matching assets only (README untouched)
  python forge/summon.py --force-readme     # overwrite README.md even if you hand-edited it

What it does
  1. Reads the "MIDNIGHT AI LAB CONFIG" comment at the top of README.md (name, title,
     links, colours, FlashDrop module status…). Facts (projects, skills, experience…)
     live in forge/vampire/data.py.
  2. Re-renders every SVG in assets/ (it never touches the live stats in assets/github/;
     it only creates "awaiting first run" placeholders when they're missing).
  3. Regenerates README.md below the config block. Anything between the CUSTOM:START /
     CUSTOM:END markers is kept. If you edited the README body by hand, it is NOT
     overwritten: the new version goes to forge/README.generated.md instead.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vampire import config, palette  # noqa: E402
from vampire.data import title_case  # noqa: E402


def split_name(name: str) -> tuple[str, str]:
    words = name.split()
    if len(words) < 2:
        return name, ""
    best = min(range(1, len(words)), key=lambda i: max(len(" ".join(words[:i])), len(" ".join(words[i:]))))
    return " ".join(words[:best]), " ".join(words[best:])


def apply_facts(cfg: dict) -> None:
    """Push config values into the shared fact tables before rendering."""
    from vampire import data
    title = title_case(cfg["TITLE"])
    data.PROFILE.update(name=cfg["DISPLAY_NAME"], title=cfg["TITLE"], specialties=cfg["SPECIALTIES"],
                        headline=f"{title} • {cfg['SPECIALTIES']}")
    data.TERMINAL[0] = ("whoami", [title])


def jobs(cfg: dict) -> list[tuple[str, callable]]:
    from vampire import chronicle, flashdrop, hero, midnight, navkit, pulse, scenes, sheet, vault
    from vampire.data import PROJECTS

    name, user = cfg["DISPLAY_NAME"].strip(), cfg["GITHUB_USERNAME"].strip()
    first = (name.split() or ["engineer"])[0].lower()
    J = [("sections/hero.svg", lambda: hero.hero(split_name(name), cfg["TITLE"], (cfg["SPECIALTIES"], cfg["SPECIALTIES_2"]),
                                                 (cfg["TAGLINE"], cfg["TAGLINE_2"]), cfg["STATUS"])),
         ("sections/awakening.svg", scenes.awakening),
         ("sections/about.svg", midnight.about),
         ("sections/ai-lab.svg", midnight.ai_lab),
         ("sections/transition-void-walker.svg", lambda: scenes.void_walker("THE PORTAL CHAMBER")),
         ("sections/flashdrop.svg", flashdrop.flashdrop_hero),
         ("sections/flashdrop-modules.svg", lambda: flashdrop.transfer_network(cfg["_BUILT"], cfg["_IN_PROGRESS"])),
         ("sections/flashdrop-pairing.svg", lambda: flashdrop.qr_transfer(f"https://github.com/{user}")),
         ("sections/projects.svg", vault.projects_header)]
    for i, p in enumerate(PROJECTS, 1):
        live = bool(p["demo"] and cfg.get(p["demo"]))
        J.append((f"sections/projects/{p['key']}.svg", lambda p=p, i=i, live=live: vault.project_card(p, i, user, live)))
    J += [("sections/skills.svg", midnight.skills),
          ("sections/transition-teleport.svg", lambda: scenes.teleport("THE TIME CHAMBER")),
          ("sections/experience.svg", chronicle.experience),
          ("sections/education.svg", chronicle.education),
          ("sections/certifications.svg", chronicle.certifications),
          ("sections/github.svg", pulse.pulse_header),
          ("sections/terminal.svg", lambda: scenes.terminal(first)),
          ("sections/contact.svg", lambda: scenes.contact(user, cfg["LINKEDIN_URL"], cfg["EMAIL"])),
          ("sections/footer.svg", lambda: scenes.footer(name, cfg["TITLE"], cfg["TAGLINE_2"])),
          ("vampire/model-sheet.svg", sheet.model_sheet),
          ("vampire/scene-roster.svg", sheet.roster)]
    for num, rel, *_ in sheet.SCENES:                      # the character alone, transparent, one per scene
        J.append((f"vampire/{rel}", lambda num=num: sheet.scene_asset(num)))
    for i, (label, ic) in enumerate(navkit.NAV):
        J.append((f"icons/nav-{label.lower()}.svg", lambda l=label, c=ic, k=i: navkit.nav_button(l, c, k)))
    li = cfg["LINKEDIN_URL"].rstrip("/").split("linkedin.com/")[-1]
    J += [("icons/top.svg", navkit.top_button),
          ("icons/code.svg", lambda: navkit.link_button("VIEW CODE", "github", "View code on GitHub")),
          ("icons/demo.svg", lambda: navkit.link_button("LIVE DEMO", "sigil:play", "Open the live demo")),
          ("icons/site.svg", lambda: navkit.link_button("LIVE SITE", "sigil:globe", "Open the live site")),
          ("icons/github.svg", lambda: navkit.contact_button("GITHUB", "github", f"@{user}", f"GitHub — @{user}")),
          ("icons/linkedin.svg", lambda: navkit.contact_button("LINKEDIN", "sigil:network", li, "LinkedIn")),
          ("icons/email.svg", lambda: navkit.contact_button("EMAIL", "sigil:mail", cfg["EMAIL"] or "email", "Email")),
          ("effects/loader.svg", lambda: navkit.loader(name)),
          ("effects/divider.svg", navkit.divider),
          ("effects/fog.svg", navkit.fx_fog),
          ("effects/particles.svg", navkit.fx_particles),
          ("effects/shadows.svg", navkit.fx_shadows),
          ("effects/violet-glow.svg", navkit.fx_violet_glow),
          ("effects/bats.svg", navkit.fx_bats)]
    return J


# ── README ─────────────────────────────────────────────────────────────────────

CUSTOM_START, CUSTOM_END = "<!-- CUSTOM:START -->", "<!-- CUSTOM:END -->"
DEFAULT_CUSTOM = (f"{CUSTOM_START}\n<!-- Anything you write between these two markers survives every rebuild. -->\n{CUSTOM_END}")


def readme_body(cfg: dict, custom: str) -> str:
    from vampire.data import EDUCATION, EXPERIENCE, FLASHDROP, PROFILE, PROJECTS, SKILLS
    from vampire import navkit
    user, name = cfg["GITHUB_USERNAME"], cfg["DISPLAY_NAME"]
    title = title_case(cfg["TITLE"])
    NAMES = {"FLASHDROP": "FlashDrop", "GITHUB": "GitHub"}
    img = lambda src, alt, w="100%": f'<img src="./assets/{src}" width="{w}" alt="{alt}">'
    btn = lambda href, src, alt, h: f'<a href="{href}"><img src="./assets/{src}" height="{h}" alt="{alt}"></a>'
    nav = lambda items: "\n".join(btn(f"#{label.lower()}", f"icons/nav-{label.lower()}.svg", NAMES.get(label, label.title()), 36)
                                  for label, _ in items)
    L = ['<a name="top"></a>', '<div align="center">', "",
         img("effects/loader.svg", "The Midnight AI Lab — boot sequence"), "",
         img("sections/hero.svg", f"{name} — {title}. {cfg['SPECIALTIES']}. {cfg['SPECIALTIES_2']}. {cfg['TAGLINE']}"), "",
         nav(navkit.NAV[:4]) + "\n<br>\n" + nav(navkit.NAV[4:]), "",
         img("effects/divider.svg", ""), "",
         img("sections/awakening.svg", "Prologue: the Midnight AI Lab — an original vampire guardian awakens; every chamber below holds part of my work"), "",
         '<a name="about"></a>', "",
         img("sections/about.svg", f"The Shadow Chamber — about {name}, {title}. {PROFILE['summary']}"), "",
         img("sections/ai-lab.svg", "The AI Laboratory — current mission: FlashDrop, final year project, in development; "
             "focus on AI applications, Machine Learning, LLMs and Generative AI"), "",
         img("sections/transition-void-walker.svg", "Passage: the vampire walks out of the fog toward the Portal Chamber"), "",
         '<a name="flashdrop"></a>', "",
         img("sections/flashdrop.svg", "The Portal Chamber — FlashDrop, final year project, in development: cross-platform "
             "high-speed file sharing between Android, iOS, Windows and macOS without a cable"), "",
         img("sections/flashdrop-modules.svg", "FlashDrop module map: " + ", ".join(FLASHDROP["modules"])), "",
         img("sections/flashdrop-pairing.svg", "FlashDrop pairing flow: scan, pair, transfer"), "",
         "<sub><b>FlashDrop is my final year project and is still in development</b> — the module map marks what is "
         "planned, in progress and built.</sub>", "",
         '<a name="projects"></a>', "",
         img("sections/projects.svg", "The Command Room — project vault: six public repositories"), ""]
    for p in PROJECTS:
        L += [img(f"sections/projects/{p['key']}.svg", f"{p['name']} — {p['tagline']}"), ""]
        row = [btn(f"https://github.com/{user}/{p['repo']}", "icons/code.svg", f"View code — {p['name']}", 44)]
        if p["demo"] and cfg.get(p["demo"]):
            src = "icons/site.svg" if p["demo_label"] == "LIVE SITE" else "icons/demo.svg"
            row.append(btn(cfg[p["demo"]], src, f"{p['demo_label'].title()} — {p['name']}", 44))
        L += ["\n".join(row), ""]
    L += ['<a name="skills"></a>', "",
          img("sections/skills.svg", "The Data Chamber — skill matrix: " + ", ".join(title_case(c) for c, _ in SKILLS)), "",
          img("sections/transition-teleport.svg", "Passage: the vampire dissolves into the void and reappears in the Time Chamber"), "",
          '<a name="experience"></a>', "",
          img("sections/experience.svg", "The Time Chamber — experience: " + ", ".join(f"{c} ({r}, {y})" for y, c, r, _ in EXPERIENCE)), "",
          '<a name="education"></a>', "",
          img("sections/education.svg", "The Ancient Library — education: "
              + " and ".join(f"{deg} ({yr.replace(' — ', '–')})" for yr, deg, _, _ in EDUCATION)), "",
          img("sections/certifications.svg", "Certifications"), "",
          '<a name="github"></a>', "",
          img("sections/github.svg", "The Digital Observatory — GitHub activity (live cards below)"), "",
          img("github/stats.svg", "GitHub statistics"), "",
          img("github/streak.svg", "Contribution streak", "49%") + "\n" + img("github/languages.svg", "Top languages", "49%"), "",
          img("github/contributions.svg", "Contribution calendar"), "",
          img("github/snake.svg", "Contribution snake"), "",
          "<sub>Live data from the GitHub API — refreshed nightly by the <b>GitHub Pulse</b> workflow. "
          "The glowing grid in the observatory is decoration, not data.</sub>", "",
          img("sections/terminal.svg", "The Code Crypt — midnight terminal: whoami, focus, project, status, environment"), "",
          '<a name="contact"></a>', "",
          img("sections/contact.svg", "The Castle Gate — contact channels"), ""]
    contact = [btn(f"https://github.com/{user}", "icons/github.svg", f"GitHub @{user}", 52)]
    if cfg["LINKEDIN_URL"]:
        contact.append(btn(cfg["LINKEDIN_URL"], "icons/linkedin.svg", "LinkedIn", 52))
    if cfg["EMAIL"]:
        contact.append(btn(f"mailto:{cfg['EMAIL']}", "icons/email.svg", f"Email {cfg['EMAIL']}", 52))
    L += ["\n".join(contact), "",
          "<details>", "<summary><b>Meet the guardian</b> — the original character of the Midnight AI Lab</summary>", "<br>", "",
          img("vampire/model-sheet.svg", "Master character sheet of the Midnight AI Vampire, an original character"), "",
          img("vampire/scene-roster.svg", "Scene roster: the same vampire in all fifteen scenes, each with the power of its chamber"), "",
          "</details>", "",
          custom, "",
          img("sections/footer.svg", f"{name} — {title}. Until the next midnight."), "",
          btn("#top", "icons/top.svg", "Back to top", 36), "",
          "</div>", ""]
    return "\n".join(L)


def write_readme(cfg: dict, force: bool = False) -> str:
    text = config.README.read_text(encoding="utf-8") if config.README.exists() else ""
    m = config.BLOCK_RE.search(text)
    head = text[:m.end()] if m else config.block(cfg)
    body_now = text[m.end():] if m else text
    c0, c1 = body_now.find(CUSTOM_START), body_now.find(CUSTOM_END)
    custom = body_now[c0:c1 + len(CUSTOM_END)] if 0 <= c0 < c1 else DEFAULT_CUSTOM
    body = "\n\n" + readme_body(cfg, custom)

    def digest(s: str) -> str:               # custom-block edits don't count as hand edits
        i, j = s.find(CUSTOM_START), s.find(CUSTOM_END)
        if 0 <= i < j:
            s = s[:i] + s[j + len(CUSTOM_END):]
        return hashlib.sha256(s.strip().encode()).hexdigest()
    last = config.load_state().get("_readme_sha")
    untouched = not body_now.strip() or last is None or digest(body_now) == last or digest(body_now) == digest(body)
    if untouched or force:
        config.README.write_text(head + body, encoding="utf-8")
        state = {k: v for k, v in cfg.items() if not k.startswith("_")}
        state["_readme_sha"] = digest(body)
        config.STATE.write_text(json.dumps(state, indent=2) + "\n")
        return "README.md regenerated"
    out = config.ROOT / "forge" / "README.generated.md"
    out.write_text(head + body, encoding="utf-8")
    return ("README.md was edited by hand, so it was left as is — the regenerated version is in "
            "forge/README.generated.md (use --force-readme to overwrite)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", help="substring filter on asset paths (skips the README)")
    ap.add_argument("--force-readme", action="store_true")
    a = ap.parse_args()
    cfg = config.read()
    palette.configure(cfg["PRIMARY_COLOR"], cfg["SECONDARY_COLOR"], cfg["ACCENT_COLOR"], cfg["GLOW_COLOR"], cfg["LAVENDER_COLOR"])
    apply_facts(cfg)
    assets = config.ROOT / "assets"
    t0, total = time.time(), 0
    for rel, fn in jobs(cfg):
        if a.only and not any(o in rel for o in a.only):
            continue
        size = fn().save(assets / rel)
        total += size
        print(f"  ◆ {rel:<46} {size / 1024:7.1f} KB")
    if not a.only:
        import github_pulse
        github_pulse.placeholders(force=False)
        print("  ◆", write_readme(cfg, a.force_readme))
    print(f"The Midnight AI Lab is summoned: {total / 1024:.0f} KB of SVG in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
