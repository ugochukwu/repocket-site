---
name: setup
description: >-
  One-time, re-runnable setup for a clone of this project — fill in and validate the kit's
  adapters on first drop-in, verify the local environment from the getting-started guide, and
  seed the project's load-bearing agent rules into this machine's memory. Use when dropping the
  agent kit into a new project, setting up a fresh clone, onboarding a new machine, or after the
  rules or setup steps in the docs change.
---

# Setup

Run this once per clone, and again whenever the rules or setup steps change. It does three
things: completes the kit's adapters on first drop-in, gets the local environment ready, and
seeds the rules that must survive across sessions into this machine's memory.

The repository is the source of truth. Memory entries are recall triggers that point back to
it — never a divergent copy. If a memory entry and the doc disagree, the doc wins.

## 0. Adapters (first drop-in only)

The kit's core never hardcodes project specifics; two adapter files and one content template
hold them. Check each for leftover `TODO` markers and walk the user through filling them —
ask, don't guess:

- [`docs/adapters/stack.md`](../../../docs/adapters/stack.md) — build/test/lint commands, the
  CI-mirror quality gate, run-the-app, the UI render check (or "no UI"). Derive suggestions
  from the repo (build files, existing CI) and confirm them with the user.
- [`docs/adapters/forge.md`](../../../docs/adapters/forge.md) — `FORGE_API` and `FORGE_REPO`
  in `.secrets/forge.env` (copy from [`.secrets/forge.env.example`](../../../.secrets/forge.env.example)).
- [`docs/guide/terminology.md`](../../../docs/guide/terminology.md) — the binding domain
  language. If it is still the template, tell the user the loop can run without it but every
  naming decision is ungoverned until it is filled; offer to draft it from the codebase for
  their review.

Then check the repo-side wiring, and report what is missing rather than fixing silently:

- Labels exist on the forge: `scripts/forge seed-labels` (idempotent).
- Branch protection: no direct pushes to `main`, the CI check required, up-to-date-with-main
  enforced. Agents cannot set this; give the user the exact settings to click.
- `.gitignore` covers `.beads/`, `.secrets/`, `.claude/worktrees/`.
- CI: `.forgejo/workflows/ci.yml`'s quality-gate job matches the stack adapter's list.

A kit with unfilled adapters must not run the orchestrate loop — say so plainly.

## 1. Environment

Work through [getting-started](../../../docs/guide/getting-started.md). For each item, check
first and act only if it is missing.

- **Tooling** — `bd version` and `bv --version` succeed. If not, give the user the
  `brew install` commands from the guide; do not install silently.
- **Bead state** — run `bd dolt pull` to sync from `refs/dolt/data`.
- **Bead actor** — `git config user.name` is set (bd uses it as the actor). If empty, ask
  the user what to set it to.
- **Forge token** — `.secrets/forge.env` exists and defines `FORGE_TOKEN`. If missing, walk
  the user through the getting-started token steps. Never print the value.
- **Stack tooling** — the commands in the stack adapter's quality gate actually run on this
  machine; report any missing tool with its install step.

Report what you verified, what you fixed, and what the user must still do themselves
(installs, creating the token, branch protection) — those need a human.

## 2. Rules → memory

For each rule below, check this machine's memory. If it is missing, write a memory entry
(`type: feedback`) that states the rule and links the canonical doc. If it exists but has
drifted from the doc, update it. Then report which rules you added, updated, or left as-is.

- **No agent merges a pull request** — not via the UI, the API, or a token, not even for its
  own changes. Merging is the auto-merge workflow (deny-list permitting) or a human. This is
  enforced only by this rule, so it must not be forgotten.
  → [development-lifecycle.md](../../../docs/guide/development-lifecycle.md)
- **The orchestrator does not write product code** — every change goes dev-implementer →
  qa-verifier; no self-implementing, self-verifying, or self-closing. If subagents cannot run
  or keep failing, STOP and ask the user; never quietly do the work in the main loop.
  → [development-lifecycle.md](../../../docs/guide/development-lifecycle.md)
- **One writer for bead state** — only the orchestrator writes beads and runs `bd dolt push`;
  subagents query read-only. Pull before claiming, push after every transition.
  → [development-lifecycle.md](../../../docs/guide/development-lifecycle.md),
  [beads-usage.md](../../../docs/guide/beads-usage.md)
- **Pull after every push** — the full sync cycle is pull → change → push → pull. A `bd dolt
  push` does not refresh the local read view when history has diverged, so run `bd dolt pull`
  immediately after to reconcile with concurrent writers on `refs/dolt/data`.
  → [development-lifecycle.md](../../../docs/guide/development-lifecycle.md),
  [beads-usage.md](../../../docs/guide/beads-usage.md)
- **QA verifies results, not just diffs** — for user-facing changes, check the rendered
  output against the intent, not only the code diff or DOM.
  → [development-lifecycle.md](../../../docs/guide/development-lifecycle.md)
- **Commands come from the adapters** — build/test/lint and forge configuration are read from
  `docs/adapters/`, never guessed or recalled.
  → [stack.md](../../../docs/adapters/stack.md), [forge.md](../../../docs/adapters/forge.md)

## Keeping this current

This skill is the seeding manifest. When a rule is added or changed in the docs, update the
list above and re-run so every machine's memory refreshes.
