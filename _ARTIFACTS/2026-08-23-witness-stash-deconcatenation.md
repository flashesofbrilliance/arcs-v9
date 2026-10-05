# Witness: Stash as De-Concatenation

**Date:** 2026-08-23  
**Source:** Session reflection on Git stash mechanics and ontological structure  
**Status:** Captured insight

---

## The Insight

Git stash operates as an accidental **de-concatenation mechanism** — it takes a working tree with multiple dirty files and splits them into isolated, individually addressable diffs.

### What stash does

When you run `git stash push`, four things happen:

1. **File-level separation:** Each dirty file becomes its own diff in the stash bundle
2. **Freezing:** Each change-set is captured independently at a point in time
3. **Isolation:** The stash becomes a discrete git object (commit-like with two parents: HEAD + index)
4. **Clean surface:** Working tree returns to HEAD state for other work

The key effect: a concatenated working tree (multiple files dirty at once, treated as "stuff to deal with") gets split into N isolated pockets, each addressable on its own.

### Why this is de-concatenation

Before stash:
- Multiple files exist in a concatenated state — they share the property "dirty"
- The working tree treats them as one undifferentiated mass

After stash:
- Each file's changes are frozen as an independent diff
- They can be inspected separately, applied selectively, or discarded individually
- The "dirty" property no longer binds them together

This is de-concatenation by mechanics, not by understanding. Git doesn't know what's in the files — it just separates them.

---

## The Limitation

Stash splits by **file boundary**, not by **ontological category**.

### Example from this session

`_STATE/snapshot.json` is a single file containing 10+ ontological categories:

- `git.head_sha`, `head_message` (ops state)
- `vercel.*` (deploy state)
- `ui_artifacts.call_briefs[20]` (content inventory)
- `open_adrs[]` (decision register)
- `session_summary_v3341`, `session_summary_v3350_prl` (session records)
- `next_action_v3341`, `next_action_v3350_prl` (action state)
- `blocking_v3350_prl` (blocker state)
- `open_source.*` (OSS track)
- `memory_shards.*` (memory inventory)
- `nci_counter` (metrics)

When stashed, this entire JSON blob becomes **one diff** — the concatenation inside the file is preserved.

Separate files like `_SEEDS/_oracle.json`, `_INBOX/lattice-drift.jsonl`, `_INBOX/seedbank-drift.jsonl` were already de-concatenated (each is its own category), so the stash preserved that structure. The only concatenation in the stash was the snapshot itself.

### The structural implication

The limitation is not in stash — it's in the **missing file boundary**.

If every category lived in its own file:
- `session_summaries/v3341.json`
- `session_summaries/v3350_prl.json`
- `ui_inventory/call_briefs.json`
- `open_adrs/index.json`
- `oss_track/manifest.json`
- etc.

Then stash would preserve the full de-concatenation automatically. Each category becomes its own cherry-pickable diff.

**File-per-category is the de-concatenation mechanism.** Stash just faithfully serializes whatever boundaries already exist.

---

## The Power: Global Serializability

Stash provides global serializability with selective reconciliation, by virtue of being a git object.

### Properties

1. **Serialized as git commit:** The stash object is a proper git commit (tree + parents + message). It can be transferred, inspected, and applied anywhere git works.

2. **Selective application:** You can:
   - Inspect with `git stash show -p`
   - Apply individual hunks manually
   - Use `git stash branch <name>` to create a branch and cherry-pick specific diffs
   - Pop only some files with careful `git stash pop` + selective staging

3. **Reversible:** The stash persists until explicitly dropped. Changes can be recovered, re-examined, or selectively applied after the fact.

4. **Inherits existing de-concatenation:** Whatever file boundaries exist in the working tree are preserved in the stash. If you've already de-concatenated by putting categories in separate files, the stash gives you per-category diffs for free.

### Cherry-picking workflow

```
# 1. Stash the concatenated working tree
git stash push -m "pre-decision state"

# 2. Inspect what's in the stash
git stash show -p stash@{0}

# 3. Create a branch from the stash
git stash branch reconciliation-branch stash@{0}

# 4. Cherry-pick specific files/hunks
git cherry-pick -n <commit>  # apply some changes
git reset HEAD <other-file>  # leave others uncommitted

# 5. Inspect, decide, commit selectively
```

This gives you **selective reconciliation** of a previously concatenated state.

---

## The Generalization

The pattern exposed by stash is generalizable to any concatenation structure:

1. **Identify the concatenation container** — the thing holding multiple categories fused together
2. **Split into separate files by ontological category** — each category gets its own home
3. **Any file-level serialization mechanism then gives you:**
   - Per-category diffs
   - Selective cherry-picking
   - Global serializability (git objects are portable)
   - Reversible reconciliation

### What this means for the larger project

For patterns, seeds, ADRs, decisions, proverbs, artifacts, Dewey receipts, skills, memories, witness moments:

- Each category should live in its own file (or directory of files)
- Then git stash, commits, patches, bundles, or diffs all give you selective reconciliation automatically
- The "concatenation" problem becomes a "missing file boundary" problem

The snapshot's 10 categories need to become 10 files (or 10 directories). Then the snapshot becomes a **pointer/aggregator** — it references the other files — not a **container** that holds them fused together.

---

## Witness Statement

> Git stash accidentally demonstrates the right shape for de-concatenation: take a concatenated state, split it at existing file boundaries, freeze each piece independently, and make each piece selectable for later reconciliation.

> The limitation is instructive: stash can only split at file boundaries it finds, not at ontological boundaries it doesn't know. To fully de-concatenate, you must first create those file boundaries — one file per category, one home per kind of thing.

> Once file-per-category is established, global serializability with selective cherry-picking is free. Any git serialization mechanism works. The stash is just one instance of a general property.

> The snapshot's concatenation is the one unresolved case: 10 categories fused into one JSON object, waiting for file boundaries that haven't been created yet.

---

## Linked Evidence

- Session stash object: `43596a14d72e1c9247196ba17e060463085b4aa7` ("On main: local drift before scott-cut merge")
- Stash contents: 4 files, 41 insertions, 35 deletions
  - `_INBOX/lattice-drift.jsonl` (4 new drift receipts)
  - `_INBOX/seedbank-drift.jsonl` (4 new rows, 3 orphan seeds finding)
  - `_SEEDS/_oracle.json` (adr 65→66, handoff 39→41, new tao:1)
  - `_STATE/snapshot.json` (61-line diff, 10 categories still fused)
- Consolidation extraction: `_STATE/consolidation-stash-2026-08-23.md`

---

## Open Questions

1. **Where do the 10 snapshot categories actually belong?**
   - Session summaries → `_ARTIFACTS/sessions/` or `_STATE/sessions/`?
   - Call briefs inventory → dedicated SSOT file?
   - Open ADRs → `_DECISIONS/index.json` (already partially there)?
   - Memory inventory → `_MEMORY/MANIFEST.md`?
   - OSS track → `open-source/MANIFEST.json`?
   - Blockers → separate blocker ledger?

2. **What does "home" mean for each category?**
   - Where does it live when current?
   - Where does it go when archived?
   - How does it age?
   - Who reads it?

3. **Which serialization mechanism for which purpose?**
   - Stash for temporary, reversible, local
   - Commits for permanent, versioned, shared
   - Patches for portable, selective, reviewable
   - Bundles for transfer across repositories

---

*This witness captures the insight that stash is accidental de-concatenation with a structural limitation (file-level, not category-level), and that the generalization — file-per-category enabling global serializability with selective reconciliation — applies to the broader project of decontatonating patterns, seeds, ADRs, decisions, and all other categories.*
