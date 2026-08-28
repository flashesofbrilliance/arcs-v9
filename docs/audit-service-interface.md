# Audit Service Interface (FastAPI)

> **Status:** SPECCED — not built yet. Read alongside `src/lib/audit-client.ts` and
> `src/lib/audit-translator.ts`.
>
> **Role:** the Python service the compass route calls to run the operator pipeline on
> a compass receipt. It's the seam that lets Path A enrich the LLM output with operator
> audit without touching the core compass route.

---

## Why FastAPI (and not the existing SAGE_URL pattern alone)

The existing `SAGE_URL` seam calls a single endpoint for SAGE and injects it as context.
Path A needs four operators (SAGE → LAB → BAR → KINTSUGI), and the **translation from
compass receipt to operator primitives happens once and is consumed by all four**.

A small FastAPI service gives you:

- One translator, running in Python next to the operators, so the primitives are native
  dataclass instances, not JSON round-tripped from TypeScript.
- Four endpoints that each run the relevant operator on those primitives.
- A place to persist the audit trail and the benchmark pairs without touching the compass route.
- The ability to run post-hoc audits (e.g. re-audit a stored receipt) without involving the
  live compass route at all.

The translator lives in the audit service, not on the TS side. The TS `audit-translator.ts`
is the TypeScript mirror — needed if you ever want to run the translator on the TS side or
validate equivalence. For Path A, the canonical translator is the Python one.

---

## Where it lives

```
operators/audit_service/
├── __init__.py          # package marker
├── main.py              # FastAPI app, 4 audit endpoints + health
├── translator.py        # compass receipt → operator primitives (canonical translator)
├── service.py           # runs the operator pipeline, builds audit responses
├── persistence.py       # writes audit trace + benchmark pair to store
└── requirements.txt     # fastapi, uvicorn, pydantic, numpy, anthropic(?)
```

The service imports from the existing `operators/` tree — it's a consumer of the operator
library, not a new operator.

---

## Process model

```
python operators/audit_service/main.py
```

Usually one process. For Path A, living next to the compass route or deployed as a small
sidecar both work. The compass route calls it via `AUDIT_SERVICE_URL`.

---

## API surface

### Health

```
GET /api/audit/health
→ { "ok": true, "operators": ["SAGE", "LAB", "BAR", "KINTSUGI"], "version": "1.0.0" }
```

Used by the compass route to confirm the service is reachable before calling the audit
endpoints. Also lets you confirm the operator set a given deployment has.

### SAGE

```
POST /api/audit/sage
Body:
{
  "primitives": { ... OperatorPrimitives ... },
  "llmOutput": { ... ReceiptJSON ... },
  "traceId": "uuid",
  "sessionVersion": 1
}

Response (200):
{
  "ok": true,
  "operator": "SAGE",
  "output": {
    "nci_score": 82.0,
    "pci_score": 71.0,
    "hci_score": 78.0,
    "signal_classification": "strong_signal",
    "axioms": {
      "clarity_before_curvature": "YES",
      "agency_over_automation": "YES",
      "minimum_steps_to_coherence": "YES",
      "kairos_over_neuroticism": "TENSION",
      "alignment_score": 0.875
    },
    "verdict": "STRONG",
    "kinematic_summary": { ... },
    "five_derivatives": { ... },
    "somatic": { ... },
    "coherence_law_score": 0.6173,
    "is_satoshi": true,
    "nci_grade": "RELEASE_READY"
  },
  "primitivesSent": { ... },
  "latencyMs": 42,
  "fidelity": {
    "somatic": "default",
    "hci": "proxy",
    "axioms": "llm_derived"
  }
}

Response (503 — audit ran but operator blocked / degraded):
{
  "ok": false,
  "operator": "SAGE",
  "output": {},
  "failureReason": "CSS below 0.65 — operator halted",
  "primitivesSent": { ... },
  "latencyMs": 38,
  "fidelity": { ... }
}
```

The `ok: false` case is real — SAGE will halt on low CSS as we saw in the CLI runs.
The audit service reports that honestly rather than fabricating a result.

### LAB

```
POST /api/audit/lab
Body: same shape
Response:
{
  "ok": true,
  "operator": "LAB",
  "output": {
    "lab_threat_level": "LOW",
    "lab_recommendation": "PROCEED",
    "loki": { challenge_statement, failure_modes, hidden_assumptions, worst_case_scenario, loki_confidence, can_be_dismissed, dismissal_argument, threat_score },
    "advisors": [ { advisor_archetype, domain, stance, reasoning, confidence } ... ],
    "bayesian": { prior_confidence, loki_evidence_weight, advisor_consensus_weight, posterior_confidence, belief_shift, proceed_recommended },
    "lab_summary": "..."
  },
  "primitivesSent": { ... },
  "latencyMs": 51,
  "fidelity": { ... }
}
```

### BAR

```
POST /api/audit/bar
Body: same shape
Response:
{
  "ok": true,
  "operator": "BAR",
  "output": {
    "bar_verdict": "STRONG",
    "baseline": { floor_scenario, floor_nci, floor_is_acceptable, floor_confidence, recovery_path },
    "asymmetry": { upside_scenario, downside_scenario, upside_magnitude, downside_magnitude, asymmetry_ratio, bet_quality, kelly_fraction },
    "ruin": { ruin_detected, ruin_scenario, ruin_probability, irreversibility_score, court_trigger, mitigation },
    "bar_summary": "..."
  },
  "primitivesSent": { ... },
  "latencyMs": 47,
  "fidelity": { ... }
}
```

### KINTSUGI

```
POST /api/audit/kintsugi
Body: same shape
Response:
{
  "ok": true,
  "operator": "KINTSUGI",
  "output": {
    "pathogens": [ { pathogen_type, severity, description, evidence, confidence } ... ],
    "is_healthy": false,
    "repaired": true,
    "golden_seams": [ { seam_id, seam_type, trust_discount, description, repair_description } ... ],
    "kintsugi_repaired": true,
    "kintsugi_repair_count": 2,
    "kintsugi_trust_discount": 0.18,
    "kintsugi_seam_ids": ["s1", "s2"],
    "kintsugi_repaired_at": 1787804237.03,
    "kintsugi_version": "v9.0-phase4",
    "nci_score": 78.0,
    "nci_pre_repair": 95.0
  },
  "primitivesSent": { ... },
  "latencyMs": 33,
  "fidelity": { ... }
}
```

KINTSUGI's `output` is a `KintsugiDiagnosis`-shaped dict, not a `CoherenceReceipt`. It
includes the repaired receipt and the trust discount so the compass route can persist the
audit trail with the trust-adjusted NCI.

---

## Translator: compass receipt → operator primitives

The canonical translator lives in `operators/audit_service/translator.py`. It takes the
compass context (what the TS client sends: question + horizon + stakes + prep + LLM output)
and produces `OperatorPrimitives`.

This is the same contract as `src/lib/audit-translator.ts`, but native Python:

```python
def translate_compass_receipt(
    question: str,
    horizon: str,
    stakes: str,
    clarity_mode: str,
    door_class: str,
    llm_output: dict,
    prep: dict | None = None,
) -> OperatorPrimitives:
    ...
```

The translator is responsible for:

- `CoherenceSignal` (with `signal_proxy` from horizon/stakes/mode/door/coherence/nci)
- `FATEDReasoning` (from `llm_output.reasoning.fated` when present, fallback structure otherwise)
- `AxiomCheck` (derived from `llm_output.meta.macro_tags` + `reasoning.court` verdicts, or default TENSION)
- `SomaticReading` (defaults unless the intake adds somatic self-report — see the `somatic_prompt` hook)
- `hci_score` + `hci_source` (proxy from `coherence_pct`, or user self-report)
- `pci_score` (computed from the signal proxy)
- `irreversibility` (from stakes + door_class)
- `next_action` (from `true_north`)
- `phase_id` (mapped from horizon)
- `signal_classification` (mapped from coherence + nci + macro tags)

The `fidelity` markers are carried in the audit response, not in the primitives themselves.

---

## Service layer

`service.py` runs the operator pipeline on the translated primitives and builds the audit
response.

```python
def run_sage(primitives: OperatorPrimitives, llm_output: dict) -> SageAuditResult:
    sage = SAGEOperator()
    receipt = sage.run(
        signal=primitives.signal,
        fated=primitives.fated,
        axioms=primitives.axioms,
        somatic=primitives.somatic,
        hci_score=primitives.hci_score,
        phase_id=primitives.phase_id,
        next_action=primitives.next_action,
        on_purpose=primitives.on_purpose,
        irreversibility=primitives.irreversibility,
    )
    return SageAuditResult.from_receipt(receipt, primitives.fidelity)

def run_lab(primitives: OperatorPrimitives, llm_output: dict) -> LabAuditResult:
    lab = LABOperator()
    sage_receipt = SageAuditResult.to_sage_receipt(primitives, llm_output)
    assessment = lab.run(sage_receipt, primitives.phase_id)
    return LabAuditResult.from_assessment(assessment, primitives.fidelity)

def run_bar(primitives: OperatorPrimitives, llm_output: dict) -> BarAuditResult:
    bar = BAROperator()
    sage_receipt = SageAuditResult.to_sage_receipt(primitives, llm_output)
    lab_assessment = LabAuditResult.to_lab_assessment(primitives, llm_output)
    assessment = bar.run(sage_receipt, lab_assessment, primitives.phase_id)
    return BarAuditResult.from_assessment(assessment, primitives.fidelity)

def run_kintsugi(primitives: OperatorPrimitives, llm_output: dict) -> KintsugiAuditResult:
    ks = KintsugiService()
    receipt_dict = build_receipt_dict_for_kintsugi(primitives, llm_output)
    diagnosis = ks.diagnose(receipt_dict)
    if not diagnosis.is_healthy:
        diagnosis = ks.repair(diagnosis, receipt_dict)
    return KintsugiAuditResult.from_diagnosis(diagnosis, primitives.fidelity)
```

Note the LAB and BAR calls need a SAGE receipt and (for BAR) a LAB assessment. The audit
service constructs these from the primitives + LLM output, not by re-running SAGE/LAB in the
same call. BAR's `run()` takes a SAGE `CoherenceReceipt` + a LAB `LABAssessment` — both are
constructed here.

---

## Persistence

`persistence.py` writes two things per compass run that hits the audit service:

1. **Audit trace** — the structured operator outputs + latencies + fidelity, associated with
   the receipt ID and trace ID. Never returned to the client.
2. **Benchmark pair** — a paired record of LLM output + audit trace + operator inputs, for
   the Path A → Path B evidence collection. See the benchmark plan.

Storage is initially whatever's simplest and available — a JSONL file, a SQLite table, or the
existing Prisma schema if there's a clean home for it. The benchmark plan is agnostic on store;
pick the simplest thing that lets you query pairs by date/operator/fidelity for review.

---

## Error model

- **Service unreachable:** compass route skips audit (same as SAGE_URL today). The TS client
  catches and logs. No user-visible impact.
- **Endpoint returns non-200:** logged by the TS client, that operator's `ok: false` with
  `failureReason`. The route continues with the other operators.
- **Operator halts internally:** SAGE returns `ok: false` with a CSS-below-threshold reason.
  The compass route still gets the LLM output; the audit just records that SAGE declined.
- **Translator produces defaults:** fidelity markers catch this. The audit response is honest
  about input fidelity. The operator runs on defaults and returns something — it's just lower
  confidence.

The audit layer never throws to the compass route. That's the contract.

---

## Integration with the compass route

The compass route gains, after the LLM inference completes and before persisting:

```typescript
// AFTER llmOutput is parsed and the receipt is about to be created:

const auditTrace = await runAudit(
  {
    question,
    horizon: activeHorizon,
    stakes: activeStakes,
    clarityMode,
    doorClass: door,
    llmOutput: parsed,
    prep,
    sessionVersion,
    traceId: crypto.randomUUID(),
  },
  (msg, meta) => console.log(msg, meta),
)

// Inject advisory block into context only if there's something to inject and
// you want a follow-up enrichment pass (optional — see note below).
// This is the same shape as sageBlock today — advisory, not authoritative.

// Persist auditTrace to an invisible audit row, never return to client.
// This is the benchmark pair source.
```

**One design choice worth flagging:** the existing SAGE_URL seam injects `sageBlock` into the
LLM context *before* inference, so the LLM sees the SAGE signal. For the full audit layer, you
have a choice:

1. **Inject all four advisory blocks before inference** (like SAGE_URL does for SAGE). The LLM
   sees SAGE/LAB/BAR/KINTSUGI output and can incorporate it. More context, more expensive.
2. **Inject only before inference if you want enrichment; otherwise just persist the audit trail
   after inference.** Less context cost, less LLM enrichment, but the audit still runs and the
   benchmark pair still accumulates.

Path A doesn't require injection. The audit layer's primary value is the structured audit trail
+ benchmark pairs, not necessarily LLM context enrichment. Injection is an enhancement, not the
core move. Start with post-inference persistence; add pre-inference injection if you want the
enrichment and the context budget supports it.

---

## What's NOT in this service

- **No LLM calls.** The audit service runs the operators, not the LLM. It's the operator side
  of the comparison, not another LLM endpoint.
- **No user-facing output.** Everything here is internal. The client never sees audit fields.
- **No blocking.** The compass route proceeds regardless of audit state.
- **No Path C commitment.** Running the audit service alongside the LLM doesn't commit you to
  replacing the LLM. It generates the comparison data. Path C is a later, separate decision.

---

## Next steps (in order)

1. Build the FastAPI service skeleton: `main.py` with health + 4 audit endpoints, returning
   the shapes above. No real operator calls yet — stub the outputs so the TS client can target
   the contract.
2. Wire `translator.py` — the canonical Python translator. Test it on a sample compass receipt.
3. Wire `service.py` to run the real operators on the translated primitives.
4. Wire `persistence.py` to write the audit trace + benchmark pair.
5. Wire the compass route to call the audit service and persist the trace (post-inference first).
6. Decide on pre-inference injection (optional enhancement).
7. Run the benchmark cadence from the plan.
