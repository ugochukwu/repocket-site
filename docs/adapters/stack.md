---
title: Stack adapter
summary: Every command an agent runs against Repocket-site's code — build, test, lint, the CI-mirror quality gate, running the site, and the UI render check.
updated: 2026-09-09
status: living
---

# Stack adapter

Every command an agent runs against this project's code lives here. Core kit files
(CLAUDE.md, the subagents, the skills) reference the section names below and never hardcode
commands — so swapping the stack means editing this one file.

## Build & language

Plain HTML/CSS/JS static site, no build step, no framework, no bundler — the site is exactly
the files served. Source lives at the **repository root** (not under a `site/` subfolder): the
brief's own README says "Copy the contents of `site/` to the repo root, including the dotfile
`.nojekyll`." GitHub Pages serves branch `master`, path `/`, from the default `<user>.github.io/<repo>/`
URL until a custom domain is added.

- `index.html`, `privacy.html`, `support.html`, `press.html` — the four pages the site ships,
  each self-contained (inline `<style>` and `<script>`, no shared CSS/JS files).
- `assets/mark.svg` — the app mark used for favicon, nav, footer.
- `assets/og.png` (may be absent) — 1200×630 link-preview image referenced by `index.html`'s
  `og:image` meta tag; the brief allows either producing it or removing the meta tag rather
  than shipping a broken reference.
- `.nojekyll` — **required** at the repo root. GitHub Pages' legacy build type runs Jekyll by
  default, and this repo's docs (`docs/**/*.md`) carry `---` frontmatter that Jekyll would
  otherwise try to build into pages. `.nojekyll` disables that processing entirely so Pages
  serves every file as-is.
- **No CNAME yet.** Custom domain is deferred (per the design handoff's step 5). When a domain
  is added later, `CNAME` at the repo root controls it.

The one toolchain dependency is Node, used only to run `html-validate` in the lint step via
`npx` — pinned as a `devDependency` in `package.json` so `npm ci` gives every agent and CI run
the same version. `npm run lint` also shells out to `scripts/check-placeholders` (Python 3, no
third-party dependencies) before `html-validate` runs. There is no `npm run build`; deployment
ships the repo root as-is once GitHub Pages picks up the push to `master`.

## Dev self-verify

The cheapest real checks a dev-implementer runs before handing off. One command per line,
cheapest first.

- lint: `npm run lint` — runs `scripts/check-placeholders` (fails if any tracked `*.html`
  carries a bracket-style placeholder like `[CONTACT EMAIL]` or a bare `href="#"`; the two
  known Repocket placeholders `https://apps.apple.com/` and `hello@repocket.app` are
  explicitly allow-listed — see [`docs/guide/terminology.md`](../guide/terminology.md); a
  landing-page brand self-link `<a class="brand" href="#">` is a same-page top-of-page
  scroll on `index.html` and is not flagged) and then `html-validate` over every tracked
  `*.html` file (excluding the frozen design prototypes under `docs/design/**/*.dc.html`
  and QA render-evidence HTML under `docs/qa-screenshots/**/`). The `no-implicit-button-type`
  and `no-inline-style` rules are disabled in `.htmlvalidate.json` because the shipped site
  uses `<button>` outside a form (the language toggle in the nav) and a small number of
  spot-tweak inline styles that the design brief locks in; both rules would flag on
  design-locked markup that cannot change.
- render: serve the site locally (see **Run the app** below) and load the changed page(s) in a
  browser — for a static site with three JS animations (hero count-up, sticky phone
  screen-switching, fade-up reveals), the running page IS the test. There is no headless test
  runner yet.

## Quality gate (the CI mirror)

`.github/workflows/ci.yml` runs on every push and pull request. QA reproduces the same commands
locally before trusting the check, per the kit's usual practice:

- docs index: `python3 scripts/gen-doc-index --check`
- html lint: `npm ci && npm run lint`

### Fallbacks

- `npx` needs network access to fetch `html-validate` on a first run in a clean environment;
  `npm ci` (run first, per the gate above) avoids that by installing from the committed
  lockfile instead. If npm/network is genuinely unavailable, fall back to `tidy -q -e *.html`
  (present on macOS by default) and say explicitly in the report that the stricter
  `html-validate` gate was skipped.

## Run the app

`python3 -m http.server 8000` from the repo root, then open `http://localhost:8000`.

## UI render check

- Trigger paths: `*.html`, `assets/**`.
- Harness: start the local server above, then use the browser preview tool
  (`preview_start`/`navigate`/`computer` screenshot) to load the changed page(s) at both a
  mobile width (375px) and a desktop width (1280px), for **both EN and DE** (the language
  toggle is in the header of every page). Take a screenshot of each changed page at each
  width, in each language, as evidence.
- Repocket has three JS animations to verify: (1) the hero total count-up with the second
  debt card sliding in; (2) the sticky phone switching screens as the story scrolls; (3)
  fade-up reveals. All must respect `prefers-reduced-motion`. Verify by emulating
  reduced-motion in DevTools and confirming the page is fully rendered with no animation.
- Lighthouse: Performance ≥ 95, Accessibility ≥ 95, no console errors (per the design brief's
  acceptance criteria). Run Lighthouse against the local server; attach the score screenshot.
- No JS unit tests exist yet; if a page grows real interactive logic beyond the three
  animations (a form handler, additional stateful UI), add a test harness and record it here
  in the same change.

## Generated artifacts

- **Docs index** — the generated list in `docs/README.md` is built from each doc's frontmatter.
  Regenerate with `scripts/gen-doc-index` after adding or renaming a doc under `docs/`.
