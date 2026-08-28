# Benchmark Collection Plan — Path A → Path B/C evidence

> **Purpose:** define what gets measured, how, and how often, so the operator-vs-LLM
> comparison becomes evidence rather than impression. Read alongside audit-translator.ts
> and the audit service interface spec.

---

## What we're measuring

The compass route produces two structured outputs per run once the audit layer is live:

1. **LLM output** — the Claude L0-L5 JSON (true_north, why, nci_score, coherence_pct,
   reasoning.court, reasoning.geometry, reasoning.fated, meta.macro_tags, tributaries, …)
2. **Operator audit** — SAGE (NCI, PCI, HCI, axioms, signal classification) + LAB (threat,
   recommendation, Loki challenge, Bayesian posterior) + BAR (verdict, floor_nci, asymmetry,
   kelly, ruin) + KINTSUGI (pathogens, repaired, trust discount).

The benchmark isn't "which is better overall." It's **subtask-by-subtask**:

| Subtask | LLM signal | Operator signal | What "better" means |
|---------|-----------|-----------------|---------------------|
| NCI calibration | `nci_score` | SAGE `nci_score` | Which tracks outcome reality / human review better? |
| Axiom compliance | `reasoning.geometry.macros_on` + court verdicts (inferred) | SAGE `axioms` (explicit YES/TENSION/NO) | Does explicit axiom compliance catch violations the LLM missed? |
| Adversarial challenge | `reasoning.advisors.loki_challenge` + `loki_counter` | LAB `loki.challenge_statement` + `loki_threat_score` | Does LAB surface a challenge the LLM's Loki didn't, or a stronger one? |
| Bayesian risk | `reasoning.advisors.bayesian_risk_pct` + rationale | LAB `bayesian.posterior_confidence` + `belief_shift` | Which posterior is better calibrated to outcome? |
| Risk geometry | `reasoning.geometry.reversibility`, `kairos`, `altitude` | BAR `baseline.floor_nci`, `asymmetry.asymmetry_ratio`, `kelly_fraction`, `ruin.ruin_detected` | Does BAR add geometry the LLM's summary didn't surface? Does BAR flag ruin the LLM missed? |
| Receipt integrity | `nci_self_grade` (factual/sources/honesty/action) | KINTSUGI `pathogens` + `trust_discount` | Does KINTSUGI surface incoherence the LLM's self-grade missed? |

The honest framing: "better" isn't a single number. It's a set of side-by-side comparisons
you review periodically and accumulate evidence on.

---

## Comparison mechanics

### 1. Paired output collection (automatic)

Every compass run that hits the audit service produces a paired record:

```
{
  traceId: uuid,
  sessionVersion: number,
  timestamp: iso,
  question: string (truncated/anonymized for storage),
  horizon: string,
  stakes: string,
  clarityMode: string,
  doorClass: string,
  llmOutput: ReceiptJSON,          // the Claude L0-L5 result
  auditTrace: AuditTrace,          // SAGE/LAB/BAR/KINTSUGI outputs + latencies + fidelity
  advisoryBlock: string,           // what got injected into the LLM context
  operatorInputs: OperatorPrimitives, // what was sent to the operators (for reproducibility)
}
```

This record is the comparison unit. Store it in a table/collection dedicated to benchmark
pairs — separate from the user-facing receipt. The user receipt is what the client sees;
the benchmark pair is the internal evidence.

### 2. Fidelity tagging (already in the translator)

The translator marks low-fidelity inputs explicitly:

- `somatic.source: "default"` (vs `"user_self_report"`)
- `hci_source: "proxy"` (vs `"user_self_report"`)
- `axioms.source: "llm_derived"` (vs `"default"`)

This matters for the benchmark review: a comparison where both sides are working from
proxy/default inputs is weaker evidence than one where the user gave real somatic self-report.
Tag each pair with its fidelity profile and weight reviews accordingly.

### 3. Periodic review cadence (human-in-the-loop)

The numbers accumulate automatically. The interpretation is the human work. Suggested cadence:

- **Weekly:** quick scan of the latest N pairs. Look for: operators flagging something the LLM
  didn't; LLM output the operators couldn't parse; operator outputs that look wrong.
- **Monthly:** structured review of a sample (e.g. 30-50 pairs). For each subtask above,
  ask: did the operator add signal? Did the LLM add signal? Did they disagree, and who was
  right when you could tell?
- **Quarterly:** decision about Path B candidates. Which subtask(s) have enough accumulated
  evidence that a specific operator looks better than the LLM for that subtask?

The key discipline: **don't promote a Path B candidate from impression.** Promote from
accumulated paired evidence on the specific subtask, reviewed periodically.

---

## Review protocol for a single pair

When you look at one paired record, the useful questions are:

1. **Did the operator audit surface something the LLM output didn't?**
   - A Loki challenge the LLM's `loki_challenge` didn't include?
   - A BAR asymmetry ratio that reframes the LLM's `geometry.reversibility`?
   - A KINTSUGI pathogen that the LLM's `nci_self_grade.honesty` didn't catch?

2. **Did the LLM output surface something the operator audit missed?**
   - A tributary (meta/challenge/adjacent) the operators have no representation for?
   - A human nuance in `true_north`/`why` that a structured operator output can't capture?

3. **Did they disagree, and on what?**
   - SAGE NCI vs LLM `nci_score` — same ballpark or wide gap?
   - BAR verdict vs LLM `court_verdict` — same direction or tension?
   - LAB recommendation vs LLM `reasoning.advisors.consensus`?

4. **Was the operator input high-fidelity or proxy?**
   - If somatic/HCI are defaults, treat the operator output as lower-confidence evidence.
   - If the user gave real somatic self-report, the operator output is higher-confidence.

5. **Who was right when you can tell?**
   - The hardest question and the one that accumulates the evidence. When a later outcome
     or human review resolves the disagreement, record it. When you can't tell, record that
     too — unresolved disagreement is still data.

---

## Path B candidate promotion criteria

A subtask becomes a Path B replacement candidate when you have:

1. **Accumulated paired evidence** — not 2-3 hand-picked examples, but a reviewed sample
   (size depends on effect size; 30-50 is a starting point for a directional read).
2. **Directional consistency** — the operator outperforms or matches the LLM on that subtask
   across the sample, not just in one or two vivid cases.
3. **No clearly worse cases** — or the worse cases are understood and bounded (e.g. low-fidelity
   input, a specific question type where the operator doesn't apply).
4. **A defined integration shape** — replacing the subtask means knowing exactly what you swap
   out and what you keep. E.g. "replace the LLM's Loki challenge with LAB's, keep the LLM's
   tributaries" is a defined shape; "use the operators more" is not.

Promote selectively. A single operator subtask can become Path B while the rest of the pipeline
stays on the LLM. That's the point of incremental replacement rather than a coordinated swap.

---

## What the benchmark DOESN'T measure (yet)

These are honest gaps, not claims they're unimportant:

- **Outcome reality.** The benchmark compares LLM-vs-operator output, not either against what
  actually happened. Outcome data (did the decision work out? was the NCI well-calibrated in
  hindsight?) is a higher bar and requires the outcome loop to close. That's a later phase.
- **Cost.** If the operator pipeline is cheaper per decision than Claude calls, that's a real
  argument for Path C independent of quality. But cost comparison needs the operators running
  at volume inside the route, which is Path A territory first.
- **User-perceived value.** Whether the extra audit layer improves the user experience is a
  UX question, not a structured-output comparison. It's worth asking, but it's a different
  measurement than the subtask benchmarks.

These are fine to leave for later. The subtask comparison is the thing Path A generates, and
it's the right first dataset.

---

## Flags to watch that would change the plan

- **Operator failures at volume.** If the audit service is flaky or slow at compass scale,
  the advisory layer becomes noise. The existing pattern (skip on failure, never block) handles
  this, but persistent failures would argue for fixing the service before extending it.
- **LLM output that doesn't translate.** If the translator can't extract useful primitives from
  a meaningful fraction of LLM outputs, the audit layer is working from weak input. That's a
  translator problem, not an operator problem — but it limits the benchmark's value.
- **Early directional signal.** If after the first 50-100 pairs the operators are clearly better
  on a subtask, that's a Path B candidate sooner than the cadence suggests. The cadence is a
  minimum, not a gate — strong evidence can move fast.
- **Strong Path C signal across many subtasks.** If the operators start looking better than the
  LLM across most subtasks after accumulated pairs, the balance tips toward Path C. That's the
  end state you said you want — this plan is the on-ramp to the evidence for it.
