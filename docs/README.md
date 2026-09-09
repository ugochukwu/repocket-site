---
title: Documentation
summary: Index of this project's documentation.
updated: 2026-08-05
status: living
---

# Documentation

## Important

Documents a human will want to read.

- [Getting started](guide/getting-started.md) — prepare a fresh clone.
- [Development lifecycle](guide/development-lifecycle.md) — how a change moves from bead to merge.
- [Conventions](guide/conventions.md) — how docs are written and maintained.
- [Terminology](guide/terminology.md) — the binding domain language for all code and docs.

## Others

All documents, by folder. This list is generated — run `scripts/gen-doc-index` after adding or
renaming a doc.

<!-- BEGIN generated: docs index (scripts/gen-doc-index) -->

### adapters/

- [Forge adapter](adapters/forge.md) — GitHub via the gh CLI — configuration, the forge verb interface, and GitHub-specific conduct rules for the Repocket site repo.
- [Stack adapter](adapters/stack.md) — Every command an agent runs against Repocket-site's code — build, test, lint, the CI-mirror quality gate, running the site, and the UI render check.

### adr/

- [ADR index & conventions](adr/README.md) — Index of architecture decision records and the one-file-per-decision / supersede-not-edit conventions.

### design/2026-09-09-repocket-launch/

- [Design handoff: Repocket landing site (2026-09-09)](design/2026-09-09-repocket-launch/README.md) — The binding design handoff for the Repocket marketing site — a complete static site under site/ with locked colors, type, copy, and section order; describes what to publish, which placeholders to resolve, and what verification acceptance means (Lighthouse ≥95/95, both languages render, reduced-motion respected).

### guide/

- [Beads usage](guide/beads-usage.md) — How work is tracked in beads — remote Dolt state, statuses, review labels, and common commands.
- [Coding principles](guide/coding-principles.md) — Stack-independent design principles — boundaries as injection seams, measurability, determinism, typed provenance, errors per boundary, and binding terminology.
- [Conventions](guide/conventions.md) — How this project's docs are written and maintained — the frontmatter schema, the concise-content rule, and the amend-vs-supersede rubric.
- [Development lifecycle](guide/development-lifecycle.md) — How a change moves from bead to merged PR through the orchestrator, dev-implementer, and qa-verifier roles.
- [Getting started](guide/getting-started.md) — TEMPLATE: prepare a fresh clone — repository access, beads tooling, the forge token, and project-specific harnesses.
- [Terminology](guide/terminology.md) — Repocket's binding domain language for code, docs, ADRs, bead titles, and PR text.

<!-- END generated -->
