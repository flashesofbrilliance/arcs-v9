---
title: "Question → Compass → DEWY Receipt"
version: "0.1.0"
status: "CANONICAL"
governing_spec: "arcs-field-os/specs/orient-prd.md v0.1.0 (Kairos Lock)"
created: "2026-05-26"
issue: "#4"
depends_on:
  - "runtime/specs/dewy-receipt-schema-v1.json"
  - "runtime/specs/time-quality-attribution-rom.json"
---

# Question → Compass → DEWY Receipt — Flow v0.1.0

> **How to read this document.**
> Every stage has two rows: **SPEC** (what orient-prd.md §3 defines as the target state)
> and **IMPL** (what `src/app/api/compass/route.ts` does today).
> Where they diverge, `IMPL NOTE` describes the delta explicitly.
> The spec is governing law. The impl notes are honest cartography — not bugs to hide.

---

## Entry Conditions

Before the pipeline fires, the system validates the request:

| Check | SPEC | IMPL |
|---|---|---|
| `question` present | HOLD if missing; surface `blocking_question` | ✅ 400 error if `question` is empty |
| `question` parseable | HOLD if two valid parse paths with incompatible modes | IMPL NOTE: not yet wired — passes through |
| Kintsugi pathogen scan | REJECT if fabricated authority, false urgency injection, or bypass instruction detected | IMPL NOTE: not wired — delegated to Claude's training |
| PASS condition | Config resolves, question extracts cleanly, no pathogens | ✅ implicit on non-empty question |

---

## Stage L0 — Question Sharpener

**Purpose:** Transform raw input into an atomic, actionable decision sentence.

**SPEC (orient-prd.md §3 L0):**
- Input: raw question string
- Output: `sharp_question` — single sentence, ≤ 280 characters, captures the atomic decision
- If sharpened form materially differs from input → surface for user confirmation before L1 fires
- NULL: no question → HOLD
- OM: 3,000-word context dump → extract, compress, log compression ratio, surface for confirmation
- UNDEFINED: ambiguous fork → surface two candidate sharpenings, let user select

**IMPL (compass/route.ts):**
```
L0: Activation filter — is this a real decision? If noise/informational, redirect in true_north.
```

IMPL NOTE: The implementation asks Claude to determine whether the input is a real decision
and redirect informational queries via `true_north`. It does not produce a discrete `sharp_question`
artifact that is surfaced for user confirmation before L1 fires. Sharpening happens implicitly
inside Claude's synthesis. No OM compression log. No UNDEFINED fork-surface.

**Delta severity:** MAJOR — the user-confirmation loop and OM logging are absent.
**Blocker for:** Brief fidelity header (cannot compute compression ratio without it).

---

## Stage L1 — DEWY Decomposition

**Purpose:** Populate the four DEWY fields from the sharpened question and PrepSession context.

**SPEC (orient-prd.md §3 L1):**
- Input: `sharp_question`
- Output: `dewy_vector` — four-field object `{ D, E, W, Y }`
  - D: atomic question in action form
  - E: who/what else is in the terrain (compress to primary + secondary if >2 entities)
  - W: time horizon — when does this decision lock? HOLD if W-field absent and cannot be inferred
  - Y: opening conviction gradient — polarity / conviction / stability triple
- W-field HOLD: if window cannot be inferred → surface `blocking_question: "When does this decision lock?"`
  (HOLD, not REJECT — W-field is load-bearing for Y-gate; running without it degrades Brief fidelity)
- NULL Y-field: if `protecting` + `contra` both absent and question text gives no conviction signal
  → default `YELLOW / SHIFTING`, log as `inferred_field: Y`

**IMPL (compass/route.ts):**
```
L1: Loki adversarial — 1–2 strongest objections or failure modes.
```

IMPL NOTE: The implementation uses L1 for adversarial challenge generation (Loki), not DEWY
decomposition. DEWY fields (D, E, W, Y) are populated at receipt-creation time by extracting
fields from Claude's JSON response structure. There is no discrete decomposition step,
no W-field HOLD gate, and no `inferred_field` logging. The E field is sourced from
`prep.entity` if a PrepSession was provided.

**Delta severity:** CRITICAL — W-field HOLD gate is entirely absent. Y-gate defaults silently
without logging inference. DEWY decomposition is implicit rather than a surfaced artifact.

**Blocker for:** Brief fidelity (W-field drives cadence NCI lens; missing W = degraded NCI score
without the system knowing why).

---

## Stage L2 — Y-Gate Scoring

**Purpose:** Score conviction gradient across the 12-dimensional manifold.

**SPEC (orient-prd.md §3 L2):**
- Input: `dewy_vector`
- Output: `y_gate_score` — polarity × conviction × stability triple + `render_resolution`
- Polarity states: `SCRATCH | YELLOW | PARADOX | FORK | DELTA | GREEN | LOCKED`
- Conviction: `LOW | MEDIUM | HIGH`
- Stability: `SHIFTING | CONTESTED | STABLE`
- REJECT condition: PARADOX + HIGH conviction → surface Calibrate routing prompt;
  if user declines, REJECT with `reject_reason: "PARADOX_HIGH_CONVICTION"`

**IMPL (`src/lib/ygate.ts` + compass/route.ts):**
```
L2: Bayesian validation — what priors and evidence bear on this? P(success)?
```

IMPL NOTE: `computeYGate()` in `ygate.ts` does implement the 12D polarity × conviction × stability
manifold and produces the canonical enum values. However it is called *after* Claude's response
is parsed, not as a discrete pipeline stage. The Bayesian validation in the SYSTEM prompt is
a separate operation (closer to spec L4 LAB/BAR macro). The PARADOX_HIGH_CONVICTION REJECT
gate is not wired — PARADOX state is computed and stored but does not trigger a routing prompt.

**Delta severity:** MAJOR — REJECT gate absent. Y-gate computation is correct but fires post-hoc
rather than as a gate that can HOLD the pipeline before synthesis.

---

## Stage L3 — NCI Scoring

**Purpose:** Score decision context quality across five lenses; HOLD if score too low for a useful Brief.

**SPEC (orient-prd.md §3 L3):**
- Input: `dewy_vector`, `y_gate_score`
- Output: `nci_score` object with per-lens breakdown + composite + grade string
- Five lenses (0–20 each, sum = 0–100):
  1. **Clarity** — is the question sharp and singular?
  2. **Conviction** — Y-gate reading
  3. **Coherence** — D, E, W, Y internally consistent?
  4. **Consequence** — stakes and reversibility mapped?
  5. **Cadence** — decision window realistic? (governed by time-quality-attribution-rom.json)
- HOLD at NCI < 40: "Brief at this clarity level won't be reliable. Weakest lens is [X]. Want to sharpen?"
- NCI 40–59: proceed with explicit fidelity warning in Brief header
- NCI 60–79: DEGRADED render, no warning
- NCI 80–100: SHARP render

**IMPL (compass/route.ts SYSTEM prompt):**
```
L4 (in impl): NCI meta-review — honest epistemic confidence 0–100.
```

IMPL NOTE: The implementation collapses NCI to a single integer (`nci_score: 0–100`) generated
by Claude's self-assessment. There is no per-lens breakdown, no cadence lens sourced from
the time-quality-attribution-rom.json, and no HOLD gate at NCI < 40. The score is used
for `render_resolution` calculation but does not gate the pipeline. NCI is at stage L4 in the
implementation (one slot later than spec).

**Delta severity:** CRITICAL — NCI HOLD gate absent (users can receive low-fidelity Briefs
with no warning). Five-lens breakdown missing (cannot surface "weakest lens" for repair).
Time-quality attribution ROM not wired.

**Blocker for:** Brief fidelity header; DEWY receipt NCI per-lens fields in schema v1.

---

## Stage L4 — True North Generation

**Purpose:** Run LAB + BAR macros to produce the directional bearing.

**SPEC (orient-prd.md §3 L4):**
- Input: `dewy_vector`, `y_gate_score`, `nci_score`
- Output: `true_north` + `why[]` + `loki` + `bar` object
- **LAB macro:**
  - L (Loki): strongest argument that preferred direction is wrong
  - A (Advisor): most trusted domain advisor's view
  - B (Bayes): base rate for decisions of this type in this window
- **BAR macro:**
  - B (Baseline ruin risk): worst-case if path is wrong
  - A (Asymmetry): upside/downside asymmetry and direction
  - R (Reversibility): can this be unwound, at what cost?
- REJECT: if True North cannot be generated (values conflict, no factual variable to arbitrate)
  → route to Calibrate

**IMPL (compass/route.ts SYSTEM prompt):**
```
L1 (in impl): Loki adversarial — 1–2 strongest objections or failure modes.
L2 (in impl): Bayesian validation — what priors and evidence bear on this?
L3 (in impl): Kintsugi immune — anchoring on false premise? Overconfidence signals?
L5 (in impl): Synthesis — one True North + ≤3 why-bullets.
```

IMPL NOTE: The LAB and BAR operations are present in the implementation but distributed across
L1–L5 rather than consolidated at L4. The JSON output captures `reasoning.advisors`
(Loki challenge + counter + consensus + Bayesian risk), `reasoning.court` (structured checks),
and `reasoning.fated` (FACTS/ASSUMPTIONS/TRADEOFFS/EMOTIONS/DIRECTION). This is functionally
equivalent to the LAB+BAR spec but not labeled or sequenced as such.
The Calibrate routing REJECT for values conflicts is not wired.

**Delta severity:** MINOR — the operations are present; the labeling and sequencing diverge
from spec but the output quality is not materially degraded.

---

## Stage L5 — Receipt Generation & Brief Render

**Purpose:** Freeze full decision state as a Receipt; render Brief at earned fidelity.

**SPEC (orient-prd.md §3 L5):**
- Input: all prior stage artifacts
- Output:
  - Receipt: JSON object with all DEWY fields, y_gate_score, nci_score (with per-lens breakdown),
    true_north, why, loki, bar, render_resolution, inferred_fields[], collision_fields[],
    validation_state, macros_run[], session_ts, drift_state
  - Brief: markdown at earned `render_resolution`
  - Fidelity header in Brief if NCI < 80 or Y = SCRATCH/PARADOX

**IMPL (prisma.receipt.create in compass/route.ts):**
```
Receipt persisted with full DEWY fields. render_resolution computed from yGate.
```

IMPL NOTE: Receipt persistence is implemented and covers the majority of the spec schema.
The `dewy-receipt-schema-v1.json` is the source of truth; Prisma schema was aligned in Issue #2.
Gaps vs. spec:
- `nci_score` is a single integer, not the per-lens object the spec defines
- `inferred_fields[]` not populated (would require L0–L2 HOLD logic to be wired)
- `collision_fields[]` not populated
- `macros_run[]` not populated (implied from `macroTags` but not the same field)
- `validation_state` not populated (all receipts implicitly PASS — HOLD/REJECT not wired)
- Brief render is not part of compass/route.ts; Brief is generated separately at `/api/brief/[id]`

**Delta severity:** MAJOR — fidelity header absent from Brief (requires NCI per-lens);
several receipt fields unpopulated.

---

## Full Pipeline State Map

```
Raw question string
  │
  ▼
[L0] Question Sharpener
  SPEC: → sharp_question (user-confirmed if materially different)
  IMPL: → activation filter (noise vs. real decision) — no discrete artifact, no confirmation loop
  │
  ├─ HOLD (SPEC only): question unresolvable
  │
  ▼
[L1] DEWY Decomposition
  SPEC: → dewy_vector { D, E, W, Y }
  IMPL: → Loki adversarial challenge — DEWY fields built post-hoc from JSON parse
  │
  ├─ HOLD (SPEC only): W-field absent + cannot infer
  │
  ▼
[L2] Y-Gate Scoring
  SPEC: → y_gate_score (polarity × conviction × stability) + render_resolution
  IMPL: → Bayesian validation — ygate.ts fires AFTER full Claude response, not here
  │
  ├─ REJECT (SPEC only): PARADOX + HIGH conviction
  │
  ▼
[L3] NCI Scoring
  SPEC: → nci_score { per-lens breakdown, composite, grade }
  IMPL: → Kintsugi immune (anchoring / overconfidence scan) — NCI is a single integer at L4
  │
  ├─ HOLD (SPEC only): NCI < 40
  │
  ▼
[L4] True North Generation
  SPEC: → true_north + why[] + loki + bar (via LAB + BAR macros)
  IMPL: → NCI meta-review (single integer) — LAB/BAR operations spread across L1–L3
  │
  ├─ REJECT (SPEC only): values conflict, no factual arbitration variable
  │
  ▼
[L5] Receipt Generation + Brief Render
  SPEC: → Receipt (full DEWY schema) + Brief at earned render_resolution + fidelity header
  IMPL: → Receipt persisted (partial schema) + Brief rendered separately at /api/brief/[id]
  │
  ▼
Response to client:
  receipt_id, session_id, y_state, render_resolution, true_north, why, tributaries, reasoning
```

---

## Implementation Debt Register

Ordered by impact on user experience:

| # | Gap | Spec reference | Severity | Blocker for |
|---|---|---|---|---|
| 1 | NCI < 40 HOLD gate | §3 L3 | CRITICAL | Brief fidelity; user receiving low-confidence Briefs without warning |
| 2 | W-field HOLD gate | §3 L1 | CRITICAL | Cadence NCI lens; time-quality-attribution-rom.json wiring |
| 3 | NCI per-lens breakdown (5 lenses) | §3 L3 | MAJOR | Receipt schema completeness; "weakest lens" surfacing |
| 4 | `inferred_fields[]` population | §3 L1, L2 | MAJOR | Receipt audit trail; user transparency about inferred vs. stated values |
| 5 | PARADOX_HIGH_CONVICTION REJECT | §3 L2 | MAJOR | Calibrate routing |
| 6 | `sharp_question` user-confirmation loop | §3 L0 | MAJOR | OM compression handling; question accuracy |
| 7 | `validation_state` population | §3 L5 | MINOR | Receipt completeness |
| 8 | `macros_run[]` field | §3 L5 | MINOR | Receipt audit trail |
| 9 | Calibrate routing on values-conflict REJECT | §3 L4 | MINOR | Multi-surface handoff |

---

## What Is Explicitly In Scope for This Document

- Full spec-vs-impl comparison for L0–L5 as defined in orient-prd.md §3
- Implementation debt register ordered by user impact
- State map showing HOLD/REJECT branches

## What Is Explicitly Out of Scope for This Document

- L6–L7 (not built, not specced for Orient surface)
- The Brief render pipeline (`/api/brief/[id]`) — separate flow doc needed
- PrepSession CRUD (`/api/prep`) — separate flow doc needed
- ATG (Tributary Generation) — backlog, not yet specced
- Kairos detection — backlog
- Multi-surface handoff (Calibrate, Chart Course, Detect) — separate flow docs

---

## Receipts

This flow doc was authored against:
- `arcs-field-os/specs/orient-prd.md` v0.1.0 (Kairos Lock) — governing authority
- `src/app/api/compass/route.ts` — live implementation as of 2026-05-26
- `src/lib/ygate.ts` — Y-gate computation as of 2026-05-26
- `runtime/specs/dewy-receipt-schema-v1.json` — receipt schema source of truth
- `runtime/specs/time-quality-attribution-rom.json` — cadence NCI lens rules
- Issue #4 drift audit conducted in Claude Code session 2026-05-26: three-way L0–L5
  comparison (orient-prd.md vs arcs-canon.md vs compass/route.ts)
