# Audit Translator Validation — Protocol + Gap Register

> **Status:** PROTOCOL WRITTEN — NOT RUN (waits for DB).
> **Purpose:** a reproducible validation pass over `translateCompassReceipt`:
> run 5–10 real compass receipts through the translator, diff the output
> against the DB primitives, and log discrepancies. Read alongside
> `src/lib/audit-translator.ts` and `docs/operator-audit-thread-state.md`
> (Task 7 output).

---

## What this validates

The translator (`translateCompassReceipt`) sits between the compass route's
parsed LLM output + request body and the Python operator pipeline's
`OperatorPrimitives`. It's the canonical TS→Python bridge for the audit layer.

This validation asks two questions:
1. **Shape contract:** does every field the translator reads from `llmOutput`
   exist in the actual Receipt model/PRISMA schema / JSONL store?
2. **Fidelity:** when we can derive a field from the DB (not just the LLM
   output), does the translator produce the same value?

---

## Inputs (per receipt)

For each receipt in the sample, pull:
- `question`, `horizon`, `stakes`, `clarityMode`, `doorClass` — request body
- `llmOutput` — parsed Claude L0–L5 JSON (what the route builds)
- DB-derived fields where available — e.g. `coherence_pct`, `nci_score`,
  `macro_tags`, `reasoning.geometry.macros_on/off`, `rawResponse`

---

## Two-path `llmOutput` extraction

The translator reads `llmOutput` from two possible sources depending on how
the receipt is stored. Validate both paths:

### Path A — direct LLM output dict (current compass route)
The route builds `llmOutput` inline from the Claude response. The translator
reads fields like `out.coherence_pct`, `out.nci_score`, `out.true_north`,
`out.reasoning?.fated`, `out.meta?.macro_tags`.

**Check:** every field the translator reads (`coherence_pct`, `nci_score`,
`true_north`, `reasoning.fated.*`, `reasoning.court`, `reasoning.geometry`,
`meta.macro_tags`, `is_satoshi`) exists on the actual parsed object for each
receipt in the sample.

### Path B — DB / JSONL retrieval (future receipt re-audit)
When the audit service re-audits a stored receipt, `llmOutput` comes from the
stored Receipt record (PRISMA `rawResponse` JSON field or JSONL `llmOutput`).
The translator must handle both shapes identically.

**Check:** the stored shape preserves the fields the translator needs. If
`rawResponse` is the canonical storage, verify `macro_tags`, `reasoning.court`,
`reasoning.fated` survive the round-trip.

---

## Fidelity check checklist (per receipt)

For each receipt, for each field the translator derives:

| Field | Source | Check |
|---|---|---|
| `signalProxy` | horizon/stakes/door/clarity/coherence/nci/irreversibility | Does the proxy vector match a manual recomputation from the inputs? |
| `fated` | `llmOutput.reasoning.fated` or `fatedFromQuestionAndTrueNorth` fallback | When `reasoning.fated` is present, does the translator use it (not the fallback)? |
| `axioms` | `deriveAxiomsFromLlm` from `macro_tags` + `court` | Are the four axiom values derivable from the stored `macro_tags` + `court` verdicts? Re-derive manually and compare. |
| `somatic` | ALWAYS `SOMATIC_DEFAULT` | Source should be `"default"` unless somatic self-report is wired. Flag if the translator ever produces non-default somatic without a wire. |
| `hci_score` | `Math.round(coherence_pct ?? 50)` | Proxied from coherence. Verify `hci_source = "proxy"`. |
| `pci_score` | `computePciProxy(signalProxy)` | Recompute manually from the proxy vector and compare. |
| `irreversibility` | `irreversibilityFromContext(stakes, doorClass)` | Re-derive manually and compare. |
| `phaseId` | `horizonToPhaseId(horizon)` | Does the phase ID match a manual mapping from the DB `horizon` value? |
| `signalClassification` | `classifySignal(coherence, nci, macro_tags)` | Re-derive manually and compare. |

---

## Discrepancy log schema

Each discrepancy logged:

```json
{
  "receipt_id": "string",
  "field": "string",            // e.g. "axioms.clarity_before_curvature"
  "translator_value": "any",
  "expected_value": "any",      // from manual derivation or DB ground truth
  "severity": "MEDIUM" | "LOW" | "INFO",
  "note": "string"              // why it differs, if known
}
```

**Severity guidance:**
- **MEDIUM** — the translator produces a different value from what the inputs
  support, and the difference is material to an operator (e.g. axiom value,
  phase ID, signal classification).
- **LOW** — the translator makes a defensible choice that differs from a naive
  expectation, but the choice is documented (e.g. `fated` fallback when
  `reasoning.fated` is absent).
- **INFO** — a fidelity observation, not a discrepancy (e.g. "somatic is
  default because no self-report wire exists").

---

## Gap register (C-1 through C-7)

From Task 7's swarm findings. These are fidelity/data-availability gaps, not
translator bugs. The translator behaves correctly given the inputs it receives;
the gaps are about what inputs are available.

| Gap | Severity | What it is | Fix owner |
|---|---|---|---|
| **C-1** | MEDIUM | `geometry.macros_on/off` only in `rawResponse`. Older receipts without `rawResponse` lose this data, reducing axiom derivation fidelity. | Storage layer — always store `rawResponse` or add JSONL fields for macros_on/off. |
| **C-2** | LOW | `is_satoshi` in `ReceiptJSON` but never consumed by the translator. | Translator — either consume it or remove from the interface. |
| **C-3** | HIGH | Somatic layer entirely default — no DB column, no intake wire. `somatic.source` is always `"default"`. | Intake UX + DB column + translator wire. See E1 in operator-audit-experiments.md. |
| **C-4** | MEDIUM | HCI always proxy — no user self-report in DB. HCI and PCI become correlated (both derived from coherence). | Intake UX + DB column + translator wire. Same root as C-3. |
| **C-5** | MEDIUM | **RESOLVED.** DB `horizon` enum (`TODAY|WEEK|QUARTER|YEAR|YEARS`) differs from translator's expected enum (`TODAY|THIS_WEEK|THIS_MONTH|THIS_QUARTER|ONE_TO_THREE_YEARS|LONGER`). Mapping was required. | **RESOLVED** — `horizonToValue()` + `horizonToPhaseId()` in `audit-translator.ts` already map the DB enum to the translator's expected values. No separate mapping layer needed. The translator reads DB `horizon` and maps it inline. Confirmed in thread-state (E2 → RESOLVED). |
| **C-6** | LOW | `prep` fields accepted but ignored by the translator. | Translator — either use `prep.confidence`/`prep.adversarialInput` or document the ignore explicitly. |
| **C-7** | LOW | No `reasoning.geometry` stored as separate DB columns. `macro_tags` captures which macros were on, but not the full geometry structure. | Storage layer — decide whether geometry detail is worth separate columns or JSONL fields. |

**Bottom line (from Task 7):** No translator bugs. All fidelity concerns are
DB/storage-layer data availability constraints. The translator is sound — it
derives what it can from what it's given, and flags low-fidelity fields with
source markers.

---

## Running it

```bash
# When DB is available:
python scripts/audit_translator_validate.py \
  --receipt-ids r1 r2 r3 r4 r5 \
  --output _STATE/audit-translator-validation-20260827.json
```

The script:
1. Loads each receipt (from DB or JSONL).
2. Runs `translateCompassReceipt` with the receipt's question/horizon/stakes/
   clarityMode/doorClass/llmOutput.
3. For each field in the fidelity checklist, recomputes the expected value
   from the available inputs.
4. Emits a discrepancy log + a summary (fields checked, discrepancies by
   severity, gaps referenced).

**Not yet run** — the script is protocol-only. Writing it is Phase 1 item 17
(from thread-state build backlog), blocked on DB availability.
