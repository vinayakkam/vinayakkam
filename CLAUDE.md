# vinayakkam/vinayakkam

GitHub profile README repo. No app code: `README.md` is the product, rendered on github.com/vinayakkam.

## Layout

- `README.md` — profile page. GitHub-flavored markdown + inline HTML (`<table>`, `<div align="center">`, `<details>`). Markdown inside HTML cells needs a blank line before and after.
- `.github/workflows/flappy.yml` — hourly. Inline Python writes `dist/flappy-bird.svg` (animated Flappy OLIT scene), pushes it to the `output` branch.
- `.github/workflows/stats.yml` — daily. `stats-organization/github-readme-stats-action@v2` writes `dist/stats.svg` and `dist/top-langs.svg`, pushes to `output`.

## `output` branch

Generated SVGs only. Never edit by hand. Both workflows publish with `peaceiris/actions-gh-pages` and `keep_files: true`, so each one adds its files without deleting the other's.
README embeds them via `https://raw.githubusercontent.com/vinayakkam/vinayakkam/output/<file>.svg`.

## External image services

- `capsule-render.vercel.app` — header/footer waves
- `readme-typing-svg.demolab.com` — typing text lines
- `streak-stats.demolab.com` — streak card
- `skillicons.dev` — tech stack icons
- `img.shields.io` — badges

Do not use public `github-readme-stats*.vercel.app` instances for the stats cards. They rate-limit or get disabled (`402 DEPLOYMENT_DISABLED`). Generate cards in `stats.yml` instead.
Check a URL with curl before adding it. Percent-encode emoji in query strings when testing; GitHub's image proxy does it for you in the README.

## Style

- Palette: red `#E03C3C`, dark red `#8B0000`, accent `#FF6B6B`, background `#0D1117`, text `#C9D1D9`, muted `#8B949E`, border `#30363D`. Matches GitHub dark theme.
- Font in generated SVGs: JetBrains Mono / monospace.
- Keep facts (OLIT Bot features, contact, stack) in sync with what the owner states; don't invent features.

## Workflows

- Scheduled workflows auto-disable after 60 days without repo activity. Re-enable in the Actions tab, or run via `workflow_dispatch`.
- Stats use `GITHUB_TOKEN` (public data only) unless a `GH_STATS_PAT` secret exists.

## Git

- Commit only; the owner pushes.
- No `Co-Authored-By` or other AI attribution trailers in commit messages.
