"""Render the static README artwork into assets/*.svg (hero, section headers, cards, footer).

Run after editing: python3 .github/scripts/assets.py
Shares palette and the reveal() animation helper with dashboard.py.
"""
import os
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


ASSETS = {"hero.svg": hero}
for _i, (_slug, _title, _tag) in enumerate(SECTIONS, 1):
    ASSETS[f"section-{_slug}.svg"] = lambda i=_i, t=_title, g=_tag: section(i, t, g)

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn in ASSETS.items():
        with open(os.path.join(OUT_DIR, name), "w") as f:
            f.write(fn())
        print("wrote", os.path.join(OUT_DIR, name))
