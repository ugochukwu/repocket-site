---
title: ADR index & conventions
summary: Index of architecture decision records and the one-file-per-decision / supersede-not-edit conventions.
updated: 2026-08-05
status: living
---

# Architecture Decision Records

Short, durable records of **why** a significant architectural choice was made — the context, the
decision, and its consequences — so contributors (human or agent) don't reverse-engineer intent
from the code or re-litigate settled trade-offs.

## Index

| # | Date | Title | Status |
|---|------|-------|--------|

<!-- Add a row per ADR, newest at the bottom. -->

## Conventions

- **One file per decision**, named `YYYY-MM-DD-<kebab-slug>.md` — the date sorts them
  chronologically, the slug makes them greppable.
- Give each an incrementing **ADR number** (`ADR-000N`) in its title and add a row above in the
  same change. Newest at the bottom.
- Sections: **Status · Date · Context · Decision · Consequences** (add *Options considered* /
  *References* when useful). Keep it tight; link to code and beads rather than restating them.
- **Status** is one of `Proposed` · `Accepted` · `Superseded by ADR-000M` · `Deprecated`. Don't
  edit a decided ADR's substance — supersede it with a new one and update both statuses.
- A bead governed by an ADR carries the `requires-adr` label and names the ADR file in its
  description, so the work and the rationale point at each other. An ADR-bearing PR never
  auto-merges — see the [development lifecycle](../guide/development-lifecycle.md).
