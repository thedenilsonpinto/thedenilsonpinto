#!/usr/bin/env python3
"""GitHub Pulse — fetches REAL GitHub stats and renders the violet live cards.

Runs nightly in the "GitHub Pulse" Action with the workflow's GITHUB_TOKEN
(public data only). To also count private contributions, add a classic PAT with
`read:user` + `repo` scopes as the repository secret PULSE_TOKEN and enable
"Private contributions" on your GitHub profile.

  python forge/github_pulse.py                               # fetch + render → assets/github/
  python forge/github_pulse.py --frame-snake dist/snake.svg  # frame Platane/snk's output
  python forge/github_pulse.py --placeholders                # "awaiting first run" cards

Nothing is estimated: if the API call fails, the script exits with an error and
leaves the previous images untouched.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vampire import config, palette  # noqa: E402
from vampire import pulse as L       # noqa: E402

API = "https://api.github.com/graphql"
OUT = config.ROOT / "assets" / "github"

Q_MAIN = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    login
    createdAt
    followers { totalCount }
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        stargazerCount
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionYears
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}"""

Q_YEAR = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def gql(query: str, variables: dict, token: str) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "midnight-ai-lab-github-pulse"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"GitHub API HTTP {e.code}: {e.read()[:300]!r}")
    if payload.get("errors"):
        raise SystemExit(f"GitHub GraphQL error: {payload['errors']}")
    return payload["data"]


def _range(a: dt.date, b: dt.date) -> str:
    if a == b:
        return a.strftime("%b %d, %Y")
    if a.year == b.year:
        return f"{a.strftime('%b %d')} – {b.strftime('%b %d, %Y')}"
    return f"{a.strftime('%b %d, %Y')} – {b.strftime('%b %d, %Y')}"


def streaks(days: dict[dt.date, int], today: dt.date):
    seq = sorted(d for d in days if d <= today)
    best, best_rng, run, start = 0, None, 0, None
    for d in seq:
        if days[d] > 0:
            if run == 0:
                start = d
            run += 1
            if run > best:
                best, best_rng = run, (start, d)
        else:
            run = 0
    cur, cur_rng = 0, None
    d = today if days.get(today, 0) > 0 else today - dt.timedelta(days=1)
    end = d
    while days.get(d, 0) > 0:
        cur += 1
        d -= dt.timedelta(days=1)
    if cur:
        cur_rng = (d + dt.timedelta(days=1), end)
    return cur, cur_rng, best, best_rng


def collect(login: str, token: str) -> dict:
    repos, cursor, user = [], None, None
    while True:
        data = gql(Q_MAIN, {"login": login, "cursor": cursor}, token)
        user = data["user"]
        if user is None:
            raise SystemExit(f"GitHub user {login!r} not found")
        page = user["repositories"]
        repos += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    cc = user["contributionsCollection"]
    langs: dict[str, int] = {}
    for r in repos:
        if r["name"].lower() == login.lower():      # skip this profile repo (the forge's own code)
            continue
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total_bytes = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])
    days: dict[dt.date, int] = {}
    total_all = 0
    today = dt.datetime.now(dt.timezone.utc).date()
    for y in sorted(cc["contributionYears"]):
        yd = gql(Q_YEAR, {"login": login, "from": f"{y}-01-01T00:00:00Z", "to": f"{y}-12-31T23:59:59Z"}, token)
        cal = yd["user"]["contributionsCollection"]["contributionCalendar"]
        total_all += cal["totalContributions"]
        for w in cal["weeks"]:
            for dd in w["contributionDays"]:
                days[dt.date.fromisoformat(dd["date"])] = dd["contributionCount"]
    cur, cur_rng, best, best_rng = streaks(days, today)
    weeks = [[{"date": d["date"], "count": d["contributionCount"], "level": d["contributionLevel"]}
              for d in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]]
    return {
        "login": user["login"],
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "contributions_year": cc["contributionCalendar"]["totalContributions"],
        "commits_year": cc["totalCommitContributions"],
        "prs_year": cc["totalPullRequestContributions"],
        "issues_year": cc["totalIssueContributions"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "first_year": min(cc["contributionYears"]) if cc["contributionYears"] else int(user["createdAt"][:4]),
        "contributions_total": total_all,
        "streak_current": cur,
        "streak_current_range": _range(*cur_rng) if cur_rng else "",
        "streak_longest": best,
        "streak_longest_range": _range(*best_rng) if best_rng else "",
        "languages": [{"name": k, "bytes": v, "pct": 100 * v / total_bytes} for k, v in top[:8]],
        "calendar": weeks,
    }


def render(data: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    L.stats(data).save(OUT / "stats.svg")
    L.streak(data).save(OUT / "streak.svg")
    L.languages(data).save(OUT / "languages.svg")
    L.calendar(data).save(OUT / "contributions.svg")
    (OUT / "stats.json").write_text(json.dumps({k: v for k, v in data.items() if k != "calendar"}, indent=2) + "\n")


PLACEHOLDERS = [("stats.svg", "GitHub statistics", "your GitHub statistics", 1000, 200),
                ("streak.svg", "Contribution streak", "streak stats", 490, 330),
                ("languages.svg", "Top languages", "top languages", 490, 330),
                ("contributions.svg", "Contribution calendar", "the contribution calendar", 1000, 200),
                ("snake.svg", "Contribution snake", "the contribution snake", 1000, 200)]


def placeholders(force: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, title, what, w, h in PLACEHOLDERS:
        if force or not (OUT / name).exists():
            L.placeholder(title, what, w, h).save(OUT / name)


def frame_snake(src: str) -> None:
    """Give Platane/snk's transparent SVG the Midnight AI Lab black-glass panel + thin violet border."""
    s = Path(src).read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>", s)
    vb = re.search(r'viewBox="([-\d.]+)[ ,]+([-\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)"', m.group(0))
    x, y, w, h = map(float, vb.groups())
    pad = 24
    X, Y, Wd, Ht = x - pad, y - pad, w + 2 * pad, h + 2 * pad
    root = re.sub(r'viewBox="[^"]*"', f'viewBox="{X:g} {Y:g} {Wd:g} {Ht:g}"', m.group(0))
    root = re.sub(r'\swidth="[^"]*"', f' width="{Wd:g}"', root)
    root = re.sub(r'\sheight="[^"]*"', f' height="{Ht:g}"', root)
    bg = (f'<rect x="{X:g}" y="{Y:g}" width="{Wd:g}" height="{Ht:g}" rx="16" fill="#050507"/>'
          f'<rect x="{X + 1:g}" y="{Y + 1:g}" width="{Wd - 2:g}" height="{Ht - 2:g}" rx="15" fill="none" stroke="{palette.P.glow}" '
          f'stroke-opacity=".7" stroke-width="1.5"/>')
    if "<title" not in s:
        bg = "<title>Contribution snake</title>" + bg
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "snake.svg").write_text(s[:m.start()] + root + bg + s[m.end():], encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frame-snake", metavar="SVG")
    ap.add_argument("--placeholders", action="store_true")
    ap.add_argument("--login")
    a = ap.parse_args()
    cfg = config.read()
    palette.configure(cfg["PRIMARY_COLOR"], cfg["SECONDARY_COLOR"], cfg["ACCENT_COLOR"], cfg["GLOW_COLOR"], cfg["LAVENDER_COLOR"])
    if a.frame_snake:
        return frame_snake(a.frame_snake)
    if a.placeholders:
        return placeholders(force=True)
    token = os.environ.get("PULSE_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN (automatic inside GitHub Actions) to fetch real stats.")
    login = a.login or cfg["GITHUB_USERNAME"] or os.environ.get("GITHUB_REPOSITORY_OWNER")
    data = collect(login, token)
    render(data)
    print(f"GitHub Pulse refreshed for @{data['login']}: {data['contributions_year']} contributions in the last year")


if __name__ == "__main__":
    main()
