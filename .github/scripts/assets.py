"""Render the static README artwork into assets/*.svg (hero, section headers, cards, footer).

Run after editing: python3 .github/scripts/assets.py
Shares palette and the reveal() animation helper with dashboard.py.
"""
import os
import random
import textwrap
from xml.sax.saxutils import escape as esc

from dashboard import ACCENT, BG, BORDER, DARK, FONT, MUTED, PANEL, RED, TEXT, reveal

OUT_DIR = os.environ.get("ASSETS_DIR", "assets")
CH = 0.6  # monospace glyph width per px of font size, for layout maths


def svg(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}" role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n'
            + "\n".join(body) + "\n</svg>\n")


def window(w, h, title):
    """Card background with dotted grid and terminal title bar, matching dashboard.svg."""
    return [
        '<defs>'
        f'<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{BORDER}" opacity=".55"/></pattern>'
        '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" '
        'result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '</defs>',
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#dots)"/>',
        f'<circle cx="28" cy="28" r="5" fill="{RED}"/><circle cx="46" cy="28" r="5" fill="{DARK}"/>'
        f'<circle cx="64" cy="28" r="5" fill="{BORDER}"/>',
        f'<text x="{w / 2}" y="32" fill="{MUTED}" font-size="12" text-anchor="middle">{esc(title)}</text>',
        f'<line x1="20" y1="52" x2="{w - 20}" y2="52" stroke="{BORDER}"/>',
    ]


def typed_cycle(x, y, lines, size=16, each=4.0, color=TEXT):
    """Lines typed out and erased one after another, forever. Static renderers show the first line."""
    total = each * len(lines)
    out = []
    for i, line in enumerate(lines):
        wpx = len(line) * size * CH + 4
        t0, t1 = i * each / total, (i + 1) * each / total
        typed, held = t0 + 1.2 / total, t1 - 0.5 / total
        kt = f"0;{t0:.4f};{typed:.4f};{held:.4f};{t1:.4f};1"
        # Clip-rect width does the typing; opacity hides the line outside its slot.
        out.append(
            f'<clipPath id="tc{i}"><rect x="{x}" y="{y - size}" width="{wpx:.0f}" height="{size * 1.5}">'
            f'<animate attributeName="width" values="0;0;{wpx:.0f};{wpx:.0f};0;0" keyTimes="{kt}" '
            f'dur="{total}s" repeatCount="indefinite"/></rect></clipPath>'
            f'<g opacity="{1 if i == 0 else 0}">'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{t0:.4f};{t1:.4f};{t1 + 0.0001:.4f}" '
            f'calcMode="discrete" dur="{total}s" repeatCount="indefinite"/>'
            f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" clip-path="url(#tc{i})">{esc(line)}</text>'
            f'</g>')
    return out


def hero():
    w, h = 900, 300
    name = "VINAYAK KAMATH"
    b = window(w, h, "~/vinayakkam — zsh")
    b.append(f'<text x="40" y="92" fill="{MUTED}" font-size="14"><tspan fill="{RED}">$</tspan> whoami</text>')
    # Name with a red/dark chromatic split that twitches every few seconds.
    for dx, col, op in ((-3, DARK, .9), (3, ACCENT, .35)):
        b.append(f'<text x="{40 + dx}" y="150" fill="{col}" opacity="{op}" font-size="50" font-weight="800" '
                 f'letter-spacing="2">{name}<animate attributeName="x" '
                 f'values="{40 + dx};{40 + dx};{40 + dx * 3};{40 - dx};{40 + dx};{40 + dx}" '
                 f'keyTimes="0;.9;.92;.94;.96;1" dur="5s" repeatCount="indefinite"/></text>')
    b.append(f'<text x="40" y="150" fill="{TEXT}" font-size="50" font-weight="800" letter-spacing="2">{name}</text>')
    b.append(f'<text x="42" y="182" fill="{MUTED}" font-size="15">AI Engineering Student '
             f'<tspan fill="{RED}">·</tspan> Founder of <tspan fill="{ACCENT}">OLIT Technologies</tspan></text>')
    b.append(f'<text x="40" y="232" fill="{MUTED}" font-size="14"><tspan fill="{RED}">$</tspan> cat now.txt</text>')
    b += typed_cycle(40, 262, ["I build bots, dev tools and AI experiences.",
                               "Shipping GitPilot · OLIT Bot · LatchVerify",
                               "BE Artificial Intelligence · Mangaluru, IN",
                               "Let's build something together."],
                     color=ACCENT)
    # Orbit emblem on the right: two counter-rotating dashed rings around a pulsing core.
    cx, cy = 760, 160
    b.append(
        f'<g>'
        f'<circle cx="{cx}" cy="{cy}" r="78" fill="none" stroke="{RED}" stroke-opacity=".07" stroke-width="18"/>'
        f'<circle cx="{cx}" cy="{cy}" r="70" fill="none" stroke="{BORDER}" stroke-width="2" stroke-dasharray="2 8">'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
        f'dur="40s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{cy}" r="54" fill="none" stroke="{RED}" stroke-width="3" '
        f'stroke-dasharray="60 24 8 24" filter="url(#glow)">'
        f'<animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" '
        f'dur="14s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{cy}" r="38" fill="{PANEL}" stroke="{BORDER}"/>'
        f'<text x="{cx}" y="{cy + 7}" fill="{TEXT}" font-size="20" font-weight="800" text-anchor="middle" '
        f'letter-spacing="1">OLIT</text>'
        # Satellite riding the outer ring.
        f'<circle cx="{cx}" cy="{cy - 70}" r="5" fill="{ACCENT}" filter="url(#glow)">'
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" '
        f'dur="8s" repeatCount="indefinite"/></circle>'
        f'</g>')
    # Live status pill.
    b.append(
        f'<rect x="{cx - 94}" y="{cy + 98}" width="188" height="24" rx="12" fill="{PANEL}" stroke="{BORDER}"/>'
        f'<circle cx="{cx - 78}" cy="{cy + 110}" r="4" fill="{ACCENT}">'
        f'<animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'
        f'<text x="{cx + 8}" y="{cy + 114}" fill="{TEXT}" font-size="11" text-anchor="middle" '
        f'letter-spacing="1">OPEN TO OPPORTUNITIES</text>')
    return svg(w, h, "Vinayak Kamath — AI Engineering Student, Founder of OLIT Technologies", b)


SECTIONS = [("about", "ABOUT", "profile.py"), ("projects", "PROJECTS", "shipped & building"),
            ("bot", "OLIT BOT", "discord.py"), ("stack", "TECH STACK", "toolchain"),
            ("stats", "GITHUB STATS", "live · daily"), ("flappy", "FLAPPY OLIT", "live · hourly")]


def section(i, title, tag):
    """Thin section banner: index, title, ruled line with a light pulse running along it, right tag."""
    w, h = 900, 46
    x_line = 48 + (14 * CH + 3) * len(title) + 14  # +3 = letter-spacing
    x_end = w - 4 - 11 * CH * (len(tag) + 4) - 14   # +4 = "[ " and " ]"
    return svg(w, h, title.title(), [
        f'<defs><linearGradient id="pulse"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>'
        f'</linearGradient></defs>',
        f'<rect x="4" y="13" width="4" height="20" rx="2" fill="{RED}"/>',
        f'<text x="18" y="29" fill="{RED}" font-size="14" font-weight="700">{i:02d}</text>',
        f'<text x="48" y="29" fill="{TEXT}" font-size="14" font-weight="700" letter-spacing="3">{esc(title)}</text>',
        f'<line x1="{x_line:.0f}" y1="23.5" x2="{x_end:.0f}" y2="23.5" stroke="{BORDER}"/>',
        f'<rect x="{x_line:.0f}" y="22.5" width="80" height="2" fill="url(#pulse)">'
        f'<animate attributeName="x" values="{x_line:.0f};{x_end - 80:.0f}" dur="4s" begin="{i * 0.4:.1f}s" '
        f'repeatCount="indefinite"/></rect>',
        f'<text x="{w - 4}" y="28" fill="{MUTED}" font-size="11" text-anchor="end">[ {esc(tag)} ]</text>',
    ])


def code_line(x, y, segs, size=13):
    """One line of highlighted code: segs = [(text, colour), ...]. Spaces kept as-is."""
    spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in segs)
    return f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve">{spans}</text>'


def about():
    w, h = 900, 330
    b = window(w, h, "profile.py — ~/vinayakkam")
    # Left pane: profile.py with line numbers.
    kv = [("name", "K Vinayak Kamath"), ("handle", "@vinayakkam"), ("based_in", "Mangaluru, India"),
          ("studying", "BE, Artificial Intelligence"), ("building", "OLIT Technologies"),
          ("status", "open to opportunities")]
    lines = [[("# profile.py", MUTED)], [("me ", TEXT), ("=", RED), (" {", MUTED)]]
    lines += [[("    ", TEXT), (f'"{k}"'.ljust(11), TEXT), (": ", RED), (f'"{v}"', ACCENT), (",", MUTED)]
              for k, v in kv]
    lines.append([("    ", TEXT), ('"ships"'.ljust(11), TEXT), (": ", RED), ("[", MUTED),
                  ('"bots"', ACCENT), (", ", MUTED), ('"dev tools"', ACCENT), (", ", MUTED),
                  ('"AI"', ACCENT), ("],", MUTED)])
    lines.append([("}", MUTED)])
    for i, segs in enumerate(lines):
        y = 88 + i * 23
        b.append(f'<g>{reveal(0.15 + i * 0.07)}'
                 f'<text x="44" y="{y}" fill="{BORDER}" font-size="12" text-anchor="end">{i + 1}</text>'
                 + code_line(60, y, segs) + '</g>')
    # Divider and right pane: projects.log, one entry at a time.
    b.append(f'<line x1="560" y1="64" x2="560" y2="{h - 20}" stroke="{BORDER}"/>')
    b.append(f'<text x="584" y="88" fill="{RED}" font-size="11" letter-spacing="2">// PROJECTS.LOG</text>')
    log = [("GitPilot", "v0.5.1"), ("LatchVerify", "MCP proxy"), ("OLIT Bot", "live"),
           ("OLIT Nexus", "local AI"), ("Twilight", "Hyprland")]
    for i, (name, tag) in enumerate(log):
        y = 120 + i * 28
        b.append(f'<g>{reveal(0.9 + i * 0.15, dx=-8)}'
                 f'<text x="584" y="{y}" fill="{RED}" font-size="12">▸</text>'
                 f'<text x="602" y="{y}" fill="{TEXT}" font-size="13">{esc(name)}</text>'
                 f'<text x="{w - 28}" y="{y}" fill="{MUTED}" font-size="11" text-anchor="end">{esc(tag)}</text>'
                 '</g>')
    y = 120 + len(log) * 28
    b.append(f'<text x="584" y="{y}" fill="{RED}" font-size="13">$</text>'
             f'<rect x="600" y="{y - 11}" width="8" height="14" fill="{RED}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" '
             f'repeatCount="indefinite"/></rect>')
    return svg(w, h, "About: K Vinayak Kamath, AI engineering student in Mangaluru, building OLIT Technologies", b)


# (slug, name, status, description, tech, meta). Facts from each repo's README and olittechnologies.co.in.
# README links LatchVerify to github.com/ANI-CPU-tech/LatchVerify (upstream), not the vinayakkam fork.
PROJECTS = [
    ("gitpilot", "GitPilot", "v0.5.1",
     "Desktop Git manager. Shows exactly what changed, stages down to single lines and explains Git "
     "errors in plain language.", ["Rust", "Tauri 2", "React"], "Windows + Linux · signed auto-updates"),
    ("latchverify", "LatchVerify", "PROTOTYPE",
     "Security proxy for MCP servers. Pins each tool's capabilities in a git-committed lockfile and "
     "blocks rug pulls.", ["TypeScript", "Node", "Electron"], "co-built with ANI-CPU-tech · MIT"),
    ("olit-bot", "OLIT Bot", "LIVE",
     "The Discord bot for space explorers: 15+ games, Galaxy Explorer RPG, auto-moderation and a "
     "web dashboard.", ["Python", "discord.py"], "olittechnologies.co.in/bot"),
    ("olit-nexus", "OLIT Nexus", "LOCAL",
     "Self-hosted AI console. Chat, attach PDFs, images or text, toggle web search. Runs entirely on "
     "your own machine.", ["Python", "Qwen2.5-Coder"], "no cloud · no billing"),
    ("twilight", "Twilight", "DESKTOP",
     "A Windows 11-style desktop for Hyprland: top bar, centred taskbar, Start menu, Settings app and "
     "lock screen.", ["QML", "Quickshell", "Hyprland"], "Linux desktop shell"),
]


def project(i, name, status, desc, tech, meta):
    w, h = 440, 200
    b = [
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
        # Corner brackets, HUD style.
        f'<path d="M12 28V12h16M{w - 28} 12h16v16M12 {h - 28}v16h16M{w - 28} {h - 12}h16v-16" '
        f'fill="none" stroke="{RED}" stroke-width="1.5" opacity=".7"/>',
        f'<text x="28" y="44" fill="{RED}" font-size="12" font-weight="700">{i:02d}</text>',
        f'<text x="56" y="44" fill="{TEXT}" font-size="18" font-weight="700">{esc(name)}</text>',
    ]
    sw = len(status) * 10 * 0.64 + 30
    b.append(f'<rect x="{w - 28 - sw:.0f}" y="29" width="{sw:.0f}" height="20" rx="10" fill="{PANEL}" '
             f'stroke="{BORDER}"/><circle cx="{w - 28 - sw + 10:.0f}" cy="39" r="3" fill="{ACCENT}">'
             f'<animate attributeName="opacity" values="1;.25;1" dur="1.6s" begin="{i * .3:.1f}s" '
             f'repeatCount="indefinite"/></circle>'
             f'<text x="{w - 28 - sw / 2 + 5:.0f}" y="43" fill="{TEXT}" font-size="10" text-anchor="middle" '
             f'letter-spacing=".5">{esc(status)}</text>')
    for j, line in enumerate(textwrap.wrap(desc, 52)[:3]):
        b.append(f'<text x="28" y="{78 + j * 19}" fill="{MUTED}" font-size="12">{esc(line)}</text>')
    x = 28
    for t in tech:
        tw = len(t) * 11 * 0.64 + 20
        b.append(f'<rect x="{x}" y="{h - 66}" width="{tw:.0f}" height="22" rx="5" fill="{PANEL}" stroke="{BORDER}"/>'
                 f'<text x="{x + tw / 2:.0f}" y="{h - 51}" fill="{ACCENT}" font-size="11" '
                 f'text-anchor="middle">{esc(t)}</text>')
        x += tw + 8
    b.append(f'<text x="36" y="{h - 18}" fill="{MUTED}" font-size="10"><tspan fill="{RED}">›</tspan> '
             f'{esc(meta)}</text>')
    # Light sweeping along the top edge.
    b.append(f'<defs><linearGradient id="sw"><stop offset="0" stop-color="{RED}" stop-opacity="0"/>'
             f'<stop offset=".5" stop-color="{ACCENT}"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/>'
             f'</linearGradient></defs>'
             f'<rect x="40" y="0" width="90" height="1.5" fill="url(#sw)"><animate attributeName="x" '
             f'values="40;{w - 130}" dur="5s" begin="{i * .5:.1f}s" repeatCount="indefinite"/></rect>')
    return svg(w, h, f"{name}: {desc}", b)


def starfield(w, h, n=70, seed=42, top=56):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y, r = rnd.uniform(10, w - 10), rnd.uniform(top + 6, h - 10), rnd.choice([.6, .8, 1, 1.4])
        col = rnd.choice([TEXT, TEXT, MUTED, ACCENT])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{col}" opacity=".5">'
                   f'<animate attributeName="opacity" values=".5;.1;.5" dur="{rnd.uniform(2, 5):.1f}s" '
                   f'begin="{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>')
    return out


def bot():
    """OLIT Bot showcase. Copy and numbers from olittechnologies.co.in/bot."""
    w, h = 900, 320
    b = window(w, h, "OLIT Bot — discord.py")
    b += starfield(w, h)
    b.append(f'<circle cx="46" cy="94" r="5" fill="{ACCENT}" filter="url(#glow)">'
             f'<animate attributeName="r" values="5;7;5" dur="1.6s" repeatCount="indefinite"/></circle>'
             f'<text x="60" y="99" fill="{ACCENT}" font-size="12" letter-spacing="2">ONLINE</text>')
    b.append(f'<text x="40" y="138" fill="{TEXT}" font-size="21" font-weight="800">The Discord bot</text>'
             f'<text x="40" y="164" fill="{TEXT}" font-size="21" font-weight="800">for <tspan fill="{RED}">'
             f'space explorers</tspan>.</text>')
    tiles = [("15+", "MINI GAMES"), ("1000+", "STAR SYSTEMS"), ("60+", "TRIVIA QS"), ("∞", "ADVENTURES")]
    for i, (num, label) in enumerate(tiles):
        x = 40 + i * 112
        b.append(f'<g>{reveal(0.3 + i * 0.12, dy=8)}'
                 f'<rect x="{x}" y="190" width="102" height="64" rx="8" fill="{PANEL}" stroke="{BORDER}"/>'
                 f'<text x="{x + 51}" y="223" fill="{ACCENT}" font-size="22" font-weight="800" '
                 f'text-anchor="middle">{num}</text>'
                 f'<text x="{x + 51}" y="243" fill="{MUTED}" font-size="9" text-anchor="middle" '
                 f'letter-spacing="1">{label}</text></g>')
    b.append(f'<text x="40" y="286" fill="{MUTED}" font-size="11">discord.py 2.4+ <tspan fill="{RED}">·</tspan> '
             f'Python 3.9+ <tspan fill="{RED}">·</tspan> Docker <tspan fill="{RED}">·</tspan> '
             f'slash + prefix</text>')
    b.append(f'<line x1="520" y1="72" x2="520" y2="{h - 24}" stroke="{BORDER}"/>')
    b.append(f'<text x="546" y="96" fill="{RED}" font-size="11" letter-spacing="2">// FEATURES</text>')
    feats = [("Galaxy Explorer", "RPG · ships · boss battles"), ("15+ games", "trivia, booster catch, RPS…"),
             ("Auto-moderation", "word filters, no restarts"), ("Leaderboards", "per-server, auto roles"),
             ("Custom commands", "from the dashboard"), ("Welcome system", "greets new members")]
    for i, (name, sub) in enumerate(feats):
        y = 128 + i * 30
        b.append(f'<g>{reveal(0.6 + i * 0.12, dx=-8)}'
                 f'<text x="546" y="{y}" fill="{RED}" font-size="10">{i + 1:02d}</text>'
                 f'<text x="572" y="{y}" fill="{TEXT}" font-size="13">{esc(name)}</text>'
                 f'<text x="{w - 32}" y="{y}" fill="{MUTED}" font-size="10" text-anchor="end">{esc(sub)}</text>'
                 '</g>')
    return svg(w, h, "OLIT Bot: the Discord bot for space explorers. 15+ games, Galaxy Explorer, "
                     "auto-moderation, leaderboards, custom commands, welcome system", b)


def footer():
    """Closing card: two drifting sine waves (signal trace) under a sign-off line."""
    import math
    w, h = 900, 170

    def wave(amp, period, y0):
        # Two periods wider than the card, so translating by one period loops seamlessly.
        pts = [f"{x},{y0 + amp * math.sin(2 * math.pi * x / period):.1f}" for x in range(-period, w + period, 6)]
        return "M" + " L".join(pts)

    b = [
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        f'<g opacity=".9"><path d="{wave(10, 180, 120)}" fill="none" stroke="{DARK}" stroke-width="2">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;180 0" dur="9s" '
        f'repeatCount="indefinite"/></path>'
        f'<path d="{wave(7, 120, 122)}" fill="none" stroke="{RED}" stroke-width="1.5" opacity=".8">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;-120 0" dur="6s" '
        f'repeatCount="indefinite"/></path></g>',
        f'<text x="{w / 2}" y="52" fill="{MUTED}" font-size="13" text-anchor="middle">'
        f'<tspan fill="{RED}">$</tspan> exit</text>',
        f'<text x="{w / 2}" y="82" fill="{TEXT}" font-size="17" font-weight="700" text-anchor="middle">'
        f'Thanks for visiting <tspan fill="{RED}">·</tspan> let\'s build something together</text>',
        f'<text x="{w / 2}" y="{h - 16}" fill="{MUTED}" font-size="10" text-anchor="middle" letter-spacing="1">'
        f'OLIT TECHNOLOGIES · MANGALURU, INDIA</text>',
    ]
    # Clip waves to the card's rounded rectangle.
    b.insert(0, f'<defs><clipPath id="card"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>')
    b[2] = b[2].replace('<g opacity=".9">', '<g opacity=".9" clip-path="url(#card)">')
    return svg(w, h, "Thanks for visiting — let's build something together", b)


ASSETS = {"hero.svg": hero, "about.svg": about, "bot.svg": bot, "footer.svg": footer}
for _i, (_slug, *_rest) in enumerate(PROJECTS, 1):
    ASSETS[f"project-{_slug}.svg"] = lambda i=_i, r=tuple(_rest): project(i, *r)
for _i, (_slug, _title, _tag) in enumerate(SECTIONS, 1):
    ASSETS[f"section-{_slug}.svg"] = lambda i=_i, t=_title, g=_tag: section(i, t, g)

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn in ASSETS.items():
        with open(os.path.join(OUT_DIR, name), "w") as f:
            f.write(fn())
        print("wrote", os.path.join(OUT_DIR, name))
