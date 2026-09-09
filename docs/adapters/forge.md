---
title: Forge adapter
summary: GitHub via the gh CLI — configuration, the forge verb interface, and GitHub-specific conduct rules for the Repocket site repo.
updated: 2026-09-09
status: living
---

# Forge adapter — GitHub via `gh`

All PR actions go through [`scripts/forge`](../../scripts/forge) (run `scripts/forge help`).
Core kit files invoke those verbs and never call the GitHub API directly. This is the GitHub
implementation of the agent kit's forge interface, backed by the `gh` CLI — the same
implementation used by the Fotospots and Mugo Works projects, unmodified.

## Configuration

- Repo: `ugochukwu/repocket-site` (public), inferred from the git remote
  (`FORGE_REPO=<owner>/<repo>` overrides).
- Reviewer: `ugochukwu` (Michel), requested on every PR `pr-create` opens regardless of the
  auto-merge/human-review path (`FORGE_REVIEWER=<login>` overrides).
- Auth: `gh auth login` on this machine (no token file) for **read verbs** (`prs`, `comments`,
  `status`). `gh auth status` must succeed.
- **Public repo — GitHub's native auto-merge IS available on the free plan**, so
  `allows-auto-merge` beads actually merge unattended once required checks pass. Same posture as
  the Fotospots landing repo (`ugochukwu/photospots-landing-page`), unlike the sibling private
  repos (Fotospots app, Mugo Works) where auto-merge is not available and every bead takes the
  human-review path.

### Bot identity for write verbs

Every **write** verb (`reply`, `comment`, `pr-create`, `pr-edit`, `label`, `unlabel`,
`automerge`, `seed-labels`) invokes `gh` with `GH_TOKEN` set to a distinct bot PAT, sourced from
macOS Keychain (service `mugo-bot`, account `$USER`) inside a `get_bot_token()` helper — the
same `mugo-bot` collaborator identity already used on Fotospots and Mugo Works and the Fotospots
landing repo, reused here rather than minted fresh. Design intent: agent-authored writes appear
as `mugo-bot` in GitHub's UI, never as the machine's default `gh` identity (Michel's personal
PAT), so a reviewer can tell an agent's comment/PR/label from a human's at a glance. **Read**
verbs (`prs`, `comments`, `status`) keep the default `gh auth` session. This touches only the
GitHub API identity; git commit authorship (`user.name`/`user.email`) is unrelated and
untouched.

**Setup requirement:** `mugo-bot` must be a collaborator with write access on this repo. The
Keychain entry itself is already established on Michel's machine from the sibling projects; a
missing entry surfaces a hard error with the exact `security add-generic-password` fix command.

## Verbs

`pr-create` · `pr-edit` · `prs` · `status` · `comments` · `reply` · `comment` · `label` ·
`unlabel` · `automerge` · `seed-labels` (· `upload` — unsupported, see quirks)

Differences from the Forgejo original, on purpose:

- **`reply <pr> <comment-id> <body>`** — GitHub threads replies by review-comment id, not by
  review-id/path/position. `forge comments` emits the `comment_id` to use.
- **`automerge <pr>`** — replaces the Forgejo label-triggered workflow: it enables GitHub's
  native auto-merge (squash), and GitHub performs the merge once required checks pass. The
  `auto-merge` label is applied alongside purely as a visible marker.
- **No deny-list backstop yet** — GitHub's native auto-merge has no equivalent hook. Treat
  `.github/**`, `.claude/**`, `CLAUDE.md`, `AGENTS.md`, and `docs/adapters/**` as never-auto-merge
  by policy: QA routes beads touching them to human review regardless of labels.
- **`pr-create <head> <base> <title> <body>` gates on `pr-body-embeds-comparison-shots`**: it
  derives the bead id from `head` (`bd/repocket-site-<id>` or `bd/dev/repocket-site-<id>`, read
  from `bd config get issue_prefix` rather than hardcoded) and checks `git ls-files` for that
  bead's `docs/qa-screenshots/<bead-id>/` on the current tree. If any image file is there, the
  resolved body must embed at least one inline (`![alt](url.png)` or `<img src="...">`) — a
  plain path reference does not count.
- **`pr-create` always requests a reviewer**: every PR is opened with `--reviewer "$FORGE_REVIEWER"`
  (default `ugochukwu`), so a human review is on record regardless of the merge path.

## Host quirks (GitHub)

- **Rendering**: newlines in PR/issue bodies render as line breaks. Never hard-wrap bodies —
  one unbroken line per paragraph or bullet, blank line between blocks.
- **Bodies with backticks or `$(...)`** go through `@<file>` or stdin `-`, never inline.
- **Review comments anchor to commit SHAs**: bring branches current by **merging** `master` in,
  never rebase + force-push — a force-push detaches review threads.
- **No image upload API for PR bodies**: screenshots are committed on the bead branch under
  `docs/qa-screenshots/<bead-id>/` and linked by path; reviewers open them in the Files tab.
- **Squash merges**: GitHub's squash leaves the branch "unmerged" in git's eyes — delete bead
  branches with `git branch -D` after the merge is confirmed.
- Authorship marking is the `mugo-bot` identity itself; comment bodies carry no prefix.
- **GitHub Pages, not Netlify**: this repo deploys via GitHub Pages, branch `master`, path `/`.
  There is no deploy-preview-per-PR; the render check runs against a local server instead (see
  the stack adapter).
