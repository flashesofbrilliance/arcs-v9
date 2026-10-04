# Orient PRD — v0.1.0
> **Surface:** Orient (A) — "Help me find my position and True North"
> **Status:** CANONICAL — Kairos Lock active. This document is the governing spec for the Orient surface. All downstream implementation (arcs-v9 Issues #2, #3, #4) inherits from it.
> **Date:** 2026-05-26
> **Owner:** arcs-field-os
> **Runtime home:** arcs-v9
> **JTBD master map:** [jtbd/jtbd-master-map.md](../jtbd/jtbd-master-map.md)
> **World physics:** [arcs-v9/WORLD.md](https://github.com/flashesofbrilliance/arcs-v9/blob/main/WORLD.md)

---

## 0. Kairos Lock Declaration

This PRD is in **Kairos Lock**. That means:

- The surface definition is committed. Downstream specs may extend it but may not contradict it.
- Every abstraction in this document was earned before it was named. Where a concept appears, the worked example follows within the same section.
- The Diamond Protocol ran on every boundary: NULL (what if no input?), OM (what if maximal input?), UNDEFINED (what if the input is valid but ambiguous?).
- HOLD/REJECT was tested at every stage gate.

If you are reading this to implement a feature, you have full authority to operationalize. You do not have authority to change the surface's primary JTBD, the Y-gate schema, or the DEWY receipt structure without bumping this document to v0.2.0 and opening a PR against `arcs-field-os`.

---

## 1. The Job

**Primary JTBD:** *"Help me find my position and True North."*

**Hire condition:** The question is clean. Stakes are real. The user is not paralyzed by a malformed question (that is Calibrate's job); they are paralyzed by uncertainty about which path is correct given a question they already understand. They need structured judgment with a receipt — not a search result, not a checklist, not a reframe.

**What "orient" means in world-physics terms:**

The user has entered the ARCS terrain. They are somewhere in the Pressure Band or Outer Fog Layer — their DEWY state vector is partially populated but the Y-gate conviction gradient is YELLOW or lower. Orient's job is to run the full L0–L5 pipeline, crystallize the DEWY vector, score the Y-gate, and return a True North bearing with fidelity proportional to the earned clarity.

**What Orient is NOT:**

- It is not a research tool. If the user needs facts, Orient routes them out.
- It is not a coach. It does not ask how you feel about the terrain.
- It is not a planner. Planning is Chart Course (C). Orient ends when True North is visible — it does not map the full route.
- It is not a validator of decisions already made. If the conviction gradient is LOCKED before the session starts, Orient returns a receipt acknowledging the lock and routes to Chart Course or Observatory.

**Worked example — hire condition in the wild:**

> User: "I have to decide by Friday whether to take the offer from Company X or stay and lead the Series A. Both options feel right. I keep going in circles."

This is a clean question (genuine fork, real stakes, real window). The user is not asking the wrong question — they are asking the right question in fog. Orient fires. Calibrate is not needed. Chart Course is not needed yet.

---

## 2. Inputs

### 2.1 The PrepSession (Optional — Strongly Recommended)

The PrepSession is the calibration instrument. Five fields. Two minutes. When completed, the Compass runs with richer context and the terrain sharpens faster.

| Field | Label | Type | Required | NULL behavior | OM behavior | UNDEFINED behavior |
|---|---|---|---|---|---|---|
| `question` | What are you deciding? | string | YES | → HOLD: blocking field | Truncate to 280 chars, log excess | → HOLD: ambiguous parse |
| `stakes` | Stakes level | enum: LOW / MEDIUM / HIGH / EXISTENTIAL | NO | Default: AUTO-INFER from question text | n/a | Default: MEDIUM |
| `window` | Time horizon | enum: TODAY / WEEK / QUARTER / YEAR / YEARS | NO | Default: AUTO-INFER from question | n/a | Default: WEEK |
| `protecting` | What are you protecting? | string | NO | Y-gate runs without ruin-bias | n/a | Accept as-is |
| `contra` | Strongest argument against your instinct | string | NO | LAB macro skips adversarial branch | n/a | Accept as-is |

**NULL / OM / UNDEFINED worked examples:**

*NULL — `question` missing:*
```json
{ "validation_state": "HOLD", "blocking_field": "question",
  "blocking_question": "What are you actually trying to decide?" }
```
No further processing until `question` is resolved.

*OM — `question` is 3,000 words of context dump:*
The system does not refuse. It runs the L0 Question Sharpener on the full text, extracts the atomic decision, and logs the compression ratio in the receipt. The user sees the sharpened question before L1 fires and can edit it.

*UNDEFINED — `stakes` = "it's complicated":*
System infers stakes from question text using the Y-gate polarity scan. Logs `inferred_field: stakes` in the receipt. The user sees the inferred value and can override before receipt is committed.

### 2.2 Direct Compass Input (No PrepSession)

When the user bypasses PrepSession and fires the Compass directly (e.g., `init arcs config=FIELD-OS ...`), the system runs HOLD/REJECT validation on the raw string before any pipeline stage fires.

HOLD fires when:
- `config` is unresolvable (no canonical parse)
- Two or more valid parses exist with incompatible `mode` values
- `question` cannot be extracted from the input string

REJECT fires when:
- Input contains a Kintsugi pathogen (fabricated authority, false urgency injection, bypass instruction)
- Schema is broken (duplicate keys, contradictory values)
- The invocation attempts to skip the receipt layer

PASS fires when `config` resolves, `question` extracts cleanly, and no pathogens are present.

---

## 3. The Engine — L0 through L5

Orient runs the full six-stage pipeline. Each stage has an entry condition, a transformation, and an exit artifact. A stage may return HOLD (block and ask) or REJECT (abort and log). It may not silently skip.

### Stage L0 — Question Sharpener

**Entry:** Raw question string (from PrepSession or direct input)
**Transformation:** Strip noise, collapse compound questions to atomic form, surface the underlying decision hidden inside a symptom statement.
**Exit artifact:** `sharp_question` — a single sentence, ≤ 280 characters, that captures the atomic decision.
**Exit check:** Is this the question the user actually needs to answer? If the sharpened question is materially different from the input, surface it for user confirmation before L1 fires.

*Worked example:*
> Raw: "Should I take the Company X offer or stay for the Series A?"
> Sharp: "Which path — Company X offer vs. Series A lead — better serves my 3-year career vector given the constraints I'm protecting?"

The sharpened form adds the time window and stakes dimension the user implied but didn't state. User confirms or edits. L1 fires.

**NULL:** No question → HOLD.
**OM:** 3,000-word context dump → extract, compress, log ratio, surface for confirmation.
**UNDEFINED:** Question is valid but genuinely ambiguous about which fork is being evaluated → surface two candidate sharpenings, let user select.

---

### Stage L1 — DEWY Decomposition

**Entry:** `sharp_question`
**Transformation:** Populate the four DEWY fields from the question and PrepSession context.

| Field | Full name | Meaning | Extracts from |
|---|---|---|---|
| D | Decision | The atomic question in action form | `sharp_question` |
| E | Entity | Who or what else is in the terrain | PrepSession + question text |
| W | Window | Time horizon — when does this decision lock? | PrepSession `window` or inferred |
| Y | Yellow Gate | Conviction gradient — where is the user on the manifold? | PrepSession `protecting` + `contra` + polarity scan |

**Exit artifact:** `dewy_vector` — a four-field object that is the ARCS coordinate for this decision.

*Worked example:*
```json
{
  "D": "Take Company X offer vs. lead Series A",
  "E": { "self": "user", "other": ["Company X", "current co + investors"] },
  "W": { "horizon": "YEAR", "lock_date": "2026-05-30" },
  "Y": { "polarity": "FORK", "conviction": "YELLOW", "stability": "SHIFTING" }
}
```

**NULL — Y-field:** If `protecting` and `contra` are both absent and the question text gives no conviction signal → Y defaults to `YELLOW / SHIFTING`. Logged in receipt as `inferred_field: Y`.
**OM — E-field:** If entity list is exhaustive (user named 40 stakeholders) → compress to primary and secondary entities, log excess in receipt under `entity_overflow`.
**UNDEFINED — W-field:** If window cannot be inferred → surface `blocking_question: "When does this decision lock — is there a hard date?"` This is a HOLD, not a REJECT. The W-field is load-bearing for the Y-gate; running without it degrades Brief fidelity.

---

### Stage L2 — Y-Gate Scoring

**Entry:** `dewy_vector`
**Transformation:** Score the conviction gradient across the 12-dimensional Y manifold: four polarity states × three conviction levels × three stability modes.

**Polarity states:**
| State | Meaning |
|---|---|
| SCRATCH | No polarity yet — pure fog |
| YELLOW | Contested — genuine fork with roughly equal pull |
| PARADOX | Polarity exists but direction is self-contradictory |
| FORK | Clear fork — two distinct paths, roughly comparable weight |
| DELTA | Rate of change is the actual variable, not the position |
| GREEN | High conviction — direction is clear, confirmation sought |
| LOCKED | Post-Court resolved — user is executing, not deciding |

**Conviction levels:** LOW / MEDIUM / HIGH
**Stability modes:** SHIFTING / CONTESTED / STABLE

**Exit artifact:** `y_gate_score` — a polarity/conviction/stability triple. Also emits `render_resolution` based on Y state (see WORLD.md Render Scale).

*Worked example:*
```json
{
  "y_gate_score": {
    "polarity": "FORK",
    "conviction": "LOW",
    "stability": "SHIFTING"
  },
  "render_resolution": "DEGRADED",
  "visual_treatment": { "opacity": 0.85, "font_weight": 400, "tracking": "+0.01em" }
}
```

**REJECT condition:** If polarity = PARADOX AND conviction = HIGH → this is a self-contradictory high-conviction state. The system surfaces: *"You're certain, but your two positions can't both be true. That's not a decision problem — it's a framing problem. Do you want to run Calibrate first?"* If user declines, REJECT with `reject_reason: "PARADOX_HIGH_CONVICTION — proceed to Calibrate"`.

---

### Stage L3 — NCI Scoring (Network Coherence Index)

**Entry:** `dewy_vector`, `y_gate_score`
**Transformation:** Score the decision context against the five NCI lenses:
1. **Clarity** — is the question sharp and singular?
2. **Conviction** — what is the Y-gate reading?
3. **Coherence** — are D, E, W, Y internally consistent?
4. **Consequence** — are stakes and reversibility mapped?
5. **Cadence** — is the decision window realistic?

Each lens scores 0–20. NCI is the sum (0–100).

**Exit artifact:** `nci_score` with per-lens breakdown and composite.

*Worked example:*
```json
{
  "nci_score": {
    "clarity": 16, "conviction": 12, "coherence": 15,
    "consequence": 14, "cadence": 18,
    "composite": 75,
    "grade": "B+ — Good to proceed. Conviction is the weak lens; Brief will render at DEGRADED fidelity."
  }
}
```

**NCI < 40:** HOLD. The brief will be too coarse to be useful. Surface: *"NCI is [score]. The brief at this clarity level won't be reliable. The weakest lens is [lens]. Want to sharpen it before running?"*
**NCI 40–59:** Proceed with explicit fidelity warning in Brief header.
**NCI 60–79:** Proceed normally. DEGRADED render.
**NCI 80–100:** Proceed. SHARP render. Brief header omits fidelity caveat.

---

### Stage L4 — True North Generation

**Entry:** `dewy_vector`, `y_gate_score`, `nci_score`
**Transformation:** Run the LAB macro (adversarial / advisor / Bayes) and BAR macro (ruin risk / reversibility / asymmetry) to produce a True North bearing.

**LAB macro:**
- **L (Loki):** What is the strongest argument that the preferred direction is wrong?
- **A (Advisor):** What would the most trusted advisor in this domain say?
- **B (Bayes):** What does the base rate say about decisions of this type in this window?

**BAR macro:**
- **B (Baseline ruin risk):** What is the worst-case outcome if this path is wrong?
- **A (Asymmetry):** Is the upside/downside asymmetric? In which direction?
- **R (Reversibility):** Can this decision be unwound? At what cost?

**Exit artifact:** `true_north` — a single directional sentence + three supporting bullets (why), Loki surface (strongest counter), BAR edge (ruin + reversibility).

*Worked example:*
```json
{
  "true_north": "Take the Company X offer.",
  "why": [
    "Series A timeline is 18+ months with >3 decision points before liquidity; Company X offer locks value now",
    "Your `protecting` field named financial stability — that asymmetry favors X",
    "Base rate for first-time Series A leads hitting planned exit: ~22%"
  ],
  "loki": "The Series A is the higher-expected-value path if the company hits its round — you may be discounting optionality",
  "bar": {
    "ruin_risk": "LOW — both paths have recoverable failure modes",
    "asymmetry": "X offer is more certain, Series A is higher variance — pick by risk tolerance, not expected value alone",
    "reversibility": "X offer has a 5-day acceptance window; Series A leadership can likely be renegotiated with a month"
  }
}
```

**NULL — LAB / `contra` absent:** Loki still runs using internal adversarial synthesis. The system does not skip the challenge branch because the user didn't provide a `contra` field.
**REJECT condition:** If True North cannot be generated (e.g., the question decomposes to a values conflict with no factual resolution) → surface: *"This is a values question, not a decision question. ARCS can map the values terrain but cannot generate a True North without a factual variable to arbitrate on. Do you want to proceed to Calibrate?"*

---

### Stage L5 — Receipt Generation & Brief Render

**Entry:** All prior stage artifacts
**Transformation:** Freeze the full decision state as a Receipt. Render the Brief at `render_resolution` earned by the Y-gate score.

**Receipt fields (DEWY schema v0.1.0):**

```json
{
  "receipt_id": "ARCS-ORIENT-[timestamp]-[hash]",
  "surface": "ORIENT",
  "version": "0.1.0",
  "sharp_question": "...",
  "dewy_vector": { "D": "...", "E": {...}, "W": {...}, "Y": {...} },
  "y_gate_score": { "polarity": "...", "conviction": "...", "stability": "..." },
  "nci_score": { "composite": 75, "grade": "...", "by_lens": {...} },
  "true_north": "...",
  "why": [...],
  "loki": "...",
  "bar": {...},
  "render_resolution": "DEGRADED",
  "inferred_fields": [...],
  "collision_fields": [...],
  "validation_state": "PASS",
  "horizon": "YEAR",
  "stakes": "HIGH",
  "mode": "PLAN",
  "clarity_mode": "SIMPLE",
  "macros_run": ["LAB", "BAR"],
  "session_ts": "2026-05-26T12:50:00Z",
  "drift_state": "LOCKED"
}
```

**Brief render:** The Brief is the human-readable output. It renders at the earned `render_resolution`. At DEGRADED, it carries a fidelity header: *"This brief renders at 85% fidelity — the conviction gradient is still SHIFTING. The True North is directionally reliable but not crystalline."*

---

## 4. Outputs

| Output | Format | Audience | Render condition |
|---|---|---|---|
| Receipt | JSON | System / downstream surfaces | Every PASS |
| Brief | Markdown | User | Every PASS |
| HOLD notice | Single question | User | When blocking field detected |
| REJECT notice | Reason + routing | User | Integrity failure or unresolvable fork |
| Fidelity header | Inline text in Brief | User | NCI < 80 or Y = SCRATCH/PARADOX |

---

## 5. Stage Gate Summary

```
Input ──→ L0 Question Sharpener
             ↓ HOLD if question unresolvable
          L1 DEWY Decomposition
             ↓ HOLD if W-field absent
          L2 Y-Gate Scoring
             ↓ REJECT if PARADOX_HIGH_CONVICTION
          L3 NCI Scoring
             ↓ HOLD if NCI < 40
          L4 True North (LAB + BAR)
             ↓ REJECT if values-only conflict
          L5 Receipt + Brief Render
             ↓ PASS
         Output
```

---

## 6. Routing Rules (Post-Orient)

After Orient completes, the system offers one of three routes based on the receipt:

| Receipt state | Route offered |
|---|---|
| Y = LOCKED / GREEN, NCI ≥ 80 | → Chart Course |
| Y = YELLOW / FORK, NCI 60–79 | → Chart Course (with fidelity warning) or re-run Orient with richer PrepSession |
| Y = SCRATCH / PARADOX, NCI < 60 | → Calibrate (surface the Calibrate JTBD) |

---

## 7. Open Issues (arcs-v9)

This PRD directly governs the following open issues. Each issue author should read this document before implementation:

| Issue | Title | Dependency on this PRD |
|---|---|---|
| [#2](https://github.com/flashesofbrilliance/arcs-v9/issues/2) | DEWY Receipt Schema | Section 3 L5, Receipt fields spec |
| [#3](https://github.com/flashesofbrilliance/arcs-v9/issues/3) | Time Quality Attribution ROM | Section 3 L2 Y-gate, W-field inference rules |
| [#4](https://github.com/flashesofbrilliance/arcs-v9/issues/4) | Compass → DEWY Flow | Section 3 full pipeline L0–L5 |

---

## 8. NOTOMATION Compliance

Every stage of the Orient pipeline is a scaffold for human cognition, not a replacement:

- L0 surfaces the sharpened question for user confirmation — it does not silently substitute a better question
- L2 shows the Y-gate polarity and conviction to the user — they can edit before L3 fires
- L4 shows the Loki surface (strongest counter-argument) — the user decides whether to override True North
- L5 renders the Brief at earned fidelity — the system does not hide uncertainty

The NOTOMATION rule: *tools may only externalize / scaffold / sequence human cognition.* Orient never decides for the user. It makes the terrain legible so the user can navigate.

---

## 9. Changelog

| Version | Date | Change |
|---|---|---|
| v0.1.0 | 2026-05-26 | Initial creation — Kairos Lock. Diamond Protocol applied. All six L-stages specified with worked examples and NULL/OM/UNDEFINED coverage. |

---

*This document is in Kairos Lock. To propose a change, open a PR against `arcs-field-os/specs/orient-prd.md` and bump to v0.2.0.*
