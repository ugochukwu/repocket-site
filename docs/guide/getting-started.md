---
title: Getting started
summary: "TEMPLATE: prepare a fresh clone — repository access, beads tooling, the forge token, and project-specific harnesses."
updated: 2026-08-05
status: draft
---

# Getting started

Prepare a fresh clone before working on this project. Complete the sections for the tooling
you need. The **setup** skill walks these checks automatically.

## Repository access

- SSH access to <!-- TODO: your forge host -->`<forge host>`.
- Clone the repository.

## Ticketing (beads)

beads (`bd`) tracks all work; `bv` is its TUI viewer.

Install:

```bash
brew install beads
brew install dicklesworthstone/tap/bv
```

Fetch bead state:

```bash
bd dolt pull
```

View tasks by running `bv` from the repository root; update it with `bv --update`.

## Forge token (pull requests)

Agents open, label, and comment on pull requests through the forge API, which requires a
personal access token.

1. Create a token at <!-- TODO: host -->`<forge host>` → Settings → Applications, with
   `repository` and `issue` set to Read and Write, scoped to this repository.
2. Copy [`.secrets/forge.env.example`](../../.secrets/forge.env.example) to the gitignored
   project file `.secrets/forge.env` and fill in `FORGE_API`, `FORGE_REPO`, and `FORGE_TOKEN`.

Agents read the configuration from that file. Never commit it. All pull-request actions go
through [`scripts/forge`](../../scripts/forge), which reads the token for you — run
`scripts/forge help` for the interface. Host specifics: [forge adapter](../adapters/forge.md).

## Build, test, run

All commands live in the [stack adapter](../adapters/stack.md) — the build/test/lint set, the
CI-mirror quality gate, how to run the app, and the UI render check if this project has one.

<!-- TODO: add install steps for the stack's tooling here (toolchain, package manager,
     test runner) so the setup skill can point users at them. -->

## Project-specific harnesses

<!-- TODO: document any additional verification harnesses this project uses (an evaluation
     harness with held-out data, a device farm, a performance rig), including any standing
     rules about who may read what. Delete this section if there are none. -->

## Generated artifacts

Some checked-in files are generated from a single source and must be regenerated when that
source changes. Each generator has a `--check` mode that CI runs to keep the checked-in copy
current.

- **Docs index** — the generated list in [`docs/README.md`](../README.md) is built from each
  doc's frontmatter. Regenerate with `scripts/gen-doc-index` after adding or renaming a doc.

<!-- TODO: list your project's other generated artifacts here (API contracts, bindings,
     schemas), each with its generate and --check commands. -->
