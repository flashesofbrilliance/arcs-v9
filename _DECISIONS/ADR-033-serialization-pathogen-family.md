# ADR-033 — The Serialization Pathogen Family (tuple axiom + membership registry)

> **Status:** DECIDED — drafted by Claude at Zach's direction (2026-07-18); tuple
> axiom concurred and Y ratified by Zach 2026-07-19 (GREEN/HIGH/REVISIT, declared
> explicitly — not inferred).
> **Date:** 2026-07-18 (drafted) · 2026-07-19 (ratified)
> **Commit:** 9ce0dfc (draft + implementation) · 09bb14b (numbering correction)
>
> **Numbering note (verified 2026-07-19):** session memory records an "ADR-033
> enforcement-parity ledger (`_PATTERNS/ledger.json`, CI-gated)" as live law. Ground
> truth: that work is real but stranded on unmerged branch
> `claude/arcs-meta-cognitive-review-b7bbb0` (commit `6dca11c`, 2026-07-16, pushed
> to origin, never merged) — absent from main. It is thus a double family receipt:
> **open-loop decay** (a shipped-feeling mechanism that never landed) and
> **epistemic-sequencer** (memory serialized it as enforced law, warrant stripped).
> This ADR takes main's 033 slot and **absorbs that design** — its
> close-only-via-mechanism-or-dated-waiver rule is the Obligation-coordinate
> mitigation below.
>
> **Loop CLOSED 2026-07-19:** the stranded branch merged to main as
> `_DECISIONS/ADR-034-enforcement-parity.md` (PR #63, merge `345091f`), renumbered
> to next-free exactly per the rule above — closure by explicit event, not
> silence. The two mechanisms now coexist with distinct jurisdictions:
> **ADR-034's `_PATTERNS/ledger.json`** (CI-gated) for repo/audit findings,
> **`receipt_lookup.py --sweep`** for call-ledger obligations. The lingering
> ADR-032 duplicate remains the standing example of numbering-without-registry.

## D — The Decision

**Sharp question:** ARCS keeps discovering failures where its own append-only
ledgers serialize beliefs that later read wrong (stale, over-transferred,
unactioned, over-trusted, or semantically drifted). Do we codify each as a new spec
section per pathogen, or as one governed family with a single axiom, an admission
gate, and mechanism-first implementations?

## E — Entity / System

Every ARCS-writes-to-ARCS surface, not just recoil:
- `runtime/recoil/generated/*.json` (internal ledger) + `runtime/specs/recoil-modes-v1.md` (§chronos-sequencer, §inductive-overfit — the two members already codified)
- `scripts/receipt_lookup.py` (the Detective — first enforcing reader)
- `CLAUDE.md` handoff chain, `MEMORY.md`, `_STATE/snapshot.json`, `.claude/arcs-session-state.md` (the tracker set that produced the original three-way drift)
- `_DECISIONS/` (ADR consequences and open gates), `_CANON/` glossary (dictionary pinning)

## W — Window

**Horizon:** PERMANENT (governance law for how ARCS writes to ARCS)
**Revisit trigger:** a candidate member passes the admission gate below; or the
sweep mechanism reaches 100+ tracked obligations (ADR-023's minimum-n gate) and the
family's own hit-rate becomes measurable.

## Context

Discovered serially, 2026-07-17 → 2026-07-18:

1. **Chronos-sequencer** codified (recoil-modes v0.2.0): a belief that WAS true,
   read after it stopped being true. Receipts: chan-suh pass-1 scenario weights;
   three-way handoff-tracker drift (Handoff v3.0.0); stale snapshot.json open-items.
2. **Inductive-overfit** codified (v0.3.0): a belief validated THERE treaded as
   causal law HERE. Receipt: chanModel n=2 under near-constant conditions.
3. **Open-loop decay** assessed 2026-07-18 (this ADR implements it): a stated
   intent that still owes an action, written, never actioned, never surfaced again.
   Receipts: v1.9.0 "Critical blindspots (unactioned)" list; ADR-015 gate open
   since 2026-05-28; Resend key rotation flagged 2026-07-02, independently
   *rediscovered* 2026-07-15; riskFlags have an `action` field but no `status`.
4. **Epistemic-sequencer** and **etymology-sequencer** proposed 2026-07-18 (Zach).
   Receipts below.

The pressure that forced this ADR: the family was growing faster than its
enforcement. A pathogen catalog nobody enforces is inventory — and inventory of
open loops is itself an open loop.

## The Axiom

> A serialized belief is a tuple: **(claim, time, scope, warrant, obligations,
> dictionary)**. Every family member is one coordinate silently dropped at write
> or read time.
>
> *Amended 2026-08-29 (ratified by Zach): the tuple gains a sixth coordinate —
> **speaker** — with the admission of Ventriloquy below. Full case:
> `_PATTERNS/2026-08-29-ventriloquy-pathogen-investigation.md`.*

Write-side law: serialization carries the full tuple. Read-side law: never consume
a claim missing a coordinate — degrade trust to the fidelity the tuple actually
earns (WORLD.md's render-at-earned-fidelity, applied to the ledger itself).

## The Registry

| Member | Dropped coordinate | Failure read | In-repo receipts | Mitigation (existing/new) | Enforcement point |
|---|---|---|---|---|---|
| Chronos-sequencer | **time** | stale truth read as live | handoff v3.0.0 tracker drift; stale snapshot.json; chan pass-1 weights | `readOrder` directive + `[SUPERSEDED]` markers + always-current cover (recoil-modes v0.2.0) | Detective skips marked flags; Deeper Strata UI renders authority order |
| Inductive-overfit | **scope** | true THERE treaded as law HERE | chanModel n=2 near-constant conditions | `validityBounds` {n, conditions, stationarity} + regime ladder + tails/edges exception (v0.3.0) | Detective Read carries n + regime |
| Open-loop decay | **obligations** | owed action decays unread | v1.9.0 unactioned list; ADR-015 (open since 2026-05-28); Resend key re-discovery; enforcement-parity ledger stranded unmerged 2026-07-16→19 (closed by explicit merge → ADR-034 — the family's first documented closure) | riskFlags `status` field (OPEN/DONE/WAIVED, dated); closure is an explicit write, never silence (recoil-modes v0.4.0); repo/audit findings → ADR-034 ledger | **Detective `--sweep`** (call ledger) + ADR-034 CI gate (repo findings) |
| Epistemic-sequencer | **warrant** | hypothesis re-read as fact after qualifiers strip in transit | MEMORY.md v1.5.0 hallucination corrections ("RLS ENABLED" — false); withdrawn citation (v3.1.0); the sqrt segment rule (a flagged paraphrase treaded as operative law); phantom ADR-033 memory claim | warrant grade travels with the claim on every re-serialization; generalizes v0.3.0's "advisory stripped of its bounds" clause beyond models | Detective surfaces bounds verbatim; future: warrant field on banked claims |
| Etymology-sequencer | **dictionary** | wrong dictionary edition applied to a stratum | BAR/KKL CANON_COLLISION (v3.1.0); Y-gate enum migration (EPHEMERAL et al. survive in old strata); "code wins over doc" standing memory | glossary as single source + rename tombstones ("X → renamed Y, date") + Kairos-locked spec versioning | canon-collision escalation discipline (never resolve under write-lock) |
| Ventriloquy *(admitted 2026-08-29)* | **speaker** | one voice's words re-read as another's — dominant strain: Zach's own framing re-attributed to a warm counterpart (stored resonance reads as shared authorship; infection rate correlates with warmth). Payload is autoimmune: recoil scores its own echo, the belief-updater degrades to a mirror | Jeben/Spock fusion (corrected 2026-08-23, human recall); Yuri 5-altitude guardrail (2026-08-05); Yuri consent-stance fabrication (2026-08-09 — passed BOTH the impeccable detector and the register gauntlet); Yuri bookmark misattribution reaching the witness stub (2026-08-29, caught by Zach live); ayesha SSOT `MISATTRIBUTED_FIT` riskFlag | speaker-provenance lambda ("paternity test"): every counterpart-attributed quote/stance must match a `Them:`/named turn in the source transcript — `Me:`-match = CONTAMINATED, no match = UNSOURCED; quote-attribution additionally requires source-read-this-session (jog-vs-rewind rule) | pre-send gauntlet (forge/recoil-ship, blocking) + sixty-second-read settle beat — *detector in build (task_ce99d3fd) per epistemic-sequencer precedent*; retro-sweep hit-rate → `_PATTERNS/2026-08-29-adr-033-registry-parity-sweep.md` |

## The Admission Gate (anti-sprawl)

A candidate joins the family ONLY with all four:
1. a **distinct dropped coordinate** (not a re-description of an existing member),
2. a **distinct mitigation mechanism** (not "be careful"),
3. **≥1 in-repo receipt** (a real incident, cited),
4. a **named enforcement point** (a reader/CI/UI that actually applies it).

Fails the gate → it's a note in an existing member's section, not a new member.

## Options Considered

### Option A — Per-pathogen spec sections (status quo trajectory)
- Each new member gets its own section in `recoil-modes-v1.md`.
- Pros: worked twice; each mandate lands next to its worked example.
- Cons: recoil-modes is the wrong host (these pathogens are repo-wide — handoffs,
  ADRs, memory, snapshot); no admission gate → taxonomy sprawl; mitigations stay
  siloed per report type.

### Option B — One family registry ADR + spec pointers + mechanism-first implementations (CHOSEN)
- This ADR holds the axiom, registry, receipts, and gate. Specs keep only their
  local mandates plus a pointer. Every new member ships with its enforcement point.
- Pros: single authority (no three-trackers drift for the taxonomy itself);
  admission gate stops sprawl; the tuple axiom turns five rules into one.
- Cons: one more governance doc to keep current (mitigated: the registry is
  table-shaped and this ADR is itself subject to the family's own laws).

### Option C — Canon Book chapter
- Promote to `_CANON` prose (Book II register).
- Pros: durable, world-grade.
- Cons: canon ratification is a separate deliberate act; premature before the
  mechanisms have run. Deferred — revisit trigger above.

## Decision

**Chosen:** Option B.
**Rationale:** mechanism should lead taxonomy (cut-don't-add, make it provable).
The family's value is enforced coordinates, not named pathogens.
**Trade-offs accepted:** epistemic- and etymology-sequencer enter the registry
with *existing* partial mechanisms only (no new enforcement built for them yet) —
registered honestly as such rather than pretending coverage.

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** REVISIT — standing leash: revisit at the sweep's 100-obligation
mark (ADR-023 gate) or on any new member candidate hitting the admission gate.

Ratified by Zach 2026-07-19, concurring specifically with the coordinate mapping
(time → chronos-sequencer · scope → inductive-overfit · obligation → open-loop
decay · warrant → epistemic-sequencer · dictionary → etymology-sequencer).

**Loki test:** the strongest case against: this ADR is meta-governance about
governance docs — exactly the kind of artifact that feels like progress while
being entropy masquerading as motion (the WORLD.md enemy). If the sweep output is
never acted on, ADR-033 becomes its own best counterexample: an open loop about
open loops. The Loki answer must be empirical: the Detective sweep either changes
what sessions do next (obligations actually close) or this gets demoted to a
_PATTERNS note at the revisit trigger.

## Consequences

- `recoil-modes-v1.md` → v0.4.0: open-loop decay section (riskFlags `status`
  mandate, closure-is-an-event) + family pointer to this ADR.
- `scripts/receipt_lookup.py`: honors `status` (DONE/WAIVED excluded from live
  aggregation) + new `--sweep` mode enumerating every open obligation across the
  ledger, aged, oldest first. Legacy flags without `status` are implicitly OPEN.
- Existing reports are NOT retrofitted (append-don't-overwrite; their owners close
  their own flags with explicit status writes).
- Unblocked next: warrant field on banked claims (epistemic member's real
  enforcement); sweep coverage for handoff/ADR/snapshot open-items beyond recoil.

**Implementation pointer:** `scripts/receipt_lookup.py` (`--sweep`),
`runtime/specs/recoil-modes-v1.md` §Open-loop decay, this file.
