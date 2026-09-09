# agent kit

A drop-in agentic-workflow kit: the instruction, skill, and agent-configuration files
that drive a supervised dev → QA → PR loop under Claude Code. Generalized from the
**basset** project's working setup.

Paths are preserved relative to the repo root, so the kit can be copied into a repo
as-is and then adapted.

## Architecture: core + adapters

The **core** (everything not listed as an adapter) is project-agnostic and should not
need editing: the three-role split, the label taxonomy, worktree isolation, the review
gate, docs conventions, and the beads ticket discipline (beads is a fixed choice of
this kit, not an adapter).

Two **adapter surfaces** hold everything project-specific. Fill these in per project;
core files reference them by section name and never hardcode their contents:

- **`docs/adapters/stack.md`** — every command an agent runs against the code: build,
  test, lint, the CI-mirror quality gate, how to run the app, the UI render check.
- **`docs/adapters/forge.md`** — the code-forge host, repo, token location, and host
  quirks. The executable half of this adapter is `scripts/forge` (Forgejo/Gitea
  implementation included; a GitHub adapter would reimplement the same verbs with `gh`).

Plus one **content template**: `docs/guide/terminology.md` — replace its contents with
your project's binding domain language (the mechanism is core; the words are yours).

## Entry points (loaded automatically)

- **CLAUDE.md** — project instructions Claude Code loads every session.
- **AGENTS.md** — tiny pointer file.

## Subagents (`.claude/agents/`)

- **dev-implementer.md** — implements one bead on a local branch and hands off. Never
  pushes, opens a PR, merges, closes, or writes bead state.
- **qa-verifier.md** — adversarially verifies against the bead's acceptance criteria;
  on a pass pushes the branch and opens the PR. Never merges, closes, or writes bead
  state.

## Skills (`.claude/skills/*/SKILL.md`)

- **orchestrate** — the main dev → QA → PR loop; owns bead state and git sync.
- **rp_planning** — turn a feature/goal into well-formed beads.
- **review** — read-only in-depth codebase review → dated document under reviews/.
- **docs-gardening** — cleanup sweep of docs/ for staleness/contradiction.
- **setup** — one-time, re-runnable: verify environment, check the adapters are filled
  in, seed load-bearing rules into machine memory.

## Guides (`docs/guide/`)

- **development-lifecycle.md** — the dev → QA → merge lifecycle and who may do what.
  The process spec; core.
- **beads-usage.md** — how work is tracked in beads (`bd`) / Dolt. Core.
- **conventions.md** — how docs are written and maintained. Core.
- **coding-principles.md** — stack-independent design principles. Core.
- **terminology.md** — TEMPLATE: your project's binding domain language.
- **getting-started.md** — TEMPLATE: environment setup for a fresh clone.

## Tooling

- **scripts/forge** — Forgejo/Gitea API wrapper all PR actions go through. Reads its
  token from `.secrets/forge.env` (see `.secrets/forge.env.example`); host and repo
  are configured there too.
- **scripts/gen-doc-index** — regenerates the generated section of `docs/README.md`
  from each doc's frontmatter; `--check` mode for CI.
- **.forgejo/workflows/ci.yml** — CI skeleton; fill its quality-gate job from
  `docs/adapters/stack.md`.
- **.forgejo/workflows/auto-merge.yml** — the label-triggered auto-merge workflow with
  the deny-list integrity backstop.

## Drop-in checklist

1. Copy the kit into the repo root.
2. Run the **setup** skill — it walks the adapter fill-in and verifies the environment.
3. Replace `docs/guide/terminology.md` content with your domain language.
4. Fill `docs/adapters/stack.md` and `docs/adapters/forge.md` (+ `.secrets/forge.env`).
5. Flesh out `.forgejo/workflows/ci.yml` from the stack adapter's quality gate.
6. `scripts/forge seed-labels` to create the workflow labels on the repo.
7. Set branch protection: no direct pushes to main, required CI check, and
   block-on-outdated-branch.
8. Run `scripts/gen-doc-index` and commit.
