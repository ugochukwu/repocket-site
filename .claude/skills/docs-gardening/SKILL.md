---
name: docs-gardening
description: >-
  Cleanup sweep of the project's docs (docs/ and its guides) — find stale, broken, or
  code-contradicted docs and fix them with the right handling (amend in place vs escalate). Use
  when the user asks to tidy/refresh/garden the docs, audit docs for staleness, or on a periodic
  docs-hygiene pass. Orchestrator-run: it makes minor fixes directly and dispatches
  dev-implementer → qa-verifier for substantive changes.
---

# Docs gardening — the cleanup routine

A repeatable sweep that keeps the docs honest without destroying rationale. The docs follow
[`docs/guide/conventions.md`](../../../docs/guide/conventions.md) — a frontmatter header plus
concise content. The generated list in [`docs/README.md`](../../../docs/README.md) is built from
that frontmatter by [`scripts/gen-doc-index`](../../../scripts/gen-doc-index).

This is an **orchestrator** routine: make **minor** edits directly; route **substantive** changes
through a `dev-implementer` → `qa-verifier` loop on a bead. Never rewrite a doc's intent on a guess —
escalate instead (step 3).

Run the sweep on its own branch so it doesn't collide with code work in flight.

## 1. Gather candidates (evidence, not vibes)

CI already enforces index freshness and required frontmatter (`scripts/gen-doc-index --check`), so
gather the signals it can't:

- **Broken in-repo links** — every relative link in `docs/` resolves to a file that exists.
- **Index drift** — regenerate with `scripts/gen-doc-index` (it rewrites the generated block); fix
  the hand-curated "Important" list by hand. A stale `title`/`summary` is a frontmatter edit.
- **Temporary docs past their purpose** — a doc marked one-time/temporary (e.g. a setup doc) whose
  task is done must be removed, along with its index entry.
- **git churn vs. doc** — `git log --oneline --since=<date> -- <paths>`: if the code a doc describes
  churned a lot and the doc didn't, it's a review candidate.
- **beads** — `bd list --status closed` / `bd show <id>`: decisions or redesigns that closed since the
  governing doc was last touched.

Produce a candidate list: `path · signal`.

## 2. Classify each candidate, then handle

Decide **minor vs substantive** first:

- **Minor** (typo, broken link, a clarifying sentence, an index entry, removing a spent temporary
  doc): **edit or delete in place directly.** Fix broken links to the correct relative path.

- **Substantive** (a change to what a doc claims or recommends): file/claim a bead, then **dispatch a
  `dev-implementer`** with the exact handling, and **`qa-verifier`** after. Amend in place and preserve
  the original rationale — never delete the reasoning behind a decision. If a change would overturn a
  decision recorded in an [ADR](../../../docs/adr/README.md), escalate for a human call (step 3) and
  supersede it with a new ADR — never rewrite a decided one.

## 3. Escalate, don't guess

If you can't tell whether the **doc** is stale or the **code** drifted — or the fix needs a decision
that isn't yours — **do not edit**. File it and move on:

```bash
bd create "doc-debt: <doc> may be stale vs <code/decision>" -t chore --description "<what looks off, what to check>"
```

Flag genuinely contentious ones for a human (`bd human <id>` or call it out in your report).

## 4. Bookkeeping

- Regenerate the index (`scripts/gen-doc-index`) and hand-check the "Important" list.
- Re-check that every in-repo link resolves.
- Commit minor fixes to the sweep branch with a clear `docs: garden <scope>` message and open a PR —
  nothing pushes to `main` directly. Docs-only fixes are low-risk `auto-merge` candidates. Substantive
  changes land via their bead through the QA gate.

## 5. Report

Summarize for the user/orchestrator:

- **Fixed directly** (minor) — one line each.
- **Dispatched** (substantive) — bead id + which subagent + handling.
- **Escalated** — doc-debt beads filed / human flags raised.
