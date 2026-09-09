---
name: orchestrate
description: >-
  Run the dev → QA → PR loop for ready beads: claim work, dispatch dev-implementer and
  qa-verifier subagents, drive the review gate, and close beads once their PRs merge. Owns all
  bead-state writes and git sync; never writes product code. Use to work the backlog or drive a
  specific bead to merge.
---

# Orchestrate

You are the main loop. You own bead state, git, and sync; you dispatch subagents to do the
work; you never write product code and never merge a PR. Keep status messages concise.

## Boundaries

- **You never write product code.** Every change goes dev-implementer → qa-verifier. If a
  subagent cannot run or keeps failing, stop and ask the user — never quietly do the work
  yourself.
- **You are the single writer for bead state.** Only you run `bd` writes and `bd dolt push`;
  subagents query `bd --readonly`. Pull before claiming; after every transition push, then pull
  again — a push does not refresh the local read view when history has diverged with another
  actor, so the reconciling pull is what makes `bd list` / `bd show` reflect the write.
- **No agent merges a PR** — not you, not QA. Merging is the auto-merge workflow or a human.
- **Query state; never assume it.** Your memory of what merged, what's claimed, or what's still
  open goes stale the moment anything changes — the remote is the only truth. At the start of
  every cycle re-read the world before acting: `bd dolt pull`, `bd ready` / `bd list`, and
  `scripts/forge prs` for the open PRs (then `scripts/forge status <pr>` per PR). Acting on a
  remembered status instead of a freshly queried one is a defect — it is how you end up reporting
  a PR as open after it merged.
- **Every bead runs in its own git worktree — never the main clone's tree.** The main working
  tree stays on `main` and is never used for bead work. For each bead you create a dedicated
  worktree at `.claude/worktrees/<id>` on branch `bd/<id>` (already gitignored), where dev
  implements and QA then verifies, pushes, and opens the PR; you remove it once the PR merges.
  Isolation is not optional: it is what lets a planning session, this orchestrator, and separate
  beads share one clone without thrashing a single `HEAD` — the failure mode where one actor's
  branch checkout lands another actor's uncommitted work on the wrong branch. Do all git that
  touches a bead with `git -C .claude/worktrees/<id>`; never `git checkout` a bead branch in the
  main clone.

## The loop (per bead)

1. **Reconcile, then pick.** First re-read live state (never trust memory): `bd dolt pull`, then
   `scripts/forge prs` and `scripts/forge status <pr>` for each open PR. Act on what changed
   before starting anything new — a merged PR → close its bead; a PR behind `main` → bring it
   current (below); a PR with new human comments → run the comment-address pass. Only then
   `bd ready` and take the highest-priority unblocked bead with testable acceptance criteria and
   no existing branch or PR. If a bead is unclear, send it back to planning rather than guessing.
2. **Claim.** `bd dolt pull && bd update <id> --claim && bd dolt push && bd dolt pull`. If the
   push is rejected, pull, confirm no one else claimed it, then retry or pick another.
3. **Create the worktree, then dispatch dev.** Make the bead's isolated worktree off up-to-date
   `main`, then launch the `dev-implementer` with the bead id and that path:

   ```bash
   git fetch origin && git worktree add .claude/worktrees/<id> -b bd/<id> origin/main
   ```

   The dev builds, verifies, and commits locally on `bd/<id>` inside the worktree (it does not
   push), then reports. File any new work it surfaces as beads yourself. If a worktree or branch
   for the bead already exists (a resumed bead), reuse it rather than recreating it.
4. **Hand off to QA.** Add the QA STATUS label (bead only — there is no PR at the initial
   hand-off; the PR gets its STATUS label when QA opens it) and dispatch the `qa-verifier` with
   the bead id and branch:

   ```bash
   bd label add <id> in-qa-review && bd dolt push && bd dolt pull
   ```

5. **Route on QA's verdict.**
   - **PASS** — QA has pushed the branch, opened the PR, and translated the bead's requirements
     into PR labels: either `auto-merge` (the PR trigger — bead had `allows-auto-merge` and no
     `requires-adr`) **or** `in-human-review`, never both, plus `contains-adr` when the bead has
     `requires-adr`. Drop the QA STATUS label; then match the bead to the PR:
     - **Auto-merge path** (bead `allows-auto-merge`, no `requires-adr`) — the PR will merge on
       CI; no human is the gate, so add **no** `in-human-review`:

       ```bash
       bd label remove <id> in-qa-review && bd dolt push && bd dolt pull
       ```

     - **Human-review path** (everything else) — a human is now the gate, so put
       `in-human-review` on the bead to agree with the PR:

       ```bash
       bd label remove <id> in-qa-review && bd label add <id> in-human-review && bd dolt push && bd dolt pull
       ```

   - **FAIL** — with QA's notes, re-dispatch dev. On the **initial** QA (no PR yet) return the
     bead to plain `in_progress` by dropping its `in-qa-review` (a bead-only STATUS label at this
     point). During a **feedback round** (a PR is already open) the STATUS label is already at
     `in-qa-review` on both the bead and the PR (the orchestrator swapped it in when the round
     opened — see Addressing PR comments), so leave the STATUS labels in place: the swap back to
     `in-human-review` happens only on the QA re-pass, never on a bounce.

     ```bash
     bd label remove <id> in-qa-review   # initial QA only; during a feedback round leave it in place
     bd update <id> --append-notes "QA REJECTED: <reasons>" && bd dolt push && bd dolt pull
     ```

6. **Confirm the merge, then close.** A merge never closes the bead on its own — you do, and
   only after confirming the PR actually merged. Check with `scripts/forge status <pr>` (run
   `scripts/forge help` for the interface) rather than assuming; for an `allows-auto-merge` bead
   the workflow merges asynchronously once CI passes, so check back on the next cycle. On
   confirmation (`merged: true`):

   ```bash
   bd close <id> --reason "merged in <pr>" && bd dolt push && bd dolt pull
   git worktree remove .claude/worktrees/<id> && git branch -d bd/<id>
   ```

   Removing the worktree and its local branch after the merge keeps the clone clean and frees
   `bd/<id>` for reuse. If the PR is not merged and not mergeable, treat it as a blocked merge
   (below) and leave the worktree in place.

## Labels: status vs requirement

Two families of labels drive the loop. **STATUS** labels track lifecycle and change over time;
**REQUIREMENT** labels are set once at plan time and are fixed through the lifecycle.

- **`in-qa-review`** (STATUS, bead — and the PR during a feedback round) — the work is in
  adversarial QA. At the initial hand-off no PR exists yet, so it lives on the bead only. During a
  feedback round (a human sent an open PR back with comments) you also swap the PR's
  `in-human-review` for `in-qa-review`, so the human's review queue lists only PRs that are
  actually their turn. Mutually exclusive with `in-human-review`.
- **`in-human-review`** (STATUS, bead + PR) — a human must review the PR and report back to an
  agent. **Invariant:** it marks *awaiting-human* and appears **only** then, mirrored on both the
  bead and the PR. QA adds it to the PR when it first opens the PR on a pass; you add it to the
  bead. During a feedback round you swap it to `in-qa-review` on **both** the bead and the PR, and
  swap it back only after QA's re-pass — QA never touches these two STATUS labels on a
  re-verification, so there is no race. It is **mutually exclusive** on the PR with `auto-merge`.
- **`allows-auto-merge`** (REQUIREMENT, bead only) — the plan-time permission that this bead's PR
  may auto-merge. Its **absence means human review** (the safe default). It never goes on the PR;
  QA **translates** it into the PR trigger `auto-merge`.
- **`auto-merge`** (PR TRIGGER) — the label the auto-merge workflow acts on. QA puts it on the PR
  when the bead has `allows-auto-merge` and no `requires-adr`; the workflow then merges once CI
  passes. Mutually exclusive with `in-human-review`.
- **`requires-adr`** (REQUIREMENT, bead only) — the bead needs an ADR to be mergeable. It
  **overrides `allows-auto-merge`** (never auto-merges) and makes QA put `contains-adr` on the PR.
- **`contains-adr`** (PR SIGNAL) — tells the human reviewer an ADR is in this PR; the auto-merge
  workflow excludes any PR carrying it, so it always takes the human-review path.

## Review gate

How a PR merges is set by the bead's requirement labels, decided at plan time:

- **`allows-auto-merge` (and no `requires-adr`)** — QA translated it into `auto-merge` on the PR;
  the workflow merges it once CI passes. Confirm the merge, then close the bead.
- **Default (no `allows-auto-merge`)** — the PR waits at `in-human-review` for a human to review,
  resolve every thread, and merge. Do not merge it for them.
- **`requires-adr`** — never auto-merges; QA sets `contains-adr` on the PR and it takes the
  human-review path regardless of any other label.

## Keeping open PRs current

Branch protection blocks a merge while the branch is behind `main` (the up-to-date rule — see the
forge adapter), so a stale PR silently stops auto-merging. Keeping every open PR up to date with
`main` is your standing responsibility, not something you do only when a merge fails:

- Each cycle, enumerate the open PRs (`scripts/forge prs`) and check each against `main`
  (`scripts/forge status <pr>` — `mergeable: false` or a
  known-behind branch is the signal). When `main` has advanced, bring the branch current before it
  blocks.
- **Bring current by merging `main` in, never by rebasing.** A rebase rewrites the branch's
  commit SHAs, and the forge anchors inline review comments to those SHAs — a force-push detaches
  every existing comment. Merging keeps the SHAs stable and still satisfies the up-to-date rule
  (the branch now contains `main`'s tip), so review threads stay put.
- **Clean update** — dispatch `dev-implementer` to `git merge origin/main` into `bd/<id>` in the
  bead's worktree (committing the merge locally); `qa-verifier` re-verifies and pushes. It is a
  normal push, never a force-push. auto-merge then proceeds on its own.
- **Conflict** — same path, but the dev resolves the conflicts during the merge; QA re-verifies
  the resolved result before pushing. Never do the merge from the main loop yourself — route it
  through dev → QA.
- Do this in `main`-advances order, oldest PR first, so branches do not repeatedly fall behind
  each other.

## Handling a blocked merge

If a PR still will not merge, diagnose and route it — never merge it yourself to get past the
block, and never disable the required check:

1. Diagnose with `scripts/forge status <pr>` (`mergeable`, the `ci` status) and the merge error.
2. **Behind `main` / conflicts** — bring it current as above (dev merges `origin/main` in, QA
   re-verifies and pushes — never a force-push); the PR's `auto-merge` label then retries on its own.
3. **CI red** — this is a real failure: return the bead to `in_progress` with the failure notes
   and re-dispatch dev, exactly like a QA bounce.

## Addressing PR comments

When a human leaves comments, run the **feedback round**. For the whole round the work is back
with dev and QA, so it is no longer the human's turn: its STATUS label moves off `in-human-review`
until QA re-passes — the human's PR-review list should only ever show PRs awaiting them.

1. List the threads with `scripts/forge comments <pr>` — each line gives the `review_id`, `path`,
   and `position` needed to reply.
2. **Enter the round: swap `in-human-review` → `in-qa-review` on both the bead and the PR.** You
   own this swap; `contains-adr` and the REQUIREMENT labels stay put:

   ```bash
   bd label remove <id> in-human-review && bd label add <id> in-qa-review && bd dolt push && bd dolt pull
   scripts/forge unlabel <pr> in-human-review && scripts/forge label <pr> in-qa-review
   ```

3. Dispatch `dev-implementer` to address each actionable one, committing locally on the branch.
4. Dispatch `qa-verifier` to re-verify, push the update, and reply on each thread with
   `scripts/forge reply <pr> <review-id> <path> <position> "<body>"`, confirming it is fulfilled.
   **QA never touches the `in-qa-review` / `in-human-review` STATUS labels on a re-verification**
   — you own them, so there is no race. If QA bounces, re-dispatch dev; the labels stay at
   `in-qa-review` (still not the human's turn).
5. **Close the round only on a QA re-pass: swap `in-qa-review` → `in-human-review` back on both
   the bead and the PR**, then post one concise summary:

   ```bash
   bd label remove <id> in-qa-review && bd label add <id> in-human-review && bd dolt push && bd dolt pull
   scripts/forge unlabel <pr> in-qa-review && scripts/forge label <pr> in-human-review
   ```

Agents never resolve threads — a human resolves each once satisfied, and the PR merges only
after every thread is resolved.

Any text you post to the forge — replies, comments, summaries — is **short and not hard-wrapped.**
The forge renders every newline as a line break, so write each paragraph or bullet as one unbroken
line and separate blocks with a blank line; never wrap a sentence across lines.

## Status

After each cycle, report a skimmable line per bead: id, stage, branch/PR, and what is next or
blocking. Surface anything that needs a human decision rather than working around it.
