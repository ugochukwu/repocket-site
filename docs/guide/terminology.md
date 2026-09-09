---
title: Terminology
summary: Repocket's binding domain language for code, docs, ADRs, bead titles, and PR text.
updated: 2026-09-09
status: draft
---

# Terminology

Repocket's domain language. These terms are **binding**: use them exactly — in code
(variables, types, functions, files), documentation, ADRs, commit messages, bead titles, and PR
text. General industry terms (URL, HTML, CSS, HTTP, GitHub Pages, Lighthouse) are not defined
here.

**Status: draft, first pass.** Drawn from the shipped copy in
[`docs/design/2026-09-09-repocket-launch/site/index.html`](../design/2026-09-09-repocket-launch/site/index.html)
and its README. The site's copy is voice-locked by the brief — this doc records the vocabulary
that copy commits to, so the four pages, this repo's code, and any future bead all name the same
concepts the same way.

## Product identity

- **Repocket** — the product name; iPhone app; €3.99 once, no subscription (7-day free trial).
  Tagline: "Track what you borrowed from yourself." Not "Re-pocket", not "RePocket", not
  "repocket.app" as a name (that is the domain; the app is Repocket).

## Domain objects (from the app; kept consistent on this site)

- **Pocket** — a single named allocation the user keeps at their bank (e.g. Groceries, Vacation,
  Kids, Home). The primary domain object. Never "envelope", "bucket", "category", or "account".
- **Debt** — an amount one pocket owes another after a wrong-card payment. Rendered on the app
  as `<Pocket A> owes <Pocket B> €X.XX since <date>`. Never "loan", "iou", "transaction",
  "expense", "balance".
- **Log** — the act of recording a debt at the checkout ("paid from Vacation, should have come
  from Groceries"). Both a noun (the log surface in the app) and a verb (to log a debt). Never
  "add", "capture", "record" for the primary action.
- **Move back** / **return** / **settle** — three moments of the same act: transfer the money
  at the bank to zero out the debt, then tap the row settled in the app. The site's copy uses
  all three; keep the phrasing per the brief, do not collapse them.
- **Widget** — the Home Screen widget with the "one open debt / owed" summary and the settle
  tap. Uses the same nouns as the app.

## Voice constraints (binding on all site copy)

- Every visible string is inline in the HTML as an `<span data-l="en">` / `<span data-l="de">`
  pair. Never add a string in only one language; a missing `data-l` counterpart is a bounce.
- German amounts use a comma (`3,99 €`), never a dot. German dates follow the design file's
  format (e.g. `Sa 5 Sep`, `Fr 28 Aug`), never a locale-mixed variant.
- No hype, no superlatives ("best", "amazing", "revolutionary", "ultimate", "powerful"), no
  emoji, no trailing dots (…).
- No em dashes and no en dashes anywhere in committed copy. Use commas, parentheses, colons,
  or separate sentences.
- Never call the app a "budget tracker" or "expense tracker". The brief is explicit:
  "No balances, no budgets: just the debts between your own pockets."

## This repo's own structural vocabulary

- **Site payload** — the four HTML files (`index.html`, `privacy.html`, `support.html`,
  `press.html`), `assets/mark.svg`, and `.nojekyll` at the repo root: the actual thing GitHub
  Pages serves. Not "the build" (there is no build step) or "the deploy" (that is what Pages
  does with the payload).
- **Design handoff** — the frozen brief and its `site/` reference copy under
  [`docs/design/2026-09-09-repocket-launch/`](../design/2026-09-09-repocket-launch/). This is
  the definition of done for the launch bead.
- **Placeholder** — a value in the shipped copy that resolves to something real later; two are
  known at launch time:
    - `https://apps.apple.com/` (three occurrences in `index.html` only) — resolves to the
      real App Store URL once the app is live; leave as-is until then.
    - `hello@repocket.app` — the contact address on privacy, support, and press; resolves when
      the inbox is set up owner-side. Ship as-is; no substitution.

## Deprecated — do not use

| Banned term | Use instead |
|-------------|-------------|
| envelope, bucket, category (for a pocket) | pocket |
| iou, loan, transaction, expense (for a debt) | debt |
| balance, budget (for what the app tracks) | debt |
| Re-pocket, RePocket, repocket.app (as the product name) | Repocket |
| feed / follow / discover (any social-network framing) | — none of these apply; the app is single-user |
