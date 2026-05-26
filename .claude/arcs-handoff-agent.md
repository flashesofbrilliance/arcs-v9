# ARCS Handoff Agent

> **What this is:** A repeatable 5-step protocol for closing a Perplexity session and
> generating a clean Claude Code pickup point. Run this at the end of any working session
> where artifacts were created, pushed, or modified.
>
> **When to run:** Any time you're switching from Perplexity (spec/design/decision work)
> to Claude Code (implementation/execution work), or ending a session mid-sprint.
>
> **Time to complete:** ~5 minutes when run cleanly.

---

## Step 1 — Audit repo state

Verify what actually landed. Do not rely on memory.

```
Check arcs-v9 recent commits:
  → list last 10 commits on main
  → confirm each artifact mentioned in the session has a corresponding SHA
  → flag any "I pushed this" claims that lack a confirmed SHA

Check arcs-field-os recent commits:
  → same process
  → note any cross-repo dependencies introduced this session
```

**Output:** A confirmed commit table with SHA, date, file, and what it does.
Any unconfirmed push is flagged as a gap.

---

## Step 2 — Identify gaps

Compare what was planned this session against what actually landed.

```
For each planned artifact:
  IF committed with SHA → ✅ LANDED
  IF discussed but not pushed → 🔴 GAP
  IF partially complete → 🟡 PARTIAL (note what remains)

Also check:
  → Open sprint issues — are any now closeable?
  → Any new gaps created by what Claude Code pushed post-handoff?
  → Any cross-repo dependency changes that affect the other repo's queue?
```

**Output:** Gap table with status per file target.

---

## Step 3 — Update MEMORY.md

Prepend a new versioned entry at the top of `arcs-v9/MEMORY.md`.

```
Version bump: v(N-1) → vN.0 for major session, v(N).(M-1) → vN.M for minor update

Required sections in new entry:
  ### Session context       (operator, environment, goal)
  ### Artifacts pushed      (tables for arcs-v9 and arcs-field-os)
  ### Post-handoff commits  (any Claude Code commits that landed after last push)
  ### Cross-repo state      (dependency rules, Kairos Lock status)
  ### Open gaps             (updated ✅/🔴/🟡 status per file)
  ### Next move             (numbered orientation chain for next session)

Rule: never delete prior versions. New entry at top only.
```

**Verify:** Push confirmed with SHA before proceeding.

---

## Step 4 — Update SKILL.md if needed

Only required if this session introduced a new skill domain, changed the priority
queue, or added a new ROM primitive.

```
Check if any of these changed:
  → Priority queue (issue scope, status, or dependency chain)
  → Skill domains (new domain, new rules, new authority reference)
  → ROM primitives (new primitive added or renamed)
  → Versioning policy (new file type added)

If yes: update in place, increment version, append changelog row.
If no: skip.
```

---

## Step 5 — Generate Claude Code one-shot prompt

Produce the pickup prompt using this exact template structure:

```
REPOS:
  Primary:   https://github.com/flashesofbrilliance/arcs-v9
  Cross-ref: https://github.com/flashesofbrilliance/arcs-field-os

Before doing anything, orient using this read order:
  1. @MEMORY.md → latest vX.Y entry
  2. @CLAUDE.md → latest Handoff section
  3. @SKILL.md → current version
  4. arcs-field-os/specs/orient-prd.md → if touching Issues #2-4
  5. @WORLD.md → before writing any logic, schema, or route

STATE OF THE REPO ([date] [time]):
  [confirmed landed table — arcs-v9]
  [confirmed landed table — arcs-field-os]
  [not yet created table with 🔴 status]

DEPENDENCY CHAIN:
  [issue graph]

[ACTIVE ISSUE — EXACT SCOPE]
  [two or three concrete tasks, no ambiguity]

CROSS-REPO RULES:
  [dependency rules]
  [gitignore rules]
  [no new deps rule]

VALIDATION LAYER:
  [PASS/HOLD/REJECT reminder + authority reference]

VERSIONING POLICY:
  [three-line policy]

START HERE → [Issue #N, Task 1]:
  [file target]
  [authority reference]
```

**Quality check before sending:**
- [ ] Both repo URLs present
- [ ] `@` prefix on MEMORY, CLAUDE, SKILL, WORLD
- [ ] All SHAs confirmed (no unverified claims)
- [ ] Active issue scope is unambiguous ("do X" not "work on Y")
- [ ] No stale file targets (check against Step 2 gap table)
- [ ] Versioning policy included
- [ ] START HERE is a single concrete file, not a category

---

## Receipt template

Log this at the end of every handoff run:

```
Handoff Receipt
  Date:              YYYY-MM-DD HH:MM
  Session operator:  [name]
  MEMORY version:    vX.Y.Z
  SKILL version:     vX.Y.Z
  CLAUDE.md handoff: vX.Y.Z
  Gaps closed:       [N]
  Gaps remaining:    [N]
  New gaps opened:   [N]
  Claude Code start: Issue #N, Task N
  Prompt generated:  yes / no
  Push confirmed:    yes / no
```

---

## Anti-patterns (never do these)

- **Saying "pushed" without a confirmed SHA.** If the tool call didn't fire, it didn't land.
- **Updating MEMORY without checking post-handoff Claude Code commits.** The repo may have moved since your last push.
- **Generating the one-shot prompt before MEMORY is current.** The prompt references MEMORY — if MEMORY is stale, the prompt is stale.
- **Skipping the gap table.** Claude Code will start from whatever the prompt says. If the prompt is optimistic about what landed, it will build on a false foundation.
- **Updating CLAUDE.md handoff section without appending.** Never overwrite. Always append a new versioned section.
