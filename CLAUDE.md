# CLAUDE.md

Documentation lives in [docs/](docs/README.md).

## Workflow

See [Development lifecycle](docs/guide/development-lifecycle.md). No agent merges a pull
request — merging is the auto-merge workflow or a human.

## Domain language

This project has a defined vocabulary in [Terminology](docs/guide/terminology.md) — the
project's ubiquitous language, **binding on every agent**. Use those exact terms when naming
code (variables, types, functions, modules, files) and in documentation, ADRs, commit
messages, bead titles, and PR text. Do not coin a synonym for a term that already exists, and
never use a **banned** term from that doc. If a needed concept has no term yet, add it to the
terminology doc in the same change rather than inventing an ad-hoc name.

## Subagents

Work is executed by two subagents in [`.claude/agents/`](.claude/agents), dispatched by the
main loop (the `orchestrate` skill):

- **dev-implementer** — implements one bead on a local branch and hands off. Never pushes, opens
  a PR, merges, closes, or writes bead state.
- **qa-verifier** — adversarially verifies the work against the bead's acceptance criteria; on a
  pass it pushes the branch and opens the PR, carrying the bead's labels onto it. Never merges,
  closes, or writes bead state.

The orchestrator is the only writer of bead state and never writes product code. No agent ever
merges. See [Development lifecycle](docs/guide/development-lifecycle.md).

## Beads

All work is tracked in beads (`bd`), backed by the remote Dolt ref `refs/dolt/data` — the source
of truth. Sync with `bd dolt pull` (before working, before every claim, and again after every
push) and `bd dolt push` (after every state transition) — a push does not refresh the local read
view when history has diverged, so the following pull reconciles it. Only built-in statuses are
used; labels split into **STATUS** (lifecycle: `in-qa-review`, `in-human-review`) and
**REQUIREMENT** (plan-time, fixed: the bead permission `allows-auto-merge` — absence means human
review; `requires-adr` — overrides it, never auto-merges). QA translates the bead permission into
the PR trigger `auto-merge` (mutually exclusive with `in-human-review` on the PR) and maps
`requires-adr` to the PR signal `contains-adr`. One writer per pool. See
[Beads usage](docs/guide/beads-usage.md).

## Toolchains & commands

Every command an agent runs against this project's code — build, test, lint, the CI-mirror
quality gate, running the app, the UI render check — is defined in the **stack adapter**:
[`docs/adapters/stack.md`](docs/adapters/stack.md). Do not hardcode or guess commands; read the
adapter.

Pull-request actions — open, label, comment, reply, status — go through
[`scripts/forge`](scripts/forge) (`scripts/forge help`). The forge host, repo, token location,
and host quirks are defined in the **forge adapter**:
[`docs/adapters/forge.md`](docs/adapters/forge.md). See
[Getting started](docs/guide/getting-started.md).


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:6cd5cc61 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->
