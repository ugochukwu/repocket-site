---
name: review
description: >-
  Run an in-depth, read-only review of the codebase from a question or concern and write a
  dated review document under reviews/ with findings and recommendations. Use when the user asks
  whether an approach holds up, why something behaves as it does, or wants an outside-perspective
  critique before committing to a direction.
---

# Review

Take a question or concern and produce a researched, evidence-backed review. This is
**read-only**: you investigate and write a document; you do not change product code or bead
state. If the review surfaces work worth doing, recommend beads for the `rp_planning` skill to file —
do not create them here.

## 1. Frame the question

Restate the user's question or concern in one line so the review has a clear target. If it is
broad, agree the scope with the user before diving in — a review answers a question, it is not a
general tour.

## 2. Investigate

Read the code and docs that bear on the question. Trace the actual behavior, not the intended
one: follow the call paths, read the tests, run the cheapest check that confirms or refutes a
claim. Ground every finding in specific files and lines. Pin code references to the current
commit so they stay valid:

```bash
git rev-parse --short HEAD
```

Cite as `path:line` (verified at `<sha>`). Separate what you verified from what you inferred.

**Never recommend from memory.** Any suggestion that reaches beyond this codebase — an
alternative approach, a library, a design pattern, a version or benchmark claim — must be
researched at the source (`WebSearch`/`WebFetch`, official docs, the library's own repo), not
recalled. Cite the source for each such claim. An unresearched recommendation is a finding you
have not actually verified — leave it out or mark it explicitly as an open question to research.

## 3. Write the review

Write to `reviews/YYYY-MM-DD[-HHMM]-<slug>.md`, newest sorting last. Cover:

- **Question** — the concern being answered.
- **Summary** — the verdict up front, in a few sentences.
- **Findings** — what the code actually does, each backed by `path:line` references.
- **Recommendations** — concrete next steps, and any beads worth filing (as suggestions, for
  the `rp_planning` skill).

Keep it concise and professional. State conclusions plainly; mark uncertainty as uncertainty.
Write in the project's domain language ([`terminology.md`](../../../docs/guide/terminology.md)) —
exact terms, no banned ones.

## 4. Index it

Add a row to [`reviews/README.md`](../../../reviews/README.md) — date, a link to the doc, and a
one-line description of what it covers and the commit its links were verified at. Create the
index if it does not exist.

## 5. Land it — worktree + branch + PR

A review touches only `reviews/` (the new doc plus its index row), so it is not a bead and does
not go through the dev → QA loop. It still runs in **its own git worktree**, never the main
clone's tree: the orchestrator works out of the main clone, and checking out a review branch
there moves its `HEAD` and stalenesses its `main` ref, interfering with in-flight orchestration.
Like every change, it reaches `main` through a pull request — **never a direct push**:

1. Create an isolated worktree off up-to-date `origin/main`, on branch `reviews/<slug>`:

   ```bash
   git fetch origin && git worktree add .claude/worktrees/reviews-<slug> -b reviews/<slug> origin/main
   ```

   Write the review doc and index row inside that worktree (`.claude/worktrees/reviews-<slug>/`),
   not the main clone.
2. Commit only the review doc and its `reviews/README.md` index row — nothing else. A review
   never edits product code or bead state.
3. Push the branch, then open the PR with [`scripts/forge`](../../../scripts/forge)
   (`forge pr-create reviews/<slug> main <title> <body>`). Run `forge` **from the main clone**,
   not the worktree — it reads its token from `.secrets/forge.env`, which is gitignored and
   exists only in the main clone.
4. **Never merge it yourself.** The default is human review. Add the PR trigger `auto-merge`
   label only when the review needs no human sign-off **and** your auto-merge policy permits
   docs-only changes to land unattended.
5. Once the PR is open, remove the worktree so the clone stays clean —
   `git worktree remove .claude/worktrees/reviews-<slug>`. The branch lives on the remote until
   it merges; never leave a review branch checked out in the main clone.

## 6. Report

Give the user the verdict in a few lines, a link to the document, and the PR. Do not act on the
recommendations — that is the user's call, routed through planning.
