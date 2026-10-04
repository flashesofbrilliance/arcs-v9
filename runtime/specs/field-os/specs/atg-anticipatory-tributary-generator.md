# ATG — Anticipatory Tributary Generator

> **Version:** v1.0 · **Status:** P0 Backlog · **Owner:** arcs-field-os  
> **Cross-links:** HOLD/REJECT gate, DEWY Y-layer, Question Compass flow

---

## Purpose

ATG is a secondary output head on every ARCS compass response. It infers the user’s deeper trajectory and surfaces 2–4 ranked follow-up prompts as one-click tributary chips — not generic suggestions, but options that represent:

1. **The meta-question** the user is actually asking beneath the surface question
2. **The need-to-hear branch** the user might be avoiding
3. **An adjacent ARCS primitive or mode** clearly implicated but not named
4. **(Optional) A Curator/Alchemist variant** — only if CUR/ALC are explicitly active

ATG runs **after** every PASS invocation and feeds both the UI chip layer and the DEWY Y (Yield) layer.

---

## Input Schema

```typescript
interface ATGInput {
  currentMessage: string;
  lastNTurns: Turn[];           // last 3–5 turns
  arcsState: {
    domain: string;             // resolved config
    romRam: 'ROM' | 'RAM';      // promotion tier of this session
    kairosChronos: 'KAIROS' | 'CHRONOS' | 'DRIFT';
    energyLevel: 'HIGH' | 'MEDIUM' | 'LOW';
    receiptId: string;
  };
}
```

---

## Output Schema

```typescript
interface ATGOutput {
  answerText: string;           // main compass response (unchanged)
  tributaries: Tributary[];     // 2–4 ranked chips
}

interface Tributary {
  prompt: string;               // exact text for one-click / copy
  type: 'meta' | 'need-to-hear' | 'adjacent-primitive' | 'alchemist';
  priority: 1 | 2 | 3 | 4;     // 1 = highest leverage
  arcsPrimitive?: string;       // e.g. 'NOTOMATION', 'WRITE-LOCK', 'DEWY'
}
```

---

## Generation Rules

1. **Always include a `meta` tributary** — the question beneath the question.
2. **Always include a `need-to-hear` tributary** — the branch the user might avoid.
3. **Include `adjacent-primitive` when** a named ARCS primitive is clearly implicated but unaddressed.
4. **Never generate generic chips** like "Tell me more" or "Explain further" — every tributary must be immediately actionable and specific to this session.
5. **Respect energy level:** if `energyLevel=LOW`, max 2 tributaries, make them short.
6. **Respect NOTOMATION:** tributaries scaffold cognition, they do not replace it. Never auto-execute a tributary without user selection.

---

## HOLD Probe Relationship

ATG runs on PASS. The HOLD probe protocol is ATG running **backward** — instead of inferring where the user wants to go, it infers what they meant and pre-fills the most likely answer as a binary confirm-or-correct. See `specs/hold-reject-validation-gate.md`.

---

## DEWY Y-Layer Hook

ATG tributary selection events feed the DEWY Y (Yield) layer:
- Which tributaries were shown
- Which (if any) were selected
- Time-to-selection (Kairos signal)

This data drives ROM promotion scoring for frequently-selected tributary patterns.

---

## French Braid Model

Every ATG response weaves three strands simultaneously:
- **Explicit strand** — what you asked for
- **Meta strand** — what you’re actually trying to solve
- **Adjacent-primitive strand** — what the OS knows belongs in the conversation

Instead of linear next-steps, the user gets braided tributaries — every answer spawns an interwoven set of next moves that keep ROM, RAM, and the current JTBD in the same plait.

---

## Implementation Target

- **File:** `arcs-v9/src/lib/atg.ts`
- **Hook:** append `tributaries` field to `POST /api/compass` response
- **UI:** render as pill chips below the main compass answer in `/dashboard`
- **Status:** P0 backlog — not yet built (see `arcs-v9` CLAUDE.md)

---

## Cross-Links

- **Upstream:** HOLD/REJECT gate (`specs/hold-reject-validation-gate.md`)
- **Upstream:** `arcs-v9` [FLOW] Compass → DEWY (#4)
- **Downstream:** DEWY Y-layer yield signal
- **Downstream:** RCS (ROM promotion scoring) — pattern extraction from selected tributaries
- **JTBD:** ATG-01, ATG-02, ATG-03 in `jtbd/jtbd-master-map.md`
