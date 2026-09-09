---
title: Coding principles
summary: Stack-independent design principles — boundaries as injection seams, measurability, determinism, typed provenance, errors per boundary, and binding terminology.
updated: 2026-08-05
status: living
related: [docs/guide/terminology.md, docs/adapters/stack.md]
---

# Coding principles

The reasoning behind how this project is put together. These are design principles, independent
of the language; the [stack adapter](../adapters/stack.md) and any language-practices doc it
links cover the language-level how.

<!-- Keep, cut, or extend these per project — but each principle here is one the kit's loop
     leans on (QA verifies against them), so removals should be deliberate. -->

## Boundaries are injection seams

Decide dependency direction up front. Anything that needs decoupling — to test a component in
isolation, or to swap one implementation for another — crosses an interface the consumer owns,
never a concrete implementation. A component depends on the *shape* it needs, not on who
provides it.

## When to split a file into modules

Reach for a split when a file holds work that pulls in different directions, not merely when it
grows long. Split on these triggers, in priority order:

- **Conceptual seam.** The file holds two or more things that change for different reasons — a
  data vocabulary and the logic that consumes it, a parser and its error taxonomy. This is the
  strong signal; a seam is worth a module even in a short file.
- **Navigation friction.** You scroll to orient, or jump between clusters that never reference
  each other. Independent clusters read better as separate files.
- **Divergent module docs.** You would write two different header comments for one file. Two
  headers means two modules; give each its own file and header.
- **Compile and churn isolation.** A hot cluster under active change sits next to a stable one.
  Splitting keeps unrelated churn off the stable code.

Pure size is the weakest reason and usually a symptom of one of the above: a long file is a
prompt to look for the seam, not a trigger on its own.

## Measurability is a boundary requirement

If the project must put a quality number on a component, that component needs a defined input
and a defined output, decoupled from its neighbors — the measurement requirement drives the
boundaries. A component that cannot be exercised in isolation is a component whose boundary is
wrong.

## Provenance is typed

The failure mode to design against is the right answer reached by the wrong route. Make the
route a first-class, typed value rather than a side effect: ids are distinct types, not bare
integers or strings; categories are enums, not free text; a computed result carries how it was
computed, so the route can be inspected and scored, not just its endpoint.

## Determinism

Outputs feed diffs — across runs, and against other systems. Non-deterministic output (iteration
order that depends on hashing, unsorted collections) makes those diffs noise. Avoid
order-dependent output: use ordered maps, or sort before emitting. Determinism is a prerequisite
for snapshot tests; without it they are not stable.

## Errors per boundary

Each layer owns its own error type, converted at the boundary as it propagates outward; the top
binary collapses to a single dynamic error. There is no shared, project-wide error enum that
every layer imports — that would be a dependency cycle in spirit and a coupling point in
practice. An error's type says which layer it came from.

## Terminology is binding

Names in code — variables, types, functions, modules, files — use the project's
[domain language](terminology.md), the same terms as the docs and the beads. A concept has one
name across the whole system. When a needed concept has no term yet, add it to the terminology
doc in the same change rather than coining an ad-hoc name, and never use a banned term.

## Small, independently-verifiable units

Work is tracked as [beads](beads-usage.md) sized to the smallest unit a reviewer can verify by
evidence, and the code follows the same grain: a change should be checkable on its own. The seam
that makes a component testable in isolation is the same seam that makes a bead independently
verifiable.
