---
title: Beads usage
summary: How work is tracked in beads — remote Dolt state, statuses, review labels, and common commands.
updated: 2026-08-05
status: living
---

# Beads usage

This project tracks all work in beads (`bd`). Run `bd prime` for command help.

## Remote-backed state

Bead state lives in Dolt and syncs to the git ref `refs/dolt/data` on the project
remote, separate from product-code branches. The remote is the source of truth; local
`.beads/` working files are gitignored.

- `bd dolt pull` — fetch the latest bead state; run before working and again after every push.
- `bd dolt push` — publish local bead changes.

Pull before a write and pull again after it. A push sends local changes to the remote but does
not refresh the local read view when history has diverged with another actor, so `bd list` /
`bd show` keep showing stale state until the reconciling pull.

## Statuses

The normal path is `open → in_progress → closed`. Only built-in statuses are used, so
every viewer renders them.

| Status        | Category | Meaning                                  |
|---------------|----------|------------------------------------------|
| `open`        | active   | Available to work; appears in `bd ready`.|
| `in_progress` | wip      | Being worked on.                         |
| `blocked`     | wip      | Blocked by a dependency.                 |
| `deferred`    | frozen   | Postponed; revisit later.                |
| `closed`      | done     | Complete.                                |

Categories control behavior: `active` appears in `bd ready`; `wip` is hidden from ready
but shown in `bd list`; `frozen` and `done` are hidden from both.

## Review labels

A task stays `in_progress` through review and carries a **STATUS** label for the stage;
**REQUIREMENT** labels, set once at plan time, decide how the PR merges. See the
[development lifecycle](development-lifecycle.md) for the full gate.

```bash
bd label add <id> in-qa-review        # STATUS: work is in QA (bead only until a PR exists; also on the PR during a feedback round)
bd label add <id> in-human-review     # STATUS: QA opened a PR; awaiting human review (bead + PR)
bd label add <id> allows-auto-merge   # REQUIREMENT (bead permission): opt-in to unattended merge; absence = human review
bd label add <id> requires-adr        # REQUIREMENT: needs an ADR; overrides allows-auto-merge
```

The QA queue is `bd list --status in_progress --label in-qa-review`. On a pass QA opens a PR and
the orchestrator swaps `in-qa-review` for `in-human-review`; on a bounce the label is removed to
return the task to plain `in_progress`. `in-human-review` is mirrored on both the bead and the
PR and appears only while a human is the gate. During a feedback round (a human sends an open PR
back with comments) the orchestrator swaps `in-human-review` → `in-qa-review` on both the bead and
the PR for the whole round, and swaps it back only after QA re-pushes the revision and replies on
the threads — so the human's review queue lists only PRs awaiting them.

The bead permission `allows-auto-merge` and the PR trigger `auto-merge` are **distinct** labels:
QA does not mirror the bead label onto the PR — it **translates** a bead's `allows-auto-merge`
(and no `requires-adr`) into `auto-merge` on the PR, which the auto-merge workflow acts on.
`auto-merge` and `in-human-review` are mutually exclusive on a PR. QA also maps a bead's
`requires-adr` to the PR signal `contains-adr` (which never auto-merges).

## Deferring

Defer a task to set it aside without blocking:

```bash
bd defer <id>                     # postpone indefinitely
bd update <id> --defer <date>     # postpone until a date
```

Deferred tasks are hidden from `bd ready` but remain in `bd list`.

## Common commands

- `bd ready` — unblocked tasks.
- `bd show <id>` — task detail; acceptance criteria are the definition of done.
- `bd update <id> --claim` — assign and set `in_progress`.
- `bd label add <id> in-qa-review` — hand off to QA.
- `bd close <id> --reason "..."`.

## Writing rules

Bead-state transitions and `bd dolt push` are serialized through a single writer. Other
agents query read-only with `bd --readonly`.
