# ADR-045 — Night Moves: End-of-Day Work Digest Routine

> **Status:** DECIDED
> **Date:** 2026-08-10
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** How does Zach keep a legible daily record of work spread across ~40
parallel worktrees, without hand-compiling it or spending unattended token budget?

---

## E — Entity / System

`.claude/skills/night-moves/SKILL.md` (synthesis) + `scripts/night_moves_gather.sh`
(deterministic gather). Writes to `_STATE/night-moves/<date>.md`. Reads git across all
worktrees (shared `.git`), `_DECISIONS/`, `_STATE/*.dewy.json`, and the user's auto-memory
directory.

---

## W — Window

**Horizon:** DURABLE — run at the end of any session where meaningful work landed.
**Revisit trigger:** if a nightly cron/schedule is added later, or if the gather script's
author filter / branch sweep needs to change (new git topology, new worktree convention).

---

## Context

Zach runs work across dozens of concurrent worktrees per day (Yuri family, Todd/PRL, the
ADR/DEWY watcher, forge pipeline hardening — all landed 2026-08-10 alone, 53 commits). No
single branch or session captures "what happened today." `/handoff` captures state for the
*next session to resume*, which is a different job — it is forward-facing and per-session,
not a daily rollup across all sessions.

The ask: a routine that produces "this is what shipped / what's next / what we learned / the
new shape of tools for JTBD / net-new tools we built" as a nightly digest.

---

## Options Considered

### Option A — Fully manual (read git log by hand each night)
- What it is: no tooling, just ask Claude to look at today's commits ad hoc.
- Pros: zero build cost.
- Cons: not repeatable, easy to skip, no fixed gather logic (different sweep each time),
  nothing durable to point future sessions at.

### Option B — Deterministic gather script + skill synthesis (chosen)
- What it is: `night_moves_gather.sh` does the mechanical sweep (git log --all, dedup,
  net-new-tool detection via diff-filter=A, ADR/DEWY/memory touch detection) with zero LLM
  cost; the `/night-moves` skill reads that output and synthesizes the five interpretive
  sections. One dated markdown file per day.
- Pros: cheap (pure git + find, no network), repeatable, matches the house pattern of
  `/handoff` (deterministic capture step + narrative synthesis step). Idempotent — re-running
  a day overwrites its file cleanly.
- Cons: gather is git-only; doesn't currently mine session transcripts for work that never
  hit a commit (explicitly deferred, see Trade-offs).

### Option C — Scheduled nightly cron agent
- What it is: an auto-firing cloud agent that runs unattended around 11pm.
- Pros: zero-touch, never forgotten.
- Cons: spends tokens on quiet days with nothing to report; less predictable cost. Deferred —
  can be layered on top of Option B later by pointing a schedule at the same skill.

---

## Decision

**Chosen:** Option B — deterministic gather script + skill-driven synthesis, manually invoked.

**Rationale:** Matches `/handoff`'s proven shape (capture-then-narrate), keeps the expensive
part (LLM synthesis) small and bounded to interpretive sections only, and gives Zach full
control over when it runs and what day it covers — important because sessions routinely run
past midnight, so "today" per the OS clock is not always the day that was worked (see
Consequences).

**Trade-offs accepted:** Git-and-memory-only gather; a "learned" moment that never produced a
commit, ADR, or memory entry won't surface. Session-transcript mining was explicitly declined
in favor of cheap and deterministic (Zach's choice when scoping this ADR).

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Strongest case against this decision — a routine invoked manually will get
skipped on busy nights, which is exactly when the digest is most valuable. Mitigated by: the
skill takes an optional date argument, so a skipped night can be back-filled the next time it
runs (proven live: this ADR's own digest was generated for 2026-08-10 from a session that
crossed into 2026-08-11).

---

## Consequences

Unblocks a running, git-tracked ledger of daily work (`_STATE/night-moves/`) that future
sessions, `/handoff`, and `/handoff-pickup` can point at instead of re-deriving "what
happened" from scratch. Surfaced a real edge case on first run: past-midnight sessions must
pass an explicit date, since the OS "today" rolls over mid-session — documented in the
skill's usage notes.

**Implementation pointer:** `.claude/skills/night-moves/SKILL.md`,
`scripts/night_moves_gather.sh`, first output at `_STATE/night-moves/2026-08-10.md`.

---

## Linked receipts / ADRs

- DEWY receipt `2026-08-10-night-moves-routine-built` — this session.
- Relates to `/handoff` (per-session forward-facing capture) and the ADR/DEWY watcher
  (`scripts/adr_dewy_watch.py`, mid-session candidate surfacing) — night-moves is the
  end-of-day ledger that sits alongside both.
