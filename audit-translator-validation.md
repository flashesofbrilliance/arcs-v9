# Audit Translator Contract Validation — ARCS v9

**Date:** 2026-08-27  
**No DB available** — shape contract + validation protocol + gap analysis only.

---

## Part A — Shape Contract Confirmation

### A.1: ReceiptJSON field coverage vs. translator reads

| ReceiptJSON field | Translator read? | Fallback if missing | Notes |
|---|---|---|---|
| `coherence_pct` | **YES** — `Number(out.coherence_pct ?? 50)` → signalProxy[9], hci_score, classifySignal | Default `50` | Pulled 3×: signalProxy, HCI, classification |
| `nci_score` | **YES** — `Number(out.nci_score ?? 50)` → signalProxy[10], classifySignal | Default `50` | Pulled 2×: signalProxy, classification |
| `true_north` | **YES** — `out.true_north as string` → nextAction fallback, fatedFromQuestionAndTrueNorth | `"Review the decision before acting."` | nextAction = `true_north || fallback` |
| `reasoning.fated` | **YES** — `out.reasoning?.fated` → FATED construct (facts/assumptions/tradeoffs/emotions/direction) | `fatedFromQuestionAndTrueNorth(input.question, true_north)` | Each sub-field has `?? ""` so missing sub-fields → empty string, not crash |
| `reasoning.court` | **YES** — `courtVerdicts` → `deriveAxiomsFromLlm` (hasCourtTension check) | `[]` (empty array) | `c.verdict === "TENSION"` check is safe on empty |
| `reasoning.geometry.macros_on` | **YES** — via `macroTags` derived from `out.meta?.macro_tags` (NOT from geometry.macros_on directly) | `[]` | ⚠️ **See gap G-1 below** |
| `meta.macro_tags` | **YES** — `out.meta?.macro_tags as string[] \| undefined ?? []` → deriveAxiomsFromLlm + classifySignal | `[]` | Used for engagedRisk (BAR/KKL) + engagedNoto (NOTOMATION) |

### A.2: ReceiptJSON fields NOT read by translator (present in type but ignored)

| Field | Status |
|---|---|
| `is_satoshi` | **NOT READ** by translateCompassReceipt. Present in ReceiptJSON but never referenced in the TS function body. |

### A.3: Request-side field coverage

| Request field | Source in translator input | Fallback / computation | Notes |
|---|---|---|---|
| `question` | `input.question.trim().slice(0, 200)` → signal.label + fatedFromQuestionAndTrueNorth | None (required) | Truncated to 200 chars for label |
| `horizon` | `input.horizon` → horizonToValue (signalProxy[0-2]), horizonToPhaseId (phaseId), deriveAxioms (kairos_over_neuroticism) | None (required) | Maps to phase_1/phase_2/phase_3 |
| `stakes` | `input.stakes` → stakesToValue (signalProxy[3-5]), irreversibilityFromContext, classifySignal is NOT using stakes directly | None (required) | HIGH/MEDIUM/LOW |
| `clarityMode` | `input.clarityMode` → clarityVal in signalProxy[8], deriveAxioms (minimum_steps_to_coherence) | None (required) | SIMPLE/RICH/DEEP |
| `doorClass` | `input.doorClass` → doorA/doorB in signalProxy[6-7], irreversibilityFromContext | None (required) | ONE_WAY/TWO_WAY |
| `prep?.confidence` | **NOT READ** by translateCompassReceipt body | N/A — passed through to input type but ignored | The function signature accepts `prep` but never destructures it |
| `prep?.adversarialInput` | **NOT READ** | N/A | Same as above |

### A.4: Summary — what's covered vs. gaps

**ReceiptJSON fully covers all translator reads** — every field the translator pulls from `llmOutput` exists in ReceiptJSON, with safe defaults (?? fallbacks) for every access path. No silent-undefined risk from the ReceiptJSON side.

**Request-side is complete** — question/horizon/stakes/clarityMode/doorClass are all consumed. The only unused request fields are `prep?.confidence` and `prep?.adversarialInput`, which are accepted by the type signature but not read. This is intentional (prep is "passed through" per the docs).

---

## Part B — Real-Receipt Validation Protocol (when DB is available)

### B.1: Prisma query to pull N receipts

```ts
// Pull receipts with all fields the translator needs, plus rawResponse for LLM output reconstruction
const receipts = await prisma.receipt.findMany({
  where: { /* optional filters: validationState: "PASS", surface: "ORIENT" */ },
  orderBy: { createdAt: "desc" },
  take: N,
  select: {
    id: true,
    receiptId: true,
    decision: true,           // legacy question
    sharpQuestion: true,      // canonical question
    horizon: true,            // schema canonical (TODAY|WEEK|QUARTER|YEAR|YEARS)
    window: true,             // legacy (THIS_WEEK etc.)
    stakes: true,
    doorClass: true,
    clarityMode: true,
    trueNorth: true,
    coherencePct: true,
    nciScore: true,
    isSatoshi: true,
    fated: true,              // JSON string
    court: true,              // JSON string
    macroTags: true,          // JSON string
    rawResponse: true,        // full Claude JSON (preferred)
    meta: true,               // if stored separately
    createdAt: true,
    sessionId: true,
    parentId: true,
  },
})
```

**Which fields to select:** Everything the translator needs from both the request side (horizon, stakes, doorClass, clarityMode, question) and the llmOutput side (coherencePct, nciScore, trueNorth, fated, court, macroTags, rawResponse).

### B.2: Map DB columns → translator input

```ts
function receiptToTranslatorInput(r: PrismaReceipt): TranslatorInput {
  // Question: prefer sharpQuestion (canonical), fall back to decision (legacy)
  const question = r.sharpQuestion?.trim() || r.decision.trim()

  // Horizon: schema canonical `horizon` (TODAY|WEEK|QUARTER|YEAR|YEARS)
  // → translator expects TODAY|THIS_WEEK|THIS_MONTH|THIS_QUARTER|ONE_TO_THREE_YEARS|LONGER
  // Need a mapping layer if DB stores compact forms
  const horizon = mapDbHorizonToTranslatorHorizon(r.horizon ?? r.window)

  // Stakes: DB stores LOW|MEDIUM|HIGH|EXISTENTIAL
  // Translator's stakesToValue handles LOW/MEDIUM/HIGH; EXISTENTIAL → treat as HIGH
  const stakes = r.stakes === "EXISTENTIAL" ? "HIGH" : r.stakes ?? "MEDIUM"

  // doorClass, clarityMode: direct pass-through (DB stores same enum values)
  const doorClass = r.doorClass ?? "TWO_WAY"  // DB allows null; translator requires string
  const clarityMode = r.clarityMode ?? "SIMPLE"

  return { question, horizon, stakes, clarityMode, doorClass }
}
```

**Critical mapping concerns:**
- **Horizon normalization:** DB stores `horizon` as `TODAY|WEEK|QUARTER|YEAR|YEARS` but translator's `horizonToValue` and `horizonToPhaseId` expect `TODAY|THIS_WEEK|THIS_MONTH|THIS_QUARTER|ONE_TO_THREE_YEARS|LONGER`. A mapping step is REQUIRED or the signalProxy and phaseId will be wrong.
- **Stakes normalization:** DB allows `EXISTENTIAL` which translator doesn't handle — map to HIGH.
- **doorClass null:** DB allows null; translator requires a string. Default to TWO_WAY if null (conservative).

### B.3: Extract llmOutput (ReceiptJSON) from Prisma Receipt

**Preferred path — rawResponse:**

```ts
function extractReceiptJsonFromRawResponse(r: PrismaReceipt): ReceiptJSON {
  if (!r.rawResponse) return {}  // empty → all defaults trigger
  const parsed = JSON.parse(r.rawResponse)
  return {
    coherence_pct: parsed.coherence_pct ?? parsed.coherencePct,
    nci_score: parsed.nci_score ?? parsed.nciScore,
    is_satoshi: parsed.is_satoshi ?? parsed.isSatoshi,
    true_north: parsed.true_north ?? parsed.trueNorth,
    reasoning: {
      fated: parsed.reasoning?.fated ?? parseFatedJson(r.fated),
      court: parsed.reasoning?.court ?? parseCourtJson(r.court),
      geometry: parsed.reasoning?.geometry ?? { macros_on: [], macros_off: [] },
    },
    meta: {
      macro_tags: parsed.meta?.macro_tags ?? parseMacroTagsJson(r.macroTags),
    },
  }
}
```

**Fallback path — reconstruct from stored fields:**

If `rawResponse` is absent (older receipts), reconstruct from individual columns:

```ts
function reconstructReceiptJson(r: PrismaReceipt): ReceiptJSON {
  return {
    coherence_pct: r.coherencePct,
    nci_score: r.nciScore,
    true_north: r.trueNorth,
    reasoning: {
      fated: r.fated ? JSON.parse(r.fated) : undefined,
      court: r.court ? JSON.parse(r.court) : undefined,
      geometry: { macros_on: [], macros_off: [] },  // NOT stored separately
    },
    meta: {
      macro_tags: r.macroTags ? JSON.parse(r.macroTags) : [],
    },
  }
}
```

### B.4: Run translateCompassReceipt for each receipt

```ts
for (const r of receipts) {
  const input = receiptToTranslatorInput(r)
  const llmOutput = extractReceiptJsonFromRawResponse(r)  // or reconstructReceiptJson(r)
  const primitives = translateCompassReceipt({ ...input, llmOutput })
  // Record primitives + fidelity markers
}
```

### B.5: What to check (fidelity profile)

For each receipt, record:

| Check | What "hit fallback" looks like |
|---|---|
| **FATED source** | `fated.facts` starts with `"Decision context:"` → fatedFromQuestionAndTrueNorth triggered (LLM's reasoning.fated absent) |
| **Axiom source** | `axioms.source === "default"` (all TENSION) → neither BAR/KKL macro nor NOTOMATION in macro_tags, no court tension |
| **Somatic source** | Always `"default"` — no DB column for somatic self-report → SOMATIC_DEFAULT always used |
| **HCI source** | Always `"proxy"` — no user self-report in DB → proxied from coherence_pct |
| **signalClassification** | Check if classification is reasonable given coherence_pct/nci_score. If both are default 50 → "decelerating" |
| **nextAction** | Falls back to `"Review the decision before acting."` if true_north is empty/null |
| **Horizon mapping** | If DB horizon couldn't be mapped, phaseId might be wrong (everything → phase_3) |
| **Court verdicts** | If court JSON is stored but empty array → hasCourtTension = false (no impact on axioms) |

### B.6: Discrepancy log shape

```ts
interface DiscrepancyLogEntry {
  receiptId: string
  createdAt: string
  // Input-side checks
  horizonRaw: string       // DB value before mapping
  horizonMapped: string    // translator value after mapping
  horizonMappedCorrectly: boolean
  stakesRaw: string
  stakesMapped: string
  doorClassRaw: string | null
  doorClassDefaulted: boolean  // true if DB null → defaulted to TWO_WAY
  questionSource: "sharpQuestion" | "decision"  // which DB field supplied the question
  // LLM output checks
  rawResponsePresent: boolean
  llmOutputReconstructed: boolean  // true if rawResponse absent → used column reconstruction
  coherencePctFromDb: number | null
  coherencePctFromRaw: number | null
  nciScoreFromDb: number
  nciScoreFromRaw: number | null
  // Fallback triggers
  fatedFellBack: boolean           // true = fatedFromQuestionAndTrueNorth used
  axiomsAllTension: boolean        // true = all four axioms are TENSION with source "default"
  somaticAlwaysDefault: true       // always true (no DB column)
  hciAlwaysProxy: true             // always true (no DB column)
  nextActionFellBack: boolean      // true = "Review the decision before acting."
  signalClassification: string
  coherencePctUsed: number         // what was actually fed to the translator
  nciScoreUsed: number
  // Output primitives (sample)
  phaseId: string
  signalProxy: number[]
  irreversibility: number
  hci_score: number
  pci_score: number
  axiomAlignment: number           // from _axiom_alignment in translator.py
  witnessScore: number             // from _witness_score in translator.py
}
```

---

## Part C — Known Gaps / Concerns

### C-1: Geometry macros_on NOT read from ReceiptJSON reliably

**Severity: MEDIUM**

`deriveAxiomsFromLlm` reads macro tags from `out.meta?.macro_tags` to determine `engagedRisk` (BAR/KKL presence) and `engagedNoto` (NOTOMATION presence). It does **NOT** read `out.reasoning?.geometry?.macacros_on` despite that field existing in both the ReceiptJSON type and the schema.

The DB stores `macroTags` as a JSON string column (`macroTags String @default("[]")`), which maps to `meta.macro_tags`. So the translator CAN get macro tags from the DB — but the `geometry.macros_on/off` fields (which give the full picture of which macros were considered, not just which fired) are NOT stored as separate columns in the DB and would only be available inside `rawResponse`.

**Impact:** If `rawResponse` is absent (older receipts), you lose the `geometry.macros_on/off` data. The translator falls back to macro_tags only, which may undercount engaged macros. The axiom derivation is still functional but less informed.

**Fix path:** Add `geometry_macros_on` and `geometry_macros_off` JSON columns to Receipt, or ensure `rawResponse` is always stored.

### C-2: is_satoshi is in ReceiptJSON but never consumed

**Severity: LOW**

`is_satoshi` is defined in ReceiptJSON and stored in the DB (`isSatoshi Boolean @default(false)`), but `translateCompassReceipt` never reads it. It's not used in signalProxy, classification, axioms, or any output field. The Python `build_kintsugi_receipt` also doesn't use it (it pulls NCI from `llm_output.get("nci_score", p.get("hci_score", 50.0))`).

**Impact:** Dead field. If the compass pipeline intends `is_satoshi` to affect translation, it's not wired. If it's purely for the UI/brief layer, this is intentional.

### C-3: Somatic layer is entirely default — no DB column exists

**Severity: HIGH (structural)**

The DB has **no somatic self-report column**. The translator hardcodes `SOMATIC_DEFAULT` (phase_tuning=0.55, surge_detection=0.50, feels_right=0.50, that_vibes=0.50, locked_in=0.55, expected_vs_actual=0.50, source="default"). The Python mirror passes these through. The `fidelity` dict in `DecodedPrimitives` always reports `"somatic": "default"`.

The somatic values are mid-range and identical for every receipt. They carry no information about the actual decision. The witness_score computed by `_witness_score` in translator.py will be the same for every receipt (~0.517) since the somatic values are constant.

**Impact:** The somatic layer in the operator pipeline is pure noise for real receipts — it won't discriminate between good and bad decisions. SAGE's kinematic lens, LAB's threat assessment, and BAR's asymmetry analysis all receive the same somatic reading regardless of content.

**Fix path:** Add a `somaticSelfReport` JSON column to Receipt (or a related table), collect the six scores at intake per the commented `somaticPrompt`, and wire the translator to use them when present (setting `somatic.source = "user_self_report"`).

### C-4: HCI is always a proxy — no user self-report in DB

**Severity: MEDIUM**

`hci_score` is always `Math.round(coherence_pct ?? 50)` with `hci_source = "proxy"`. There's no user self-report column for HCI in the DB. The HCI is literally the same as the LLM's coherence_pct (rounded).

**Impact:** HCI and PCI become correlated in a way that may not be meaningful. The HCI-PCI comparison (which BAR uses) is comparing the LLM's self-assessed coherence against a derived proxy of the same number — not an independent human coherence measure.

**Fix path:** Same as C-3 — add a user self-report at intake for HCI (single 0-100 question), store it, and wire the translator to use it when present.

### C-5: Horizon mapping between DB and translator is lossy

**Severity: MEDIUM**

The DB `horizon` enum is: `TODAY | WEEK | QUARTER | YEAR | YEARS`  
The translator's `horizonToValue` expects: `TODAY | THIS_WEEK | THIS_MONTH | THIS_QUARTER | ONE_TO_THREE_YEARS | LONGER`

The DB's `window` (legacy) field uses: `TODAY | THIS_WEEK | THIS_QUARTER | ONE_TO_THREE_YEARS` — which matches the translator's expectations better. But `window` is legacy and `horizon` is canonical.

If you feed `horizon="QUARTER"` directly into the translator, it doesn't match any branch → falls to `0.2` (LONGER/unknown), which is wrong. The phaseId mapping also breaks: `QUARTER` → unknown → phase_3 (correct by coincidence), but `YEAR` → unknown → phase_3 (should be phase_3 anyway, but the signalProxy value is 0.2 instead of 0.3).

**Impact:** Every receipt with `horizon` set to `WEEK`, `QUARTER`, `YEAR`, or `YEARS` gets a wrong signalProxy value and potentially wrong phaseId unless an explicit mapping layer is applied.

**Fix path:** Map DB horizon values explicitly:
```
TODAY → TODAY
WEEK → THIS_WEEK
QUARTER → THIS_QUARTER
YEAR → ONE_TO_THREE_YEARS  (or THIS_YEAR — translator doesn't have THIS_YEAR)
YEARS → LONGER
```

### C-6: `prep` fields accepted but ignored

**Severity: LOW**

The translator's function signature accepts `prep?: { confidence?: string; adversarialInput?: string } | null` but the function body never reads either field. The DB stores `confidence` (Int 1-5) and `adversarialInput` (String) on the `PrepSession` table, linked to Receipt via `prepId`. These could enrich the translation (e.g., confidence could modulate the signal proxy, adversarialInput could populate fated.tradeoffs) but currently don't.

**Impact:** Low — these are "nice to have" enrichments, not required for the translator to function. The prep data is available in the DB but not used.

### C-7: No `reasoning.geometry` stored as separate DB columns

**Severity: LOW**

The ReceiptJSON type includes `reasoning.geometry.macros_on` and `macros_off`, but the DB doesn't have dedicated columns for these. They're only available inside `rawResponse` (the full Claude JSON). If `rawResponse` is null/missing for older receipts, the geometry data is lost, and `deriveAxiomsFromLlm` falls back to macro_tags only.

**Impact:** Older receipts without rawResponse lose the macros_on/off detail. The macro_tags column partially compensates (it captures which macros fired) but doesn't capture which were considered and rejected.

---

## Summary

| Area | Status |
|---|---|
| ReceiptJSON covers all translator reads | ✅ Confirmed — every llmOutput field the translator reads exists in ReceiptJSON |
| Request-side fields all available | ✅ Confirmed — question/horizon/stakes/clarityMode/doorClass all consumed; prep fields accepted but unused (intentional) |
| Somatic layer fidelity | 🔴 HIGH concern — always default, no DB column, no discrimination between receipts |
| HCI fidelity | 🟡 MEDIUM — always proxy from coherence_pct, no independent user measure |
| Horizon DB→translator mapping | 🟡 MEDIUM — enum mismatch requires explicit mapping layer or signalProxy is wrong |
| Geometry macros_on/off availability | 🟡 MEDIUM — only in rawResponse; older receipts lose this data |
| is_satoshi wiring | 🟢 LOW — dead field, not consumed (may be intentional) |
| prep fields usage | 🟢 LOW — available in DB but not wired into translator |
| DB can reconstruct faithful llmOutput | 🟡 CONDITIONAL — only if rawResponse is present; otherwise macro geometry is lost |

**Bottom line:** The translator's shape contract is sound — ReceiptJSON fully covers what it reads. The real-fidelity concerns are all in the DB storage layer: somatic and HCI have no independent data sources (always default/proxy), horizon needs a mapping layer, and geometry detail requires rawResponse. None of these are translator bugs — they're data availability constraints.
