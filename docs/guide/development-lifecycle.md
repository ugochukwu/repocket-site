---
title: Development lifecycle
summary: How a change moves from bead to merged PR through the orchestrator, dev-implementer, and qa-verifier roles.
updated: 2026-08-05
status: living
---

# Development lifecycle

All work is tracked in beads (`bd`) and moves through a fixed sequence of roles to a pull
request. Nothing is pushed to `main` directly. This document is the process spec; the skills
and agents under `.claude/` implement it.

## Roles

| Role | Does | Never |
|------|------|-------|
| **Orchestrator** (main loop) | Plans and claims beads, dispatches subagents, owns bead state, git, and sync, keeps open PRs current with `main`, closes each bead once its PR merges, relays status. | Writes product code. |
| **dev-implementer** | Implements one bead against its acceptance criteria, self-verifies, commits locally, hands off for review. | Pushes, opens a PR, merges, or closes its own work. |
| **qa-verifier** | Adversarially verifies a bead against its acceptance criteria; on a pass, pushes the branch, opens the pull request, and carries the bead's labels onto it. Refuses to pass anything it cannot verify. | Writes product code, or merges. |

Each role refuses work outside its scope and points to the role that owns it.

**No agent ever merges a pull request** — not through the UI, the API, or a token, and not
even for its own infrastructure changes. Merging is done only by the auto-merge workflow
(deny-list permitting) or by a human. Agents push branches, open PRs, apply labels, and
comment.

## The loop

The orchestrator claims an open bead and dispatches a dev-implementer, which builds it and
commits on a local branch. A qa-verifier then verifies the work against the bead's acceptance
criteria and, on a pass, pushes the branch and opens the pull request — dev never pushes or
opens one, so only reviewed work reaches the remote. From there the PR either merges
automatically (`allows-auto-merge`) or waits for a human. The orchestrator closes the bead once
its PR merges.

## Isolation

Every bead runs in its own **git worktree** at `.claude/worktrees/<id>` (gitignored) on branch
`bd/<id>`. The orchestrator creates it when dispatching dev, dev and qa work only inside it, and
the orchestrator removes it once the PR merges. The main clone's working tree stays on `main` and
is never used for bead work.

This is not just tidiness: one clone has a single `HEAD` and index, so two actors doing branch
work in the same tree collide — one actor's `git checkout` carries another's uncommitted changes
onto the wrong branch. Worktrees give each bead its own `HEAD`, so a planning session, an
orchestrator, and several in-flight beads coexist in one clone without stepping on each other. No
agent ever runs `git checkout` on a bead branch in the main clone.

## Ticket lifecycle

Status stays built-in (so every viewer renders it); the review stage is carried by a STATUS
label.

| State | Meaning | Set by |
|-------|---------|--------|
| `open` | Ready to claim. | plan |
| `in_progress` | Claimed, being worked. | claim |
| `in_progress` + `in-qa-review` | In QA. Bead-only at the initial hand-off (no PR yet); during a feedback round it is also mirrored on the open PR (swapped from `in-human-review`). | orchestrator, at handoff |
| `in_progress` + `in-human-review` | QA opened a PR; awaiting human review. Mirrored on the bead and PR. | qa, unless the bead is `allows-auto-merge` |
| `closed` | PR merged. | orchestrator |

A QA bounce returns the bead to plain `in_progress` with rejection notes. `blocked` and
`deferred` apply as usual.

## Labels: status vs requirement

Labels split into two families. **STATUS** labels track lifecycle and change over time;
**REQUIREMENT** labels are set once at plan time and stay fixed.

| Label | Family | Where | Meaning |
|-------|--------|-------|---------|
| `in-qa-review` | STATUS | bead — and PR during a feedback round | Work is in QA. Bead-only at the initial hand-off (no PR yet); during a feedback round it is also mirrored on the open PR — swapped from `in-human-review` — so the human's review queue lists only PRs awaiting them. Mutually exclusive with `in-human-review`. |
| `in-human-review` | STATUS | bead + PR | A human must review the PR and report back. Present **only** while awaiting a human, mirrored on both. Mutually exclusive on the PR with `auto-merge`. |
| `allows-auto-merge` | REQUIREMENT | bead only | Plan-time **permission** that this bead's PR may auto-merge. **Absence means human review** (the safe default). Never on the PR; QA translates it into `auto-merge`. |
| `auto-merge` | PR TRIGGER | PR | The label the auto-merge workflow acts on. QA sets it from the bead's `allows-auto-merge` when there is no `requires-adr`. Mutually exclusive with `in-human-review`. |
| `requires-adr` | REQUIREMENT | bead only | Bead needs an ADR to be mergeable. **Overrides `allows-auto-merge`** (never auto-merges). |
| `contains-adr` | PR SIGNAL | PR | An ADR is in this PR; the workflow excludes it from auto-merge. Set by QA when the bead has `requires-adr`. |

**Invariant:** `in-human-review` marks *awaiting-human* and appears only then, mirrored on bead
and PR. A feedback round swaps it to `in-qa-review` on both — the orchestrator owns the swap and
QA never touches these STATUS labels on a re-verification — and it is restored only after the QA
re-pass.

## Review gate

Every change lands through a pull request; there are no direct pushes to `main`. dev commits
locally and hands off — **only qa-verifier pushes the branch and opens the PR**, and only after
an adversarial pass, so unreviewed work never reaches the remote. On a pass QA translates the
bead's requirements into PR labels — `auto-merge` when the bead has `allows-auto-merge` and no
`requires-adr`, otherwise `in-human-review` (never both), plus `contains-adr` when the bead has
`requires-adr` — then writes a **concise** summary, but never merges.

How the PR then merges depends on the bead's requirement labels, a plan-time decision:

- **`allows-auto-merge`** — QA sets `auto-merge` on the PR and the repo merges it automatically
  once its checks pass. Use it for work an agent should land unattended (e.g. a build-loop fix);
  propagate it across an epic's children with `bd label propagate allows-auto-merge <epic>`.
- **No label (default)** — the PR is labelled `in-human-review` and waits for a human to review,
  resolve every thread, and merge.
- **`requires-adr`** — a major change (library switch, architecture change, larger schema change)
  is tagged `requires-adr` at plan time and is never auto-merged; QA sets `contains-adr` on the
  PR, opens the description with `⚠️ Contains ADR-000N — review the decision first.`, and it
  takes the human-review path.

If the project has user-facing UI (see the [stack adapter](../adapters/stack.md)), a **UI or
user-facing bead** may carry `allows-auto-merge` like any other, but its auto-merge is gated on a
rendered-result check that runs **locally, not in CI**: before opening the PR, QA drives and
screenshots the real app on the PR's branch and verifies the rendered result against the bead's
intent. This **local render check** is the render gate. Only on a passing render does QA
translate the bead's `allows-auto-merge` into the PR `auto-merge` trigger — a failing render is a
bounce, so no UI PR reaches `auto-merge` without a verified render.

Branch protection enforces the mechanical guarantees: no direct pushes to `main`, the required
CI check must pass before any merge (this is where CI attaches), and the branch must be up to
date with `main` — a stale branch cannot merge, so the orchestrator
keeps open PRs current by merging `main` into them (dev merges, QA re-verifies and pushes),
never by rebasing: a rebase rewrites commit SHAs and force-pushing detaches the inline review
comments anchored to them, whereas a merge keeps the history stable. Branch protection does
**not** stop an agent that holds a merge-capable token from merging a PR itself — that restraint
is the "no agent merges" rule above, not a server control.

## Addressing PR comments

When a human leaves comments, the orchestrator runs the **feedback round**. For the whole round
the work is back with dev and QA, so it is no longer the human's turn: its STATUS label moves off
`in-human-review` until QA re-passes — the human's PR-review list should only ever show PRs
awaiting them.

1. Fetch unresolved comment threads.
2. **Enter the round:** the orchestrator swaps `in-human-review` → `in-qa-review` on **both** the
   bead and the PR. `contains-adr` and the REQUIREMENT labels stay put.
3. dev-implementer addresses each actionable one, committing locally on the branch.
4. qa-verifier re-verifies, pushes the update, and **replies on each thread** confirming it is
   fulfilled. **QA never touches the `in-qa-review` / `in-human-review` STATUS labels on a
   re-verification** — the orchestrator owns them, so there is no race. A bounce keeps the round
   at `in-qa-review`.
5. **Close the round:** only after the QA re-pass, the orchestrator swaps `in-qa-review` →
   `in-human-review` back on both the bead and the PR, then posts one concise summary.

Agents never resolve threads. A human resolves each thread once satisfied, and the change
merges only after **every thread on the PR is resolved**.

## Claiming and coordination

Multiple humans may run their own orchestrator against the shared bead state on
`refs/dolt/data`. `bd` attributes each claim to the repository's git `user.name`, so no
extra identity is needed — the git config every contributor already sets is the actor.

`--claim` sets the assignee and rejects a bead already held by another actor — but only
against the local database. Cross-clone safety therefore requires a fixed order:

```bash
bd dolt pull && bd update <id> --claim && bd dolt push
```

- **Pull before claiming** so the local view is current; **push right after** so the claim
  is visible to other pools.
- If the push is rejected, pull, confirm the bead was not claimed by someone else, then
  retry or pick another.
- Before taking a bead, check: latest pulled · not owned by another pool · dependencies
  satisfied (`bd ready` filters these) · no existing branch or PR.

Query ownership with `bd list --assignee <actor>`; find free work with
`bd list --no-assignee`.

## Sync discipline

- `bd dolt pull` before a work cycle and before every claim.
- `bd dolt push` after every state transition (claim, `in-qa-review`, `in-human-review`, close).
- `bd dolt pull` again immediately after every `bd dolt push` — the full cycle is
  pull → change → push → pull. A push does not refresh the local read view when history has
  diverged, so the following pull reconciles the local database with concurrent writers on
  `refs/dolt/data`.
- Within a pool, only the orchestrator writes bead state; subagents query read-only
  (`bd --readonly`).

Small, frequent pushes keep pools from diverging.
