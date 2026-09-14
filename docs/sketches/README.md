# Harness Sketches & Cross-Agent Workspace

This directory serves as the cross-harness scratchpad and observation ledger for Claude Code, Hermes, Cursor, and human operators.

**Append-only.** Never overwrite or restructure an existing sketch file — append to it, or fork a new
dated file. This directory exists specifically so Perplexity (GitHub-connector-only, no access to
gitignored scratch) can read and write it too; a silent rewrite here is a silent loss of an idea no
other harness can recover, with no diff to show what vanished. (2026-09-13: an earlier version of this
README was rewritten in place 43 minutes after being written, dropping two undocumented concepts —
a lesson, not a rule violation, since this rule didn't exist yet.)

---

## Operational Anti-Patterns & Cost Leaks (2026-09-13 Ledger)

### 1. Token-Floor & Boot Context Bloat
- **Anti-Pattern:** Auto-loading exhaustive reference catalogs (such as the full Operators Library) inside root configuration files like `AGENTS.md` inflates the context baseline by ~1,025+ tokens per turn across every session.
- **Remedy:** Lazy-load operator specifications from `docs/operators/`. Keep `AGENTS.md` restricted to a lean 1-line index lookup table.

### 2. Worktree & Branch Sprawl
- **Anti-Pattern:** Temporary or orphaned harness worktrees (`recursing-brattain`, `determined-lovelace`) leave uncommitted disk state and inflate active branch counts, triggering false alarms regarding unmerged drift.
- **Remedy:** Enforce routine cleanup prior to starting new task blocks:
  ```bash
  git worktree prune
  python3 scripts/branch_hygiene_check.py
  ```
  Never leave merged feature branches checked out locally.

### 3. Vercel Preview Build Compute Waste
- **Anti-Pattern:** Pushing documentation updates, scratchpad files, or internal research notes triggers full Next.js App Router production/preview builds, consuming unnecessary CI/build minutes.
- **Remedy:** Tag commits touching only docs, sketches, or state ledgers with `[skip ci]`, and configure `vercel.json` with an appropriate `ignoreCommand` for non-app paths.

### 4. Cross-Harness State Retrieval
- **Anti-Pattern:** Relying on table scans or unindexed queries against local database state (e.g., `~/.hermes/state.db`) undercounts active work performed in other worktrees, leading to redundant reimplementation.
- **Remedy:** Always run full-text search (`session_search FTS`) over `_STATE/` and verify Git commit histories before assuming prior work does not exist.
