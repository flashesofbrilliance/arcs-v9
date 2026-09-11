# ADR-046 — Witness Trigger: Live Capture of a Flash of Brilliance

> **Status:** DECIDED
> **Date:** 2026-08-11
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** When a genuine insight crystallizes mid-conversation, how does ARCS attest
to it honestly, without either losing it or reconstructing it later and pretending the
reconstruction was a live witness?

---

## E — Entity / System

`.claude/commands/witness.md` (the capture command) + `WORLD.md` → THE WITNESS (the behavioral
trigger, sitting beside the Drift Sentinel). Writes to `_STATE/witness/<date>.jsonl`.

---

## W — Window

**Horizon:** DURABLE.
**Revisit trigger:** if witness stubs prove useful across a few days of real use, revisit
whether `/night-moves` should surface a WITNESSED section (count + GREEN-gated ones). Don't
build that ahead of evidence.

---

## Context

Zach asked, in conversation, whether a "flash of brilliance" moment should have a scribe —
"can I get a witness — the tree did indeed fall and this is the quality of sound it made." The
existing mechanisms (DEWY receipts, ADRs, `/night-moves`) all capture decisions and days
*after* the fact — at handoff, at session end, or when a commit lands. None of them fire at the
actual moment an insight names itself.

That gap has a direct parallel already governed by ADR-044 (temporal-provenance gate): a
capability claim that states aspiration as present fact is dishonest. A receipt written hours
later that implies it witnessed a moment it was reconstructed from is the same failure on the
attestation side — hearsay dressed as testimony.

---

## Options Considered

### Option A — Extend `/dewy-stub` to fire automatically on detected insight
- What it is: reuse the existing ADR-scaffolding command, trigger it proactively.
- Pros: no new artifact type.
- Cons: `/dewy-stub` is deliberately heavy (options-considered, Y-gate conviction, numbering
  ceremony) — wrong weight for a moment that may or may not prove durable. Firing that
  automatically would either annoy (too much ceremony per moment) or get skipped (too heavy to
  offer honestly as a quick "yes/no").

### Option B — A new lightweight capture command + proactive behavioral trigger (chosen)
- What it is: `/witness` — verbatim quote, timestamp, one-line honest gut-check, appended to a
  day-keyed JSONL log. No scoring, no options, no numbering. WORLD.md carries the trigger
  instruction: Claude offers it unprompted when it notices the signal live.
- Pros: matches the weight of the thing being captured (a flash, not yet a decision). Cheap
  enough to fire often without ceremony fatigue. Explicitly upstream of ADR/DEWY — promotion is
  a separate, later, deliberate act, so it never overclaims permanence it hasn't earned.
- Cons: a second logging surface (`_STATE/witness/`) alongside `_STATE/*.dewy.json` and
  `_STATE/night-moves/`. Accepted — the surfaces serve different timescales (moment / decision /
  day) and merging them would blur exactly the honesty distinction this ADR is about.

### Option C — Do nothing; rely on the user to say "remember this" explicitly
- What it is: status quo before this session — witness moments only get captured if Zach asks.
- Pros: zero build cost, zero false-positive risk.
- Cons: the whole point raised was that Claude should notice and offer, not wait to be asked —
  this option doesn't answer the actual question.

---

## Decision

**Chosen:** Option B.

**Rationale:** The artifact's weight has to match the thing it's capturing. A witness stub is a
bet that something *might* matter, filed cheaply and honestly at the moment it happens;
promotion to ADR/DEWY/memory is the separate, deliberate act that happens once durability is
proven. Collapsing those two into one heavy step (Option A) would make the live-capture trigger
too expensive to fire, defeating the purpose.

**Trade-offs accepted:** A new file surface to maintain (`_STATE/witness/`); risk of the trigger
firing too often if under-tuned (mitigated by the explicit "deliberately rare" instruction in
both WORLD.md and the command itself — over-firing is treated as a signal to tighten, not a
sign it's working).

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** MEDIUM
**Stability:** SHIFTING — not yet used in anger; revisit after a few days of real firings.

**Loki test:** Strongest case against this decision — this is a third parallel logging surface
(witness / DEWY / night-moves) and could fragment "where do I look for what happened" instead
of clarifying it. Mitigated by: each surface has a distinct, non-overlapping timescale (moment /
decision / day) and `/night-moves` is explicitly NOT wired to ingest witness stubs yet, so
there's no premature coupling to unwind if the pattern doesn't hold.

---

## Consequences

Unblocks honest in-the-moment capture without forcing every flash through full ADR ceremony.
Creates a small backlog risk: witness stubs that are never promoted just sit in
`_STATE/witness/*.jsonl` — acceptable, since an unpromoted stub costs nothing and the schema's
`promoted` field makes it trivial to audit later which stubs actually mattered.

**Implementation pointer:** `.claude/commands/witness.md`, `WORLD.md` → THE WITNESS, first
entry `_STATE/witness/2026-08-11.jsonl`.

---

## Linked receipts / ADRs

- DEWY receipt `2026-08-11-witness-trigger-built` — this session.
- Relates to ADR-044 (temporal-provenance gate) — same honesty principle, applied to
  attestation instead of capability claims.
- Relates to ADR-045 (`/night-moves`) — a different timescale of the same instinct (durable,
  git-tracked record of work), deliberately kept separate rather than merged.
