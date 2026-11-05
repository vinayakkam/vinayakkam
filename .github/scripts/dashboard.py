"""Render dist/dashboard.svg: a custom GitHub stats dashboard for the profile README.

Usage:
  GITHUB_TOKEN=... python dashboard.py            # live data for $GH_USER (default vinayakkam)
  python dashboard.py --demo                      # sample data, no network; runs self-checks
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "vinayakkam")
OUT = os.environ.get("OUT", "dist/dashboard.svg")

RED, DARK, ACCENT = "#E03C3C", "#8B0000", "#FF6B6B"
BG, PANEL, TEXT, MUTED, BORDER = "#0D1117", "#161B22", "#C9D1D9", "#8B949E", "#30363D"
FONT = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
W, H = 900, 460

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    pullRequests { totalCount }
    mergedPRs: pullRequests(states: MERGED) { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) { totalCount }
    contributionsCollection {
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}
"""


def api(url, token, body=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-dashboard",
                 "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(token):
    res = api("https://api.github.com/graphql", token, {"query": QUERY, "variables": {"login": USER}})
    if res.get("errors"):
        sys.exit(f"GraphQL error: {res['errors']}")
    u = res["data"]["user"]
    # All-time commit count, same source as github-readme-stats include_all_commits.
    commits = api(f"https://api.github.com/search/commits?q=author:{USER}", token)["total_count"]
    cc = u["contributionsCollection"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "commits": commits,
        "prs": u["pullRequests"]["totalCount"],
        "merged": u["mergedPRs"]["totalCount"],
        "issues": u["issues"]["totalCount"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "followers": u["followers"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "total_contrib": cc["contributionCalendar"]["totalContributions"],
        "days": [(d["date"], d["contributionCount"])
                 for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]],
        "langs": langs,
    }


def demo():
    import random
    rnd = random.Random(7)
    days, start = [], datetime(2025, 11, 9).toordinal()
    for i in range(364):
        burst = 3 if (i // 21) % 3 == 0 else 1
        days.append((datetime.fromordinal(start + i).date().isoformat(),
                     rnd.choice([0, 0, 1, 2, 4, 6]) * burst))
    return {"stars": 15, "commits": 1512, "prs": 43, "merged": 38, "issues": 0, "reviews": 4,
            "followers": 12, "contributed": 2, "total_contrib": sum(c for _, c in days), "days": days,
            "langs": {"TypeScript": 442, "Python": 159, "Rust": 149, "HTML": 144, "QML": 69, "C#": 36}}


def rank(s):
    """Port of github-readme-stats calculateRank (all-commits medians). Returns (level, percentile)."""
    exp = lambda x: 1 - 2 ** -x
    logn = lambda x: x / (1 + x)
    parts = [(2, exp(s["commits"] / 1000)), (3, exp(s["prs"] / 50)), (1, exp(s["issues"] / 25)),
             (1, exp(s["reviews"] / 2)), (4, logn(s["stars"] / 50)), (1, logn(s["followers"] / 10))]
    pct = (1 - sum(w * v for w, v in parts) / sum(w for w, _ in parts)) * 100
    for t, lvl in zip([1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100],
                      ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]):
        if pct <= t:
            return lvl, pct
    return "C", pct


def fmt(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def reveal(delay, dur=0.5, dx=0, dy=0):
    """Fade (and optionally slide) in after `delay` s. Starts at 0s and holds via keyTimes, so the
    element's resting state stays visible in renderers that ignore animation."""
    total = delay + dur
    k = f'keyTimes="0;{delay / total:.3f};1" dur="{total:.2f}s" fill="freeze"'
    out = f'<animate attributeName="opacity" values="0;0;1" {k}/>'
    if dx or dy:
        out += (f'<animateTransform attributeName="transform" type="translate" '
                f'values="{dx} {dy};{dx} {dy};0 0" {k}/>')
    return out


def rank_ring(level, pct, cx=140, cy=170, r=62):
    """Rank letter in a ring that fills to (100 - percentile)%, inside a slowly turning tick ring."""
    circ = 2 * 3.14159265 * r
    fill = circ * max(0.04, (100 - pct) / 100)
    ticks = "".join(
        f'<line x1="{cx}" y1="{cy - r - 14}" x2="{cx}" y2="{cy - r - (20 if i % 6 == 0 else 17)}" '
        f'stroke="{RED if i % 6 == 0 else BORDER}" stroke-width="2" transform="rotate({i * 7.5} {cx} {cy})"/>'
        for i in range(48))
    return [
        '<g>',
        f'<g opacity=".9">{ticks}<animateTransform attributeName="transform" type="rotate" '
        f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></g>',
        f'<circle cx="{cx}" cy="{cy}" r="{r + 26}" fill="none" stroke="{RED}" stroke-opacity=".06" stroke-width="14"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PANEL}" stroke="{BORDER}" stroke-width="10"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#ring)" stroke-width="10" '
        f'stroke-linecap="round" stroke-dasharray="{fill:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})" '
        f'filter="url(#glow)">'
        f'<animate attributeName="stroke-dasharray" from="0 {circ:.1f}" to="{fill:.1f} {circ:.1f}" '
        f'dur="1.6s" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></circle>',
        f'<text x="{cx}" y="{cy + 15}" fill="{TEXT}" font-size="44" font-weight="700" '
        f'text-anchor="middle">{level}</text>',
        f'<text x="{cx}" y="{cy - 26}" fill="{MUTED}" font-size="10" text-anchor="middle" '
        f'letter-spacing="2">RANK</text>',
        f'<text x="{cx}" y="{cy + r + 46}" fill="{MUTED}" font-size="11" text-anchor="middle">'
        f'TOP <tspan fill="{ACCENT}" font-weight="700">{pct:.1f}%</tspan></text>',
        '</g>',
    ]


def stat_rows(s, x=280, y=92, w=270):
    """Labelled counters with dotted leaders; each row slides in after the previous one."""
    rows = [("STARS", s["stars"]), ("COMMITS", s["commits"]), ("PULL REQUESTS", s["prs"]),
            ("MERGED PRS", s["merged"]), ("REVIEWS", s["reviews"]), ("CONTRIBUTED TO", s["contributed"])]
    out = [f'<text x="{x}" y="{y - 14}" fill="{RED}" font-size="11" letter-spacing="2">// OVERVIEW</text>']
    for i, (label, val) in enumerate(rows):
        ry = y + 14 + i * 29
        out.append(
            f'<g>{reveal(0.3 + i * 0.12, dx=-12)}'
            f'<text x="{x}" y="{ry}" fill="{RED}" font-size="10">{i + 1:02d}</text>'
            f'<text x="{x + 24}" y="{ry}" fill="{MUTED}" font-size="12">{label}</text>'
            f'<line x1="{x + 30 + len(label) * 7.3:.0f}" y1="{ry - 4}" x2="{x + w - 52}" y2="{ry - 4}" '
            f'stroke="{BORDER}" stroke-dasharray="1 4"/>'
            f'<text x="{x + w}" y="{ry}" fill="{TEXT}" font-size="14" font-weight="700" '
            f'text-anchor="end">{fmt(val)}</text>'
            f'</g>')
    return out


def languages(langs, x=600, y=92, w=270, n=6):
    """Top languages by bytes as bars that grow in, shaded from accent to dark red by rank."""
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:n]
    shades = [ACCENT, RED, "#C62F2F", "#A82424", DARK, "#6E0A0A"]
    out = [f'<text x="{x}" y="{y - 14}" fill="{RED}" font-size="11" letter-spacing="2">// LANGUAGES</text>']
    for i, (name, size) in enumerate(top):
        ry, p = y + 14 + i * 29, size / total
        bw = max(3, w * p / (top[0][1] / total))  # longest bar spans the column
        d = 0.5 + i * 0.12
        out.append(
            f'<g>{reveal(d)}'
            f'<text x="{x}" y="{ry}" fill="{TEXT}" font-size="12">{name}</text>'
            f'<text x="{x + w}" y="{ry}" fill="{MUTED}" font-size="11" text-anchor="end">{p * 100:.1f}%</text>'
            f'<rect x="{x}" y="{ry + 6}" width="{w}" height="4" rx="2" fill="{PANEL}"/>'
            f'<rect x="{x}" y="{ry + 6}" width="{bw:.1f}" height="4" rx="2" fill="{shades[i % len(shades)]}">'
            f'<animate attributeName="width" values="0;0;{bw:.1f}" keyTimes="0;{d / (d + 0.9):.3f};1" '
            f'dur="{d + 0.9:.2f}s" calcMode="spline" keySplines="0 0 1 1;.2 .8 .2 1" fill="freeze"/></rect>'
            f'</g>')
    return out


def render(s):
    level, pct = rank(s)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}" role="img" aria-label="GitHub stats for {USER}: rank {level}">',
        f'<title>{USER} · rank {level} · {fmt(s["commits"])} commits · {s["stars"]} stars</title>',
        '<defs>',
        f'<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{BORDER}" opacity=".55"/></pattern>',
        f'<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{DARK}"/></linearGradient>',
        '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
        '<feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '</defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#dots)"/>',
        # Header: terminal-style prompt.
        f'<g font-size="13">'
        f'<circle cx="28" cy="28" r="5" fill="{RED}"/><circle cx="46" cy="28" r="5" fill="{DARK}"/>'
        f'<circle cx="64" cy="28" r="5" fill="{BORDER}"/>'
        f'<text x="86" y="32.5" fill="{RED}">{USER}@github<tspan fill="{MUTED}">:~$</tspan>'
        f'<tspan fill="{TEXT}" dx="8">./stats --live</tspan></text>'
        f'<text x="{W - 28}" y="32.5" fill="{MUTED}" text-anchor="end" font-size="11">SYNC {now}</text>'
        f'</g>',
        f'<line x1="20" y1="52" x2="{W - 20}" y2="52" stroke="{BORDER}"/>',
    ]
    parts += rank_ring(level, pct)
    parts += stat_rows(s)
    parts += languages(s["langs"])
    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        assert rank({k: 0 for k in ("commits", "prs", "issues", "reviews", "stars", "followers")})[0] == "C"
        assert rank({k: 10 ** 6 for k in ("commits", "prs", "issues", "reviews", "stars", "followers")})[0] == "S"
        stats = demo()
    else:
        stats = fetch(os.environ["GITHUB_TOKEN"])
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(render(stats))
    print(f"wrote {OUT}: rank {rank(stats)}")
