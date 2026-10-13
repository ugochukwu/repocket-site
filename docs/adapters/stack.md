---
title: Stack adapter
summary: Every command an agent runs against Repocket-site's code — build, test, lint, the CI-mirror quality gate, running the site, and the UI render check.
updated: 2026-10-13
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

- `index.html`, `privacy.html`, `support.html`, `press.html`, `impressum.html` — the five pages the site ships,
  each self-contained (inline `<style>` and `<script>`, no shared CSS/JS files).
- `how-to/index.html`, `how-to/everyday.html`, `how-to/people.html`: the How to hub and its two
  guides, served at `/how-to/`. Self-contained like the pages above (inline `<style>`, no
  `<script>` at all) and English only (German deferred, owner 2026-10-13), so they carry no
  `data-l` spans and no language switcher. Every other page links the hub from its nav and footer,
  and `support.html` from the top of its English block, with an English-only `data-l="en"` link,
  the way the English-only bank chips were added, so the German view is unchanged.
- `assets/illustrations/`: the brand illustrations the How to pages show, as WebP derived from
  the app repo's `docs/marketing/header/` renders (riffs 1, 2 and 3, riff 5 "people pockets" at
  3:2, and the en-US payday wheel poster), resized and saved with `cwebp -q 85` (the poster at
  `-q 90`).
- `assets/mark.svg` — the app mark used for favicon, nav, footer.
- `assets/og.png`: the 1200×630 link preview that every page's `og:image` and `twitter:image`
  meta tags point at, rendered from `docs/og/og.html` (see **Generated artifacts**).
- `assets/screens/<locale>/` holds the landing page's phone screens: real app captures from the
  app repo's App Store screenshot pipeline (`home`, `log`, `widget-large`, `all-square`), resized
  to about 2x the drawn phone's rendered width and saved as WebP. English shows `en-US` (US
  dollars, the same captures as the press kit's app screens and widget); German shows `en-GB`
  (euros) until German captures exist.
- `assets/screens/how-to/` holds the How to guides' phone screens in the same format: an en-US
  1320x2868 capture resized to 640x1392 and saved with `cwebp -q 85`. Each file is a fixed
  **screen slot** the page points at, so replacing a screen is dropping the converted capture in
  at the same path; the HTML and its alt text describe the screen each slot holds. All eight slots
  hold real 1.0.1 captures. Three come from the app repo's
  `docs/marketing/screenshots/appstore/set-2/en-US/sources/` (`everyday-log`, `everyday-to-settle`
  and `all-square`). Five come from app repo bead repocket-0bpt's
  `docs/marketing/screenshots/howto/` (its README there says how they were captured):

  | Slot | Page and step | Its capture in `docs/marketing/screenshots/howto/` |
  |------|---------------|------------------------------|
  | `everyday-starter-pockets.webp` | everyday, step 1 | `everyday-starter-pockets.png`: the first cover on the starter pockets, with the line "Name pockets after envelopes, or the people you hold money for." |
  | `everyday-pair.webp` | everyday, step 5 | `everyday-pair.png`: the pair screen for Vacation covered Groceries, $45.50, with the notes "Farmers market" and "Weekend grocery run" and the Mark settled button |
  | `people-picker.webp` | people, panel 1 | `people-picker.png`: the Paid from picker over Ama, Leo, Maya, My money, Nia and Sam |
  | `people-log.webp` | people, panel 3 | `people-log.png`: the Log sheet on Cover: $250.00, Paid from My money, Covering for Nia |
  | `people-to-settle.webp` | people, panel 4 | `people-to-settle.png`: To settle with Nia's $250.00 under "Back to My money" |

  The capture set also holds `people-to-settle-flat.png`, an alternate for `people-to-settle`
  (flat cards, one reading "My money covered Nia", no "Back to My money" header). Swapping it in is
  the one WebP plus three edits in `how-to/people.html`: that panel's alt text, its body copy
  (which names Back to My money), and the `at-settle` row and clip below, which are measured
  against the grouped capture's rows.

  To swap one: `sips -z 1392 640 <capture>.png --out /tmp/slot.png && cwebp -q 85 -metadata none
  /tmp/slot.png -o assets/screens/how-to/<slot>.webp`, then render the page. The people panels
  show only a window of each screen, and the screen shrinks with the panel (about 490 to 650 px
  tall between 375 and 1440 wide) while the corner chip's bottom edge stays 39 px down. So each screen panel
  pins the first row that matters a fixed distance below the chip, `--at: calc(-<row>% + 42px)`
  (44px for To settle's small header), and clips the screen just above that row with `--clip`,
  set on the `at-picker`, `at-log` and `at-settle` classes in `how-to/people.html`. The rows are
  percentages of the capture's height: the Paid from field (22.2%), the Cover toggle (16.53%) and
  the "Back to My money" header (25.14%). With those values the chip sits over the dark frame,
  clear of every word, at 375, 820, 981, 1024, 1100, 1180, 1280 and 1440. A new capture with a
  different layout needs its row and clip measured again and checked at those widths.
- `assets/press/` holds the press kit files that `press.html` shows and links: the en-US App
  Store frames, app screens and widgets (PNG, copied unchanged from the app repo), the four
  illustrations at 21:9, 16:9 and 3:2 (plus 1200px WebP previews for the page), the app icon (SVG,
  a 1024 PNG and the three layer SVGs), the two small `-iphone.mp4` video previews with WebP
  posters, and `README.txt`, `fact-sheet.txt` and `copy.txt`. The full-resolution MP4s and the
  press ZIP are too large for the repo: they are prepared in `dist/press-kit-<date>/` (gitignored)
  and published as the GitHub release `press-kit-<date>`, which the page's download links point at.
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
  carries a bracket-style placeholder like `[CONTACT EMAIL]` or a bare `href="#"`; the App
  Store badges link the live listing and are not placeholders, see
  [`docs/guide/terminology.md`](../guide/terminology.md); a
  landing-page brand self-link `<a class="brand" href="#">` is a same-page top-of-page
  scroll on `index.html` and is not flagged) and then `html-validate` over every tracked
  `*.html` file (excluding the frozen design prototypes under `docs/design/**/*.dc.html`
  and QA render-evidence HTML under `docs/qa-screenshots/**/`). The `no-implicit-button-type`
  and `no-inline-style` rules are disabled in `.htmlvalidate.json` because the shipped site
  uses `<button>` outside a form (the language switcher, hidden while `SHOW_LANGUAGE_SWITCHER` is `false`) and a small number of
  spot-tweak inline styles that the design brief locks in; both rules would flag on
  design-locked markup that cannot change.
- render: serve the site locally (see **Run the app** below) and load the changed page(s) in a
  browser. For a static site with two JS animations (sticky phone screen-switching, fade-up
  reveals), the running page IS the test. There is no headless test runner yet.

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

- Trigger paths: `*.html`, `how-to/*.html`, `assets/**`.
- Harness: start the local server above, then use the browser preview tool
  (`preview_start`/`navigate`/`computer` screenshot) to load the changed page(s) at both a
  mobile width (375px) and a desktop width (1280px), in English (every page always
  renders English and shows no language switcher while `SHOW_LANGUAGE_SWITCHER` is `false` in each
  page's script; check once with a German browser language and with `rp-lang=de` pre-set that English
  still shows). Take a screenshot of each changed page at each
  width, as evidence.
- Repocket has two JS animations to verify: (1) the sticky phone switching screens as the
  story scrolls; (2) fade-up reveals. Both must respect `prefers-reduced-motion`. Verify by
  emulating reduced-motion in DevTools and confirming the page is fully rendered with no
  animation. The phone screens are real app captures (WebP under `assets/screens/en-US/` and `assets/screens/en-GB/`),
  not drawn HTML, so the earlier hero count-up (a drawn total counting up while a second debt
  card slid in) is gone with the drawn screens.
- `press.html` has its own small script: three screenshot tabs, a Copy description button, and
  muted looping videos that it starts itself (or leaves paused, with controls, under
  `prefers-reduced-motion`). Click each tab, use the copy button, and confirm the videos play.
- Lighthouse: Performance ≥ 95, Accessibility ≥ 95, no console errors (per the design brief's
  acceptance criteria). Run Lighthouse against the local server; attach the score screenshot.
- No JS unit tests exist yet; if a page grows real interactive logic beyond the two
  animations (a form handler, additional stateful UI), add a test harness and record it here
  in the same change.

## Generated artifacts

- **Docs index** — the generated list in `docs/README.md` is built from each doc's frontmatter.
  Regenerate with `scripts/gen-doc-index` after adding or renaming a doc under `docs/`.
- **Link preview**: `assets/og.png` is a screenshot of `docs/og/og.html` (the mark over the
  tagline in Bricolage Grotesque 800 at 52px, white on `#241B5E`). Edit the HTML, then run
  `scripts/render-og` (Python Playwright with its Chromium) to rewrite `assets/og.png` at
  1200×630, and look at the result before committing.
