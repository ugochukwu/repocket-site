---
name: rp_planning
description: >-
  Turn a feature, requirement, or goal into well-formed beads ready to work — testable
  acceptance criteria, correct type and priority, dependencies, and a per-ticket decision on
  whether it auto-merges or needs human review. Use when breaking down new work, filing an
  epic, or refining vague tickets before they are claimed.
---

# Plan

Turn intent into beads that a dev-implementer can build against without re-asking. This runs in
the main loop, which is the single writer for bead state: `bd dolt pull` before creating,
`bd dolt push` after.

## 1. Understand the work

Do not write a single bead until you and the user are aligned on what the work is. Gather the
requirement from the user and the codebase, restate the goal in your own words, and **keep asking
until the ambiguity is gone** — surface the open questions, the assumptions you would otherwise
make, the edge cases, and where scope should stop. Treat "I'll guess and file it" as a failure
mode: a wrong shared understanding here propagates into every bead. Only once the user confirms
your restatement is correct do you move on. Do not invent scope the user did not ask for.

Alignment applies to edits, not just first creation: reach agreement in discussion, then apply
ticket changes in a single batch — never edit a ticket reactively after each message. Before
creating or editing any bead, confirm it is not already `in_progress`; never write to a bead the
orchestrator is working — route the change to the PR or a follow-up instead.

## 2. Shape the beads

Word every bead in the project's domain language ([`terminology.md`](../../../docs/guide/terminology.md)) —
titles, descriptions, and acceptance criteria use the exact terms, never a banned one.

Break the work into the smallest units that are independently verifiable. For each bead set:

- **Title** — a concrete outcome, not a task area.
- **Type** — `feature`, `task`, `bug`, `chore`, or `epic` for a parent that groups children.
- **Acceptance criteria** — the definition of done, written so QA can verify them by evidence
  (a command to run, an output to observe, a behavior to exercise). If you cannot make a
  criterion testable, the bead is not ready — split or clarify it.
- **Priority** — relative to the current backlog, not in the abstract.
- **Dependencies** — `--deps` for hard ordering; record `discovered-from:<id>` when a bead came
  out of other work; parent an epic's children with `--parent`.

Create them through the single writer:

```bash
bd dolt pull
bd create "<title>" -t <type> --acceptance "<criteria>" -p <priority> [--parent <epic>] [--deps ...]
```

## 3. Decide the merge path (ask, per ticket)

Every bead lands through a PR. At plan time, decide for each whether it may merge unattended.
**Ask the user per ticket (or per epic), with an educated suggestion:**

- **Suggest `allows-auto-merge`** for work an agent should land on its own — mechanical or
  low-risk changes, build-loop fixes, docs, isolated additions with strong tests.
- **Suggest human review (no label)** for anything touching core behavior — the project's core
  algorithms, schema or data-model changes, public contracts, architecture. These take the
  human-review path and, when the decision is significant, get an ADR.

Apply the decision:

```bash
bd label add <id> allows-auto-merge          # only for tickets the user approved for auto-merge
bd label propagate allows-auto-merge <epic>  # push the decision to an epic's children
```

Leave everything else unlabelled — **absence of `allows-auto-merge` means human review**, the
safe default, so a forgotten label never lands unattended. `allows-auto-merge` is a **bead**
permission, set **only here, at plan time**; it never goes on the PR. QA later translates it into
the PR trigger `auto-merge`, but never adds `allows-auto-merge` itself.

## 4. Flag ADR-worthy decisions

If a bead involves a library switch, an architecture change, or a larger schema change, it needs
an ADR under `docs/adr/`. Mark it both ways so the signal survives the whole flow:

- **Label** — `bd label add <id> requires-adr`. This is the machine-readable flag; QA maps it to
  `contains-adr` on the PR, and it forces the human-review path (a `requires-adr` bead overrides
  `allows-auto-merge` and is never auto-merged).
- **Description** — say which decision needs the ADR, so a reader knows why without cross-checking.

```bash
bd label add <id> requires-adr
```

## 5. Publish and report

```bash
bd dolt push
```

Report the beads you created: id, title, type, priority, merge path (`allows-auto-merge` or
human review), and any `requires-adr` flags. Keep it a skimmable list.
