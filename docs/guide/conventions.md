---
title: Conventions
summary: How this project's docs are written and maintained — the frontmatter schema, the concise-content rule, and the amend-vs-supersede rubric.
updated: 2026-08-05
status: living
---

# Conventions

How docs under `docs/` are written and kept honest. [Terminology](terminology.md) governs the
words; this governs the form.

## Frontmatter

Every doc under `docs/` opens with a YAML frontmatter block. The forge folds it by default, so it
costs the reader nothing; the [docs index](../README.md) and the CI check read it.

```yaml
---
title: <index link text>
summary: <one line, no "|" — used verbatim in the index>
updated: YYYY-MM-DD                     # last content change
status: living | draft | deprecated     # ADRs: proposed | accepted | superseded | deprecated
related: [repo-relative paths]           # optional
---
```

`title` and `summary` are required. The folder already says the type (`guide/`, `adr/`), so
there is no `type` field. Add a field only once something consumes it.

## Content

The header carries the metadata so the body can be **plain**. Write for a reader, not a
scorecard:

- Concise and declarative — one idea per sentence. No buzzword stacking; don't re-incant a
  concept's full name every sentence — name it once and move on.
- Define each term once (in [Terminology](terminology.md)) and use it plainly thereafter.
- Convey structure in prose, lists, and tables. For genuinely structural content — a dependency
  graph, a pipeline, a data model — a [mermaid](https://mermaid.js.org) diagram is allowed;
  the forge renders it. Never hand-drawn ASCII or text diagrams.
- Prefer specific names to generic labels; link to code and beads rather than restating them.
- No meta-notes about the writing itself.

## Maintaining a doc

Classify every change as minor or substantive first.

- **Minor** (typo, link, a clarifying sentence, a frontmatter field): edit in place.
- **Substantive**:
  - **ADR** — never rewrite a decided one. Write a new ADR, set the old one `status: superseded`,
    and update the [ADR index](../adr/README.md); the old file stays as the record of what we
    believed then.
  - **Everything else** — amend in place; never delete the rationale behind a decision. When a
    later decision overtakes part of a doc, add an inline pointer to the ADR that governs it.

If you can't tell whether the doc is stale or the code drifted, don't guess — file a `doc-debt`
bead and flag it.

## The index

The generated list in [`docs/README.md`](../README.md) is built from frontmatter by
[`scripts/gen-doc-index`](../../scripts/gen-doc-index); the "Important" list is hand-curated. Run
the generator after adding, renaming, or re-summarising a doc — CI fails if the index is stale or
a doc is missing `title`/`summary`. Cross-link by repo-relative path.
