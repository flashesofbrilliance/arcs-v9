---
version: "0.1.0"
status: REVIEW
depends-on:
  - runtime/specs/dewy-receipt-schema-v1.json
  - WORLD.md
blocks:
  - runtime/specs/time-quality-attribution-rom.json
  - runtime/flows/question-compass-to-dewy.md
  - prisma/schema.prisma (Receipt model)
governing-authority: arcs-field-os/specs/orient-prd.md v0.1.0
---

# DEWY Receipt Schema v0.1.0 — Human-Readable Companion

> Machine-readable authority: `runtime/specs/dewy-receipt-schema-v1.json`  
> This document is the canonical prose companion. When the two conflict, the JSON schema wins.

---

## What

A **Receipt** is a state vector frozen at the moment the ARCS Orient surface completes an L0–L5 evaluation pass. It is not a document — it is a coordinate on the decision manifold, with full DEWY decomposition, Y-gate scoring, NCI scoring, and render metadata attached.

Every compass run that reaches PASS validation produces exactly one Receipt. HOLD and REJECT runs produce a stub receipt (validation_state only — no full decomposition).

The DEWY acronym encodes the four axes of the state vector:

| Axis | Meaning | Populated by |
|------|---------|-------------|
| **D** | Decision — the atomic sharpened question | L0 Question Sharpener |
| **E** | Entity — who else is in the terrain | L1 Decomposition |
| **W** | Window — time horizon, lock date | L1 Decomposition |
| **Y** | Yellow Gate — conviction gradient | L2 Y-Gate |

---

## Why

Receipts are the world's memory. Without them, every compass run is stateless — the fog never retreats, the terrain never accumulates cartography, and the Observatory has nothing to replay.

A Receipt serves three functions simultaneously:

1. **Persistence** — freezes the decision state at a specific moment so it can be reviewed, replayed, and compared to outcomes.
2. **Rendering input** — the `render_resolution` field drives the Brief's silkscreen fidelity (SHARP at the clarity ridge, GRAIN in dense fog).
3. **Pattern substrate** — receipts accumulate into the Observatory's trajectory layer, enabling conviction gradient analysis across sessions.

---

## Governance rules

1. **One schema per surface.** This schema governs the Orient surface only. Other surfaces (CALIBRATE, CHART_COURSE, DETECT) will define their own receipt schemas.
2. **No breaking changes without a new file.** Any change that removes a required field, changes an enum value, or restructures `dewy_vector` requires `dewy-receipt-schema-v2.json` + a new companion `v2.md`. The v1 files are write-locked once status reaches ROM.
3. **PASS only.** Only receipts with `validation_state = PASS` receive full DEWY decomposition. HOLD and REJECT stubs carry only: `receipt_id`, `surface`, `version`, `validation_state`, `hold_reason`/`reject_reason`, `blocking_question`, `session_ts`.
4. **JSON arrays as TEXT.** All array fields (`why`, `inferred_fields`, `collision_fields`, `macros_run`) are stored as `TEXT` in SQLite (Prisma). Always `JSON.stringify()` before write, `JSON.parse()` after read.
5. **Enums as plain strings.** No Prisma `enum` type until datasource is Postgres. Store as `String` with application-layer validation.
6. **Render resolution is derived, not authored.** `render_resolution` at the top level mirrors `y_gate_score.render_resolution`. Do not set them independently.

---

## Field definitions

### Top-level required fields

#### `receipt_id`
- **Type:** string
- **Pattern:** `ARCS-ORIENT-[ISO8601]-[8-char hash]`
- **Example:** `ARCS-ORIENT-2026-05-26T13:01:00Z-a3f9c21b`
- **Note:** Generated at L5 freeze. Not user-supplied.

#### `surface`
- **Type:** enum string
- **Values:** `ORIENT | CALIBRATE | CHART_COURSE | DETECT`
- **For this schema:** Always `ORIENT`.

#### `version`
- **Type:** enum string
- **Values:** `"0.1.0"` (only)
- **Note:** Pinned at creation time. Receipts are not migrated to new schema versions.

#### `sharp_question`
- **Type:** string (≤280 characters)
- **Produced by:** L0 Question Sharpener
- **Note:** Single sentence. The atomic decision question confirmed by the user before L1 fires. Not the raw user input — the sharpened form.

#### `dewy_vector`
The four-axis coordinate of this decision on the manifold. See DEWY axes below.

#### `y_gate_score`
Mirror of `dewy_vector.Y` plus render artifacts. See Y-gate section below.

#### `nci_score`
Five-lens Network Coherence Index from L3. See NCI section below.

#### `true_north`
- **Type:** string
- **Example:** `"Take the Company X offer."`
- **Note:** Single directional sentence produced by L4. The bearing. Not a recommendation — a reading of the terrain.

#### `why`
- **Type:** string array (1–5 items)
- **Note:** Supporting reasons for `true_north`. Each item is a distinct factual or structural reason. Not "because you said so" — earned terrain observations.

#### `loki`
- **Type:** string
- **Note:** The strongest argument that `true_north` is wrong. Always present. Synthesized internally even if the PrepSession `adversarialInput` field was absent. Named after the trickster — it is always playing devil's advocate.

#### `bar`
BAR macro output: Baseline ruin / Asymmetry / Reversibility. See BAR section below.

#### `render_resolution`
- **Type:** enum string
- **Values:** `GRAIN | MOIRE | DEGRADED | SHARP`
- **Derived from:** `y_gate_score.render_resolution`
- **Render scale (from WORLD.md):**

| Value | Y State | Opacity | Weight | Tracking |
|-------|---------|---------|--------|----------|
| `GRAIN` | SCRATCH / EPHEMERAL | 0.70 | 300 | +0.02em |
| `MOIRE` | PARADOX | 0.60 | 300 | +0.03em + CSS ::after |
| `DEGRADED` | YELLOW / CONTESTED | 0.85 | 400 | +0.01em |
| `SHARP` | GREEN / HIGH | 1.0 | 500 | normal |

#### `validation_state`
- **Type:** enum string
- **Values:** `PASS | HOLD | REJECT`
- **Note:** Gate state from the HOLD/REJECT validator (SKILL.md §6). Only PASS receipts contain full DEWY decomposition.

#### `session_ts`
- **Type:** string (ISO 8601 date-time)
- **Note:** L5 freeze time. When the receipt was sealed.

---

### DEWY vector sub-fields

#### `dewy_vector.D` — Decision
- **Type:** string
- The atomic question in action form, extracted from `sharp_question`. D is the verb — what is being decided, stripped of context preamble.

#### `dewy_vector.E` — Entity
| Sub-field | Type | Required | Description |
|-----------|------|----------|-------------|
| `self` | string | yes | The deciding agent |
| `other` | string[] | no | Other entities in the terrain. Compressed to primary + secondary if >10 named |
| `entity_overflow` | string[] | no | Entities omitted from `other` due to overflow. Present only when >10 entities |

#### `dewy_vector.W` — Window
| Sub-field | Type | Required | Description |
|-----------|------|----------|-------------|
| `horizon` | enum | yes | `TODAY \| WEEK \| QUARTER \| YEAR \| YEARS` |
| `lock_date` | date string | no | Hard lock date (ISO 8601). Absent if unknown |
| `inferred` | boolean | no | True when horizon was auto-inferred, not explicitly provided |

#### `dewy_vector.Y` — Yellow Gate
| Sub-field | Type | Required | Values | Description |
|-----------|------|----------|--------|-------------|
| `polarity` | enum | yes | `SCRATCH \| YELLOW \| PARADOX \| FORK \| DELTA \| GREEN \| LOCKED` | Y-gate polarity state |
| `conviction` | enum | yes | `LOW \| MEDIUM \| HIGH` | Conviction level within polarity |
| `stability` | enum | yes | `SHIFTING \| CONTESTED \| STABLE` | Rate of change in the conviction gradient |

**Polarity definitions:**

| State | Terrain description |
|-------|---------------------|
| `SCRATCH` | Scratchpad — not yet committed to session history |
| `YELLOW` | Moving but contested — conviction gradient is active |
| `PARADOX` | Options non-separable — Curator auto-invoked |
| `FORK` | Two live paths with significant separation |
| `DELTA` | Conviction collapsed — inflection point tracked |
| `GREEN` | High conviction — clear directional signal |
| `LOCKED` | Post-Court resolved — Kairos Lock active |

---

### Y-gate score

`y_gate_score` mirrors `dewy_vector.Y` and adds render artifacts:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `polarity` | enum | yes | Same values as `dewy_vector.Y.polarity` |
| `conviction` | enum | yes | Same values as `dewy_vector.Y.conviction` |
| `stability` | enum | yes | Same values as `dewy_vector.Y.stability` |
| `render_resolution` | enum | yes | `GRAIN \| MOIRE \| DEGRADED \| SHARP` |
| `visual_treatment` | object | no | CSS treatment: `opacity` (0–1), `font_weight` (300/400/500/600), `tracking` (string) |

---

### NCI score

Network Coherence Index — five-lens scoring from L3:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `composite` | integer (0–100) | yes | Sum of all five lens scores |
| `grade` | string | yes | Human-readable grade. E.g. `"B+ — Conviction is the weak lens."` |
| `by_lens.clarity` | integer (0–20) | yes | How well-formed and atomic is the question? |
| `by_lens.conviction` | integer (0–20) | yes | How strong and directional is the conviction signal? |
| `by_lens.coherence` | integer (0–20) | yes | Do the stated reasons cohere? Internal contradiction? |
| `by_lens.consequence` | integer (0–20) | yes | Are downstream effects understood? |
| `by_lens.cadence` | integer (0–20) | yes | Is the timing appropriate? Not too early, not too late? |

**Composite thresholds:**

| Range | Behavior |
|-------|----------|
| 0–39 | HOLD — do not emit receipt |
| 40–59 | Proceed with warning — `fidelity_header` required |
| 60–79 | DEGRADED render |
| 80–100 | SHARP render |

---

### BAR macro

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ruin_risk` | string | yes | Worst-case outcome if `true_north` is wrong. Prefixed: `LOW / MEDIUM / HIGH / EXISTENTIAL` |
| `asymmetry` | string | yes | Is the upside/downside asymmetric? In which direction? |
| `reversibility` | string | yes | Can this be unwound? At what cost and in what window? |

---

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `fidelity_header` | string | Shown at top of Brief when `render_resolution != SHARP`. E.g. `"This brief renders at 85% fidelity — conviction gradient is still SHIFTING."` |
| `inferred_fields` | string[] | Fields auto-inferred (not explicitly provided). Transparency log. E.g. `["stakes", "W.horizon", "Y"]` |
| `collision_fields` | string[] | Fields where two valid parses collided. Logged when HOLD resolved |
| `horizon` | enum | Top-level convenience mirror of `dewy_vector.W.horizon`. For indexing only |
| `stakes` | enum | `LOW \| MEDIUM \| HIGH \| EXISTENTIAL` — from PrepSession or auto-inferred |
| `mode` | enum | `QUICKMOVE \| PLAN \| COURT` — evaluation mode |
| `clarity_mode` | enum | `SIMPLE \| RICH \| DEEP` — output verbosity |
| `macros_run` | string[] | Which macros fired: `LAB \| BAR \| KKL \| ATG` |
| `drift_state` | enum | `ON_TRACK \| DRIFTING \| LOCKED \| LANDED` — Drift Sentinel state at freeze |
| `prep_session_id` | string | ID of the PrepSession that seeded this receipt |
| `parent_receipt_id` | string | ID of the parent receipt if this is a re-run or refinement |

---

## Worked example

A user submits: *"Should I take the job at Company X or stay where I am?"*

After L0 sharpening: `sharp_question = "Should I accept the Company X offer before Friday's deadline?"`

A PASS receipt at SHARP resolution looks like:

```json
{
  "receipt_id": "ARCS-ORIENT-2026-05-26T13:01:00Z-a3f9c21b",
  "surface": "ORIENT",
  "version": "0.1.0",
  "sharp_question": "Should I accept the Company X offer before Friday's deadline?",
  "dewy_vector": {
    "D": "Accept Company X offer by Friday",
    "E": { "self": "Zach", "other": ["Company X hiring manager", "current employer"] },
    "W": { "horizon": "WEEK", "lock_date": "2026-05-30", "inferred": false },
    "Y": { "polarity": "GREEN", "conviction": "HIGH", "stability": "STABLE" }
  },
  "y_gate_score": {
    "polarity": "GREEN",
    "conviction": "HIGH",
    "stability": "STABLE",
    "render_resolution": "SHARP",
    "visual_treatment": { "opacity": 1.0, "font_weight": 500, "tracking": "normal" }
  },
  "nci_score": {
    "composite": 84,
    "grade": "A- — Consequence is the weak lens.",
    "by_lens": { "clarity": 18, "conviction": 17, "coherence": 17, "consequence": 15, "cadence": 17 }
  },
  "true_north": "Accept the Company X offer.",
  "why": [
    "Deadline is real — delay past Friday converts to a no.",
    "Conviction gradient is stable HIGH — no ambivalence signal detected.",
    "Role aligns with Q3 trajectory already locked in prior session."
  ],
  "loki": "You haven't tested whether current employer would match. You're deciding under incomplete information on the counterfactual.",
  "bar": {
    "ruin_risk": "LOW — worst case is a role that underperforms; exit window is 6 months.",
    "asymmetry": "Upside asymmetric — ceiling at Company X significantly higher.",
    "reversibility": "Low reversibility once accepted, but not existential. Bridge preserved."
  },
  "render_resolution": "SHARP",
  "validation_state": "PASS",
  "session_ts": "2026-05-26T13:01:00Z",
  "mode": "PLAN",
  "stakes": "HIGH",
  "horizon": "WEEK",
  "macros_run": ["LAB", "BAR"]
}
```

---

## Failure modes

| ID | Condition | Behavior |
|----|-----------|----------|
| FM-R1 | `receipt_id` format mismatch | REJECT — log malformed ID, do not persist |
| FM-R2 | `nci_score.composite < 40` | HOLD — do not emit receipt; surface which lens is blocking |
| FM-R3 | `dewy_vector.Y.polarity = PARADOX` | HOLD — Curator auto-invoked; receipt deferred until paradox resolved |
| FM-R4 | `validation_state = HOLD` but full decomposition present | REJECT — integrity violation; HOLD receipts carry stub only |
| FM-R5 | `render_resolution` at top level differs from `y_gate_score.render_resolution` | REJECT — fields must be identical; derived field set inconsistently |
| FM-R6 | `why` array empty | REJECT — true_north without supporting terrain is not a bearing |
| FM-R7 | `loki` absent | REJECT — every receipt must carry the strongest counter-argument |

---

## Acceptance criteria

- [ ] Every required field listed in the JSON schema is present and typed correctly in a PASS receipt
- [ ] HOLD receipts carry only: `receipt_id`, `surface`, `version`, `validation_state`, `hold_reason`, `blocking_question`, `session_ts`
- [ ] REJECT receipts carry only: `receipt_id`, `surface`, `version`, `validation_state`, `reject_reason`, `session_ts`
- [ ] `render_resolution` (top-level) === `y_gate_score.render_resolution` on all receipts
- [ ] `nci_score.composite` is the arithmetic sum of the five `by_lens` values
- [ ] All array fields are stored as JSON-stringified TEXT in SQLite (never as Prisma `Json` type)
- [ ] `receipt_id` matches the pattern `ARCS-ORIENT-[ISO8601]-[8-char hash]`
- [ ] `loki` is always present on PASS receipts regardless of PrepSession state
- [ ] Prisma `Receipt` model contains fields for every required property in this schema
