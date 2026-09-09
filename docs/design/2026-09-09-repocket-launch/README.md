---
title: "Design handoff: Repocket landing site (2026-09-09)"
summary: The binding design handoff for the Repocket marketing site — a complete static site under site/ with locked colors, type, copy, and section order; describes what to publish, which placeholders to resolve, and what verification acceptance means (Lighthouse ≥95/95, both languages render, reduced-motion respected).
updated: 2026-09-09
status: living
---

# Repocket website · handoff for Claude Code

Goal: publish the Repocket landing page on GitHub Pages, exactly as designed, with the privacy and support URLs App Store Connect needs.

## What is in `site/`
Static HTML, no build step, no framework.

- `index.html` landing page. EN/DE toggle (remembered in localStorage, defaults from browser language). All copy is inline in `<span data-l="en">` / `<span data-l="de">` pairs.
- `privacy.html`, `support.html`, `press.html` same toggle, shared inline styles.
- `assets/mark.svg` app mark used for favicon, nav and footer.
- `.nojekyll` keeps GitHub Pages from running Jekyll over the files.
- `README.md` short deploy notes.

Fonts load from Google Fonts (Bricolage Grotesque, Outfit). Everything else is self-contained.

## Do not change
- Colours, type, spacing, section order, copy. The page follows the Repocket design system (ink #241B5E, coral #FF5C39, ground #F4F1FF, marigold #FFC947, green #1FA588).
- The three animations: hero total count-up with the second debt card sliding in; sticky phone switching screens as the story scrolls; fade-up reveals. All already respect `prefers-reduced-motion`.
- The German amounts (`3,99 €`) and dates.

## Steps

1. **Create the repo.** `repocket-site` (or `<user>.github.io` for an apex site), public. Copy the contents of `site/` to the repo root, including the dotfile `.nojekyll`.
2. **Enable Pages.** Settings › Pages › Source: *Deploy from a branch*, branch `main`, folder `/ (root)`. First deploy takes about a minute; the URL is `https://<user>.github.io/repocket-site/`.
3. **Replace placeholders** in `index.html` (three occurrences) and nowhere else: `https://apps.apple.com/` → the real App Store URL once the app is live. Until then leave the placeholder; do not invent an ID.
4. **Add `assets/og.png`** at 1200×630 for link previews: ink background, the mark, the line "Track what you borrowed from yourself." in Bricolage Grotesque 800, white. `index.html` already references it. If you cannot produce a raster image, remove the `og:image` meta tag rather than shipping a broken reference.
5. **Custom domain (optional).** If a domain like `repocket.app` exists: add a `CNAME` file containing the bare domain, set the DNS `A` records to GitHub Pages' IPs (185.199.108–111.153) and `www` CNAME to `<user>.github.io`, then tick *Enforce HTTPS* once the certificate is issued.
6. **Contact address.** `hello@repocket.app` appears in privacy, support and press. Confirm it exists or replace all occurrences.
7. **Verify.** Open the Pages URL on a phone: hero fits one screen, the toggle switches every string, the story phone changes screens while scrolling, all four pages link to each other, `privacy.html` and `support.html` resolve (paste both into App Store Connect › App Information).

## Acceptance
- Lighthouse: Performance ≥ 95, Accessibility ≥ 95, no console errors.
- No layout shift on font load beyond the swap itself (fonts use `display=swap`).
- Both languages render every section; no untranslated `data-l` span left empty.
- Reduced-motion users see the page fully rendered with no animation.

## Later, not now
- Self-host the two fonts to drop the Google request (download WOFF2, put in `assets/fonts/`, swap the `<link>` for `@font-face`).
- A `sitemap.xml` and `robots.txt` once the domain is final.
- Real App Store screenshots in `press.html` (currently "on request").
