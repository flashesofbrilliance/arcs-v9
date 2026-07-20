# state-sync

A [Claude Code](https://claude.com/claude-code) skill that scaffolds a two-surface state sync
pattern for any repo: a single committed `_STATE/snapshot.json` that lets any session – local or
cloud, yours or a teammate's – restore ground-truth project state from a cheap file read instead
of re-deriving it every time.

## Why it exists

A session that starts cold has to reconstruct context from scratch: what's deployed, whether
local is in sync with origin, what was decided last, what's next. That reconstruction is exactly
the kind of work that's expensive to redo and easy to get subtly wrong (stale assumptions about
what's live, forgotten open threads). A single JSON file, updated at the end of a session and read
at the start of the next, turns that into a fixed, cheap first step.

This is the same idea behind "don't make the agent re-derive what a file could just tell it" –
just applied to project state instead of code.

## Install

```bash
git clone https://github.com/flashesofbrilliance/state-sync-skill.git ~/.claude/skills/state-sync
```

Or project-scoped:

```bash
git clone https://github.com/flashesofbrilliance/state-sync-skill.git .claude/skills/state-sync
```

## How to use

Run once per project:

```
/state-sync
```

It gathers your git/deploy/env facts, writes `_STATE/snapshot.json`, optionally prints the
cloud-environment config lines if you run sessions in a cloud sandbox, scaffolds a companion
pickup command, and commits.

From then on, update the snapshot at the end of a working session (pair it with your own
end-of-session habit), and start the next session with the pickup command it scaffolds.

## Use cases

- **Cloud sandboxes that start cold.** A cloud agent environment spins up with no memory of what
  happened last session. A snapshot fetched at boot gives it the last commit, deploy status, and
  open thread in one read, no investigation required.
- **Handing a repo to a teammate (or your future self).** Instead of a stale README claiming
  "deployed to X," the snapshot states what's actually true as of the last update, machine-checked
  facts instead of prose that drifts.
- **Multiple active branches or worktrees.** When more than one line of work is in flight, a
  snapshot per checkout keeps "what's the state of this one" answerable without cross-referencing
  chat history.
- **Reducing context-restore token cost.** Reading one committed JSON file is far cheaper than an
  agent running `git log`, checking a deploy dashboard, and inferring what was decided from old
  commit messages, every single session start.

## What it produces

A `_STATE/snapshot.json` with a deploy-target-agnostic schema (git state, deploy state, database
note, open decisions, a one-line summary, the next action, and a blocking flag), plus a pickup
command that reads it back – locally or via a `curl` fallback for cloud sessions.

## License

MIT. See [LICENSE](./LICENSE).
