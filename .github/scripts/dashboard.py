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
        '</defs>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#dots)"/>',
        # Header: terminal-style prompt.
        f'<g font-size="13">'
        f'<circle cx="28" cy="28" r="5" fill="{RED}"/><circle cx="46" cy="28" r="5" fill="{DARK}"/>'
        f'<circle cx="64" cy="28" r="5" fill="{BORDER}"/>'
        f'<text x="86" y="32.5" fill="{RED}">{USER}@github<tspan fill="{MUTED}">:~$</tspan>'
        f'<tspan fill="{TEXT}"> ./stats --live</tspan></text>'
        f'<text x="{W - 28}" y="32.5" fill="{MUTED}" text-anchor="end" font-size="11">SYNC {now}</text>'
        f'</g>',
        f'<line x1="20" y1="52" x2="{W - 20}" y2="52" stroke="{BORDER}"/>',
    ]
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
