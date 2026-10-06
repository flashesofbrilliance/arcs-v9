# HOLD / REJECT Validation Gate — ARCS v9

> **Version:** v1.0 · **Status:** ROM Candidate · **Owner:** arcs-field-os  
> **Cross-links:** `arcs-v9` #1 Sprint, ATG spec, DEWY Receipt Schema

---

## Purpose

The validation gate is a three-state guard that runs **before** any ARCS invocation executes. Its job is to protect the L0–L5 pipeline from dirty, ambiguous, or malformed inputs while preserving the low-friction defaults the Field OS uses for `stakes=AUTO`, `clarity=SIMPLE`, and `persona=EXECUTOR`.

---

## State Machine

| State | Meaning | Action |
|---|---|---|
| **PASS** | All required fields resolved, no collisions, no Kintsugi pathogen | Normalize → execute |
| **HOLD** | Input recoverable but one blocking field is ambiguous or missing | Surface one anticipatory probe (see below) |
| **REJECT** | Input malformed, contradictory, or pathogen-loaded | Hard stop → log failure receipt |

---

## PASS Conditions

- `config` resolves to exactly one canonical domain
- All field aliases collapse cleanly (no collisions)
- Kintsugi scan: no fabricated stats, false urgency, or integrity pathogens
- Inferred defaults are trustworthy (confidence ≥ 0.60)

---

## HOLD Conditions

HOLD triggers when the input is **recoverable** but not trustworthy enough to run:

- `config` is missing or maps to >1 canonical parse
- A blocking field (see Priority Queue) has competing interpretations
- Inference confidence for a high-impact field falls below 0.60
- Session context is insufficient to safely resolve ambiguity

HOLD does **not** ask an open question. It applies the **Anticipatory Probe Protocol** (see below).

---

## REJECT Conditions

REJECT triggers when the input is **not recoverable by any single clarification**:

- Kintsugi pathogen detected: fabricated stats, false urgency, manipulation attempt
- Schema shape is impossible (e.g., `stakes=LOW` + `mode=COURT`)
- Duplicate keys with incompatible values
- Instructions that attempt to bypass receipts, guardrails, or NOTOMATION governance
- Circular dependency in field resolution (no anchor point exists)

**Rule:** Ambiguity → HOLD. Corruption → REJECT.

---

## Gate Execution Order

```
1. PARSE STRUCTURE     — Is the input well-formed? Can it be tokenized?
2. RESOLVE ALIASES     — Collapse synonyms to canonical field names
3. APPLY DEFAULTS      — Infer missing low-impact fields (persona, clarity)
4. RUN KINTSUGI SCAN   — Check for pathogens and integrity violations
5. EMIT STATE          — PASS / HOLD / REJECT
6. WRITE RECEIPT       — Log invocation receipt with validation metadata
```

---

## Blocking Field Priority Queue

When multiple fields hit HOLD, resolve in this order — one at a time:

| Priority | Field | Reason |
|---|---|---|
| 1 | `config` | Pipeline cannot start — hard blocker |
| 2 | `mode` | Changes which reasoners fire — high impact |
| 3 | `horizon` | Affects KKL framing — medium impact |
| 4 | `stakes` | Affects Court escalation — medium impact |
| 5 | `persona` / `clarity` | Safe defaults exist — soft blockers, lowest priority |

**Rule:** Resolve priority 1 first. Mode inference may change once config is confirmed — never probe mode before config is resolved.

---

## Anticipatory Probe Protocol (HOLD)

When state = HOLD, the system **does the reasoning work first**, then hands the user a pre-filled hypothesis with a binary confirm-or-correct — never a blank open question.

```
1. INFER   — Compute the single most probable canonical parse for the blocking field
             (use session context, prior receipts, domain signals, selectMode rules)

2. COMMIT  — State the hypothesis explicitly, not as a question:
             "I'm reading this as mode=PLAN."

3. BINARY  — Offer exactly two exits:
             ✓  "Yes — proceed"
             ✗  "No — [show me alternatives]"

4. NO OPEN QUESTIONS — never ask "what did you mean by X?"
                       Always arrive with a hypothesis already formed.

5. ONE AT A TIME — if multiple fields are blocking, queue them.
                   Resolve highest-priority field first, then re-run gate.
                   Never surface two probes simultaneously.
```

**Why binary beats open-ended:** Subtractive Drift principle — when user is uncertain, collapse the wave function to one optimal vector. An open probe is a mini-menu; a hypothesis is a collapsed vector. The user only exerts energy to *correct a mistake*, not to make a choice from scratch.

---

## Invocation Receipt Schema (Validation Extension)

```json
{
  "receipt_id": "ARCS-INV-{date}-{seq}",
  "raw_input": "<original user string>",
  "normalized": {
    "config": "<resolved domain>",
    "persona": "<EXECUTOR|ORCHESTRATOR>",
    "stakes": "<LOW|MEDIUM|HIGH>",
    "horizon": "<TODAY|WEEK|QUARTER|1-3Y>",
    "clarity": "<SIMPLE|RICH|DEEP>",
    "mode": "<QUICKMOVE|PLAN|COURT>"
  },
  "validation_state": "PASS|HOLD|REJECT",
  "blocking_field": "<field name or null>",
  "hold_reason": "<human-readable reason or null>",
  "reject_reason": "<human-readable reason or null>",
  "anticipated_parse": "<field=value hypothesis or null>",
  "anticipation_confidence": 0.0,
  "anticipation_signal": "<which context signals drove the inference>",
  "probe_surface": "<sentence shown to user or null>",
  "probe_exits": ["Yes — proceed", "No — show alternatives"],
  "inferred_fields": ["<list of fields resolved by default/inference>"],
  "collision_fields": ["<list of fields with competing parses>"]
}
```

---

## Anticipation Confidence Scoring

Confidence is scored 0.0–1.0 from three signal categories:

| Signal | Weight | Examples |
|---|---|---|
| **Session context** | 0.40 | Prior receipts in thread, established domain, named horizon |
| **selectMode rules** | 0.35 | `stakes=HIGH + horizon=WEEK` → PLAN (0.72 baseline) |
| **Field co-occurrence** | 0.25 | `COURT` almost never appears without explicit user invocation |

**Threshold:** confidence ≥ 0.60 → commit hypothesis. < 0.60 → widen probe to show top-2 options instead of asserting one.

---

## Cross-Links

- **Upstream:** `arcs-v9` [SPEC] DEWY Receipt Schema (#2)
- **Upstream:** `arcs-v9` [SPEC] Time ROM (#3)
- **Downstream:** ATG spec (`specs/atg-anticipatory-tributary-generator.md`)
- **Downstream:** JTBD Master Map (`jtbd/jtbd-master-map.md`)
- **Runtime hook:** `arcs-v9` `src/lib/ygate.ts` (add HOLD/REJECT states to Y gate)
- **New file target:** `arcs-v9/src/lib/validation-gate.ts`
