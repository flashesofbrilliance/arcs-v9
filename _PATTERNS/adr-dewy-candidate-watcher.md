# ADR / DEWY candidate watcher — design

> _2026-08-10. Reconstructs and sharpens the parked idea ("calendar-auto-prep routine + an ADR/DEWY
> candidate watcher hook"). Problem: durable decisions get made in-session and the ADR / DEWY receipt never
> gets filed because someone has to remember. This makes the filing a **caught** signal, not a remembered
> chore._

## Governing constraint (why it queues, never auto-files)

NOTOMATION: scaffold cognition, never replace revealed preference. A governance record that the machine
mints unattended is a **fabricated** record — the same failure class as [[canon-collision-escalate-never-resolve-under-write-lock]].
So the watcher only ever **detects candidates and queues them**; a human promotes. The model writes an actual
ADR / receipt at exactly one place: the promote step, on confirmation.

Cost: heuristic detection is free (regex, no model). A model runs only on promote. Honors
[[cost-efficiency-global-goal]] + [[cost-leaks-ruin-vector]] — no always-on model watcher.

## The unlock: one candidate, two promotions

`_DECISIONS/_TEMPLATE.md` is already DEWY-native (carries D / E / W). A DEWY **receipt** is the lighter,
faster sibling: D / E / W **+ Y-gate + tributaries + priors-to-update**. So a candidate is one object that can
promote to an **ADR** (durable rule / architecture, reusable), a **DEWY receipt** (a bet under uncertainty
with priors to check later), or **both** (adaptive-rhetorical-resonance was ADR-043 **and** a receipt).

## Signal taxonomy — what is each

| | ADR candidate | DEWY candidate |
|---|---|---|
| **Is** | a decision that constrains future work: X over Y, a standard adopted, a tradeoff resolved | a judgment under uncertainty: a bet, a conviction, an ex-ante read whose outcome you'd check later |
| **Test** | "would a future contributor need to know *why we do it this way*?" | "did I make a *bet* whose outcome I'd want to measure against?" |
| **Cues** | chose … over …, going with, from now on, standardize, default to, deprecate, supersede, instead of, the tradeoff, pivot to, adopt | my read is, I'm betting, conviction, I expect, likely, ex-ante, update priors, we'll see if, hypothesis, prior, Y-gate, green/yellow/red |

Overlap is expected; a candidate can carry both flags.

## Architecture — three layers, cheapest first

**L1 — reflex (zero infra).** A behavioral rule (memory feedback / CLAUDE.md): when a durable decision lands
in-session, proactively offer to mint an ADR and/or DEWY candidate. Backstop; relies on the model noticing.

**L2 — the mechanism (candidate ledger + promote loop).** THE core, buildable with no config change:
- `scripts/adr_dewy_watch.py` — scans a blob (transcript / diff / free text), regex-classifies decision hits
  as `adr | dewy | both`, appends to an append-only ledger `_INBOX/adr-dewy-candidates.jsonl`
  (`{ts, source, excerpt, type, proposed_title, hash, status}`), deduped by excerpt hash. No model.
- promote loop: a `/adr-dewy-inbox` review step reads the ledger, shows pending candidates, and on your pick
  mints the ADR (from `_TEMPLATE.md`, next `ADR-NNN`) and/or the DEWY receipt (existing schema), then marks
  the candidate `promoted` (never deletes — audit trail). Dismissals mark `dismissed`, also kept.

**L3 — automation (the hook).** A Claude Code **PreCompact** hook (already a live hook point) runs the L2
detector over the session transcript right before context is summarized, so a session's decisions are
harvested at exactly the moment they'd otherwise be lost. **SessionStart** surfaces "N pending candidates" so
the inbox doesn't rot. Wiring this edits `.claude/settings.json` — a persistent config change, so it is the
LAST step and gated on explicit approval (per the JIT rule: build + verify local, then one deploy).

## The loop reuse (brief → prep → recoil → debrief → update-priors)

The DEWY receipt already **is** ex-ante → debrief → update-priors. The watcher automates the **debrief**
harvest (decisions caught at PreCompact). Calendar-auto-prep (the sibling parked idea) is the **front** of the
same loop — `recoil-prep` fired ahead of a counterpart call — a separate scheduled-task/hook, not this one.

## Guardrails (non-negotiable)

1. Never auto-commit a canonical ADR / receipt. Candidates only; human promotes.
2. Ledger is append-only; dismiss/promote are status flags, not deletes.
3. Detector is heuristic (free); model only on promote.
4. Dedup by excerpt hash so the same decision is not re-flagged every compaction.

## Build order

1. `scripts/adr_dewy_watch.py` + `_INBOX/` ledger + self-test. ✅ DONE (+ `--sessions N` sweep, scored `--top N`).
2. Curation pass (CURATOR meta-operator) over `--top` → `_INBOX/adr-dewy-gems.md`. ✅ DONE (8 gems from 60).
3. Hook wiring — the first activated ARCS listener. ✅ WIRED (2026-08-10) by extending the existing hook
   scripts (no `settings.json` structural change): `pre-compact.sh` runs `--sessions 1` to harvest each
   session's decisions before compaction; `session-start.sh` runs `--list` to surface the pending count at
   pickup. Both guarded (`|| true`) so the watcher can never fail the hook. Per-worktree ledger (v1).
4. `/adr-dewy-inbox` promote skill (reads ledger → mints ADR/receipt → flips status). ← next
5. Central/shared ledger across worktrees (v2 refinement). ← later
