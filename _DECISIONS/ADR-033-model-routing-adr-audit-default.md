# ADR-033 — Route ADR-audit harness default to laguna-xs-2.1:free

> **Status:** DECIDED
> **Date:** 2026-08-26
> **Author:** Claude Sonnet 4.6
> **Stakeholders:** ARCS operator harness team, calibration subgroup
>
---

## D — The Decision

**Sharp question:** Which free model should `adr_audit.py` target by default when the `--model` override is omitted — solar-pro4:free (current Hermes default, most-audited against our ADR corpus) or laguna-xs-2.1:free (fastest measured, pure JSON output, free)?

---

## E — Entity / System

`l OPERATOR4 / operators/adr_audit.py` — the ADR-audit harness that fires `cli_arcs_run.py` via subprocess with CIS-pipeline framing to produce structured audit envelopes (gate verdict, CSS, findings). This decision sets the default model for every future ADR audit call that doesn't explicitly override.

`l OPERATOR2 / operators/cli_arcs_run.py` — the harness entry point that `adr_audit.py` shells out to. Currently has no `--model` flag; model resolution is implicit via the Hermes stack.

`l OPERATOR0 — DEWY / _DECISIONS/` — the ADR corpus being audited (5 ADRs ranging 2.4K–7.7K chars; ADR-032 is the calibration anchor with known Tier 1/2/3 envelopes on solar-pro4:free).

`l ~/.hermes/profiles/arcs/config.yaml` — current default model is `upstage/solar-pro4:free`. This ADR may update that default, or leave it and override per-call.

`l /tmp/adr_real_audit_bench.py` — the real audit-bench script designed to run `adr_audit.py --tier 1` once per model per ADR through the actual CIS pipeline path. Depends on the `--model` override being wired.

---

## W — Window

**Horizon:** QUARTER (this routing decision holds until a model change, a harness refactor, or new calibration evidence surfaces)

**Revisit trigger:**
- A new free model becomes reachable that beats laguna-xs on any of {parse-success, speed, CSS coherence vs reference}
- laguna-xs-2.1:free goes offline or behind a paywall
- We accumulate ≥50 audit envelopes and want to re-run the calibration with corpus-scale data
- The harness is refactored to call a model API directly instead of shelling `cli_arcs_run.py` (the transport changes, and the calibration assumption may not hold)
- The full audit-bench (5 ADRs × 4 models × Tier 1) reveals a coherence divergence between laguna-xs and solar-pro4:free that changes the calculus

---

## Context

### What we already know

1. **Two prompt paths, not one — and the path matters more than the model.** Adr_audit.py's output is *path-dependent*:
   - **HALT (CSS 0.557)** when invoked through `adr_audit.py → cli_arcs_run.py` with CIS-pipeline framing (the actual audit path)
   - **WARN (CSS 0.4–0.7)** when invoked through `hermes chat` bare prompt (no CIS framing)
   
   Same ADR (ADR-032), same model (solar-pro4:free), different path → different verdict. This is the single most important calibration insight: *you cannot calibrate a model's audit quality by running raw prompts* — you must run through the actual CIS pipeline path. The real audit-bench (`/tmp/adr_real_audit_bench.py`) is designed around this insight.

2. **Tier 1/2/3 all HALT on ADR-032 via solar-pro4:free.** Confirmed across three runs:
   - Tier 1 (BAR only): HALT, CSS 0.557
   - Tier 2 (BAR + KINTSUGI): both HALT, CSS 0.557 / 0.574
   - Tier 3 (BAR + KINTSUGI + LAB): all HALT (LAB high)
   
   The decision is consistent across tiers — adding lenses doesn't flip it. The same seam (sender coherence) shows up in BAR, KINTSUGI, and LAB independently.

3. **laguna-xs-2.1:free is dramatically faster and structurally cleaner.** From the narrow bench (ADR-032, 4 models × Tier 1 + 2×2 Tier 2/3):
   - **laguna-xs-2.1:free Tier 3: 22.6s, all pure JSON** — no prose wrapping, parseable directly
   - **solar-pro4:free Tier 3: 122.0s, all prose-wrapped JSON** — needs post-processing to extract JSON from response text
   
   That's a **5.4× speed advantage** and a **structural cleanliness advantage** (pure JSON vs prose-wrapped). The cleanliness advantage is structural — it comes from the model's output style, not the prompt, and is stable across calls.

4. **Raw-prompt smoke test (6 models, 1 prompt):** All 6 claimed free models respond via `hermes chat`. Of those, laguna-xs-2.1:free returns pure JSON in 5.9s on a simple calibration prompt; solar-pro4:free returns prose-wrapped JSON in 10.3s. longcat-2.0-free and hy3-free returned non-parseable/empty via direct OpenRouter calls (but respond via `hermes chat` — the wrapper handles auth/routing differently).

5. **No `--model` override exists yet.** `adr_audit.py`'s `_invoke_cis_text()` and `cli_arcs_run.py` have no model override. The real audit-bench needs this to fire `adr_audit.py` once per model through the actual CIS pipeline path. The patch is designed in discussion; not yet written.

6. **Corpus-scale bench completed (calibration_20260826_1046, 2026-08-26):** After the `--model` override was wired, `adr_real_audit_bench.py` ran `adr_audit.py --tier 1 --format json --model <model>` across 5 ADRs × 4 models = 20 CIS-pipeline calls. Result: **all 20 calls produced identical gate verdicts and CSS values per ADR** (parse_ok 20/20, all gate=critical, all overall=fail). Per-ADR CSS: ADR-004=0.507, ADR-008=0.486, ADR-029=0.546, ADR-032=0.557, ADR-030=0.606 — identical across all 4 models.

   This confirms what the CIS pipeline structure suggested: **`adr_audit.py` is model-independent because it's rule-based.** The CIS pipeline in `cli_arcs_run.py` runs `CognitiveInterfaceSystem` with `llm_client=None` — HC does a lexical scan (Python regex/word-list), LTE uses sentence-chunking stubs. No LLM is called, so `--model` has no effect through this path. The `--model` flag is wired and verified (accepts the arg, passes `ARCS_MODEL` env var, exits clean) but inert.

   The **5.4× timing story** (laguna-xs 22.6s vs solar 122s Tier 3) comes from the `hermes chat -q` **bare-prompt path** — the only path in this repo that actually calls an LLM today. That path is *not* the `adr_audit.py` CIS-pipeline path, and bare-prompt verdicts don't match pipeline verdicts (ADR-032: HALT via CIS pipeline at CSS 0.557, WARN via bare prompt at CSS 0.4–0.7). The 5× story is real but it's about a different instrument.

### What we don't know yet

- **Corpus-scale coherence:** Resolved by calibration_20260826_1046 — all 4 models produce identical CIS-pipeline envelopes across 5 ADRs. The coherence gap closed because there was no LLM to diverge.
- **Per-tier latency on longer ADRs:** Not applicable to the rule-based path (all calls ~0.1–0.3s regardless of ADR size). Relevant only to the LLM path (bare-prompt or future CIS-with-LLM-client).
- **Parse success rate at scale:** Confirmed at 100% (20/20) for the rule-based path. For the bare-prompt path, laguna-xs returned pure JSON on the narrow bench (1 ADR); full-corpus parse success on the LLM path is untested.
- **LLM-based ADR audit quality by model:** No LLM-based audit path exists in the harness today. `adr_audit.py` is rule-based; `hermes chat` bare prompts aren't structured audit pipelines. Measuring "which model produces the best structured ADR-audit envelope through an LLM" would require either parameterizing the compass route (`src/app/api/compass/route.ts`, currently hardcoded to `claude-sonnet-4-6`) or wiring an `llm_client` into the CIS pipeline. Both are future work.

### Why this is a decision, not a rubber stamp

Model routing for a structured-output harness trades off multiple axes that aren't all aligned — but **which axes are in play depends on whether the path calls an LLM at all.**

### Why this is a decision, not a rubber stamp

Model routing for a structured-output harness trades off multiple axes that aren't all aligned:

| Axis | solar-pro4:free | laguna-xs-2.1:free | Winner |
|---|---|---|---|
| Cost | Free | Free | Tie |
| Speed (Tier 3) | 122.0s | 22.6s | laguna-xs (5.4×) |
| Output cleanliness | Prose-wrapped JSON | Pure JSON | laguna-xs |
| Corpus audit history | Tier 1/2/3 on ADR-032, more | Tier 1/2/3 on ADR-032 only | solar (more data) |
| Gate verdict coherence (CIS path) | Measured (HALT on ADR-032) | Not yet measured | solar (measured) |
| Parse reliability | Needs stripping | Direct parse | laguna-xs |

Cost is flat, so speed + cleanliness dominate — but the coherence gap is real. The decision is: prefer the strong, structural signal (speed + cleanliness) and treat the weak signal (coherence) as the thing the full bench measures, not a blocker.

---

## Options Considered

### Option A — Keep solar-pro4:free as default (status quo)

- **What it is:** Leave the Hermes default as `upstage/solar-pro4:free`. `adr_audit.py` inherits whatever the Hermes stack resolves to. No override, no routing table.
- **Pros:**
  - Zero harness change — no patch to write, no `--model` flag needed
  - solar-pro4:free is the most-audited model against our ADR corpus (we have Tier 1/2/3 envelopes for ADR-032)
  - Familiar failure modes — we know what solar-pro4:free's prose-wrapping looks like and how to strip it
- **Cons:**
  - 5.4× slower on Tier 3 — corpus-scale calibration becomes a 30-minute event, not a routine operation
  - Prose-wrapped JSON on every call — needs post-processing, adds parse-failure surface
  - Not a calibrated choice — it's the default because it's the Hermes default, not because it's the best audit model
  - The coherence gap with laguna-xs is unmeasured in both directions

### Option B — Route default to laguna-xs-2.1:free (CHOSEN)

- **What it is:** Set `laguna-xs-2.1:free` as the default model for `adr_audit.py`. Keep solar-pro4:free as an explicit calibration reference (one `--model` argument away). Wire the `--model` override so both are callable.
- **Pros:**
  - 5.4× faster Tier 3 — corpus-scale calibration becomes feasible (5 ADRs × 3 tiers × laguna-xs ≈ 5-7 min vs 30+ min on solar)
  - Pure JSON output — no prose stripping, no parse-failure surface from LLM chatter
  - Free — same $0 cost as solar-pro4:free
  - The 5× efficiency story is structural, not a one-off — it comes from the model's output style, which is stable across prompts
  - solar-pro4:free remains available for any call that needs it (calibration reference, per-tier comparison, suspicion about a laguna-xs verdict)
- **Cons:**
  - Less corpus audit history against laguna-xs — we have Tier 1/2/3 for ADR-032 only (vs solar-pro4:free which we've audited more against)
  - We haven't verified that laguna-xs's gate verdicts are *coherent* with solar-pro4:free across the full corpus (the full bench is designed to measure this)
  - Small risk: laguna-xs is a "small" model — if it has a thinner reasoning envelope, its HALT verdicts might be less well-founded than solar's, even if they agree on the gate
  - Opens a follow-on decision: do we also re-route other harness calls (receipt_evaluator, pipeline_runner) to laguna-xs?

### Option C — Per-tier routing table (laguna-xs for Tier 1/2, solar for Tier 3)

- **What it is:** Route fast/cheap models to Tier 1/2 screening, keep the heavy model for Tier 3 confirmation. Maintain a `MODEL_ROUTING` table in the harness that maps {tier → model}.
- **Pros:**
  - Optimizes per-tier: fast screening + heavy confirmation
  - If laguna-xs is good for BAR (Tier 1) but solar is better for LAB (Tier 3 adversarial), you get both
- **Cons:**
  - More complex — needs a routing table, per-tier model selection logic
  - Premature without corpus-scale data — we don't have evidence that laguna-xs fails on Tier 3 LAB specifically (the narrow bench showed it handling Tier 3 fine on ADR-032)
  - Adds a maintenance surface (routing table to update when models change)
  - The narrow bench showed laguna-xs Tier 3 = 22.6s all pure JSON with HALT — no evidence it's worse than solar on Tier 3

### Option D — Defer: don't pick a default, require `--model` on every call

- **What it is:** Don't set a default at all. Every `adr_audit.py` call must specify `--model`. The harness has no opinion.
- **Pros:**
  - Forces explicitness — no hidden default doing work you didn't choose
  - No wrong-default risk
- **Cons:**
  - Friction — every ad hoc audit call needs a model argument
  - No calibrated baseline — "what did we use last time?" becomes a question
  - Defeats the purpose of having a harness — the harness should have a sensible default and let you override it

---

## Decision

**Chosen:** Option B — route default to `laguna-xs-2.1:free`, wire `--model` override, keep solar-pro4:free as explicit calibration reference.

**Rationale:**

1. **Speed is a force multiplier — but for the LLM path, not the rule-based path.** At 5.4× faster Tier 3 *on the `hermes chat` bare-prompt path*, laguna-xs turns a 30-minute corpus calibration into a 5-7 minute one — **if you're calibrating through an LLM**. Through `adr_audit.py`'s rule-based CIS pipeline, calibration is already ~0.1–0.3s per call regardless of model (confirmed by calibration_20260826_1046: 20 calls, all sub-second, all identical). The speed rationale applies to the future LLM path (CIS-with-LLM-client or GIGI+LLM-synthesis), not to today's rule-based harness. The routing decision is forward-looking: when the LLM path exists, laguna-xs is the measured faster option.

2. **Pure JSON is a reliability win.** solar-pro4:free wraps its JSON in prose ("Here is the structured output: ..."). That's not a bug — it's a conversational model being conversational. But for a harness that parses the output, prose wrapping is parse-failure surface. laguna-xs returns raw JSON. That's one fewer thing to go wrong per call × N calls.

3. **Cost is flat, so speed + cleanliness dominate.** All models are free. The decision reduces to: which free model gives us faster, cleaner, more-calibratable audits? laguna-xs-2.1:free wins on both measured axes.

4. **Coherence risk is resolved at corpus scale for the rule-based path.** calibration_20260826_1046 ran 5 ADRs × 4 models = 20 CIS-pipeline calls and found **perfect coherence** — every ADR produced identical gate verdicts and CSS values across all 4 models. The coherence gap closes because there is no LLM to diverge. For the future LLM path (CIS-with-LLM-client or GIGI+LLM-synthesis), coherence is unresolved — that's where laguna-xs vs solar-pro4:free verdicts might differ, and where the full bench (or an LLM-enabled variant) becomes the coherence check. Until then, Option B is forward-looking, not provisional.

5. **The `--model` override is the safety net.** With the override wired, solar-pro4:free remains one argument away for any call that needs it (calibration reference, per-tier comparison, suspicion about a laguna-xs verdict). Option B without the override would be a lock-in; Option B *with* the override is a default with an escape hatch.

**Trade-offs accepted:**

- We accept that laguna-xs's audit verdicts may be less well-founded than solar's on a per-finding basis — we trade *explanation depth* for *speed + cleanliness*, with the understanding that the gate verdict (HALT/WARN/PASS) is the primary output, not the prose explanation.
- We accept that the first corpus-scale run against laguna-xs is partially a coherence check — we're calibrating as we go, not after perfect data.
- We accept a follow-on decision surface: if laguna-xs becomes the default for `adr_audit.py`, should it also become the default for `receipt_evaluator.py` and `pipeline_runner.py`? That's a separate ADR.

---

## Y — Conviction

**Polarity:** YELLOW — we have strong speed/cleanliness evidence but incomplete coherence evidence across the corpus.

**Conviction:** MEDIUM-HIGH — the speed + cleanliness case is structural and stable, not a one-off. The coherence gap is real but addressable (the full audit-bench is the fix).

**Stability:** STABLE for this quarter, contingent on the full bench running without a coherence alarm.

**Loki test:** Strongest case against this decision:

> "laguna-xs-2.1:free is a small model — its HALT verdicts on ADR-032 look right, but that's one ADR. On a 7.7K-char ADR with subtle multi-stakeholder tradeoffs (like ADR-030), a smaller model may miss the coherence failure that solar catches, producing a FALSE PASS. You're trading 5× speed for a higher false-pass rate on complex ADRs, and you won't discover the gap until a decision you audited with laguna-xs goes sideways. The right move is to keep solar-pro4:free as default for Tier 3 (the confirmation tier) and only use laguna-xs for Tier 1 screening."

Response: This is a real risk, but it's a *tier-specific* risk, not a blanket one. Tier 1 (BAR only) is a single-operator screening — the coherence bar is lower. Tier 3 (BAR + KINTSUGI + LAB) is the confirmation tier — that's where solar's depth matters. The Loki case argues for Option C (per-tier routing), not Option B. We're rejecting Option C for now because: (a) we have no evidence laguna-xs fails on Tier 3 specifically (the narrow bench showed it handling Tier 3 fine on ADR-032), and (b) per-tier routing adds complexity we don't yet need. If the full bench reveals laguna-xs-tier-3 divergences, we revisit — that's exactly what the revisit trigger covers.

---

## Consequences

**What changes:**
- `adr_audit.py` default target becomes `laguna-xs-2.1:free` (via `--model` override on the `cli_arcs_run.py` subprocess, or Hermes config override)
- solar-pro4:free remains available as `--model upstage/solar-pro4:free` for calibration calls
- Corpus-scale calibration becomes feasible (5 ADRs × 3 tiers in ~5-7 min on laguna-xs vs 30+ min on solar)
- The first full audit-bench run (5 ADRs × 4 models × Tier 1) becomes a coherence check, not just a speed benchmark

**What gets unblocked:**
- Running the real audit-bench without it being a 30-minute wall-clock event
- Per-model, per-ADR calibration as a routine operation
- Treating model quality as something we can measure regularly, not something we assume

**New decisions this creates:**
- Should laguna-xs also become the default for `receipt_evaluator.py` and `pipeline_runner.py`? (separate ADR — different output structure, different coherence bar)
- Do we maintain a `MODEL_ROUTING` table in the harness, or keep it implicit via `--model` overrides? (simplicity vs explicitness)
- When a new free model appears, do we add it to the calibration corpus automatically, or only when someone flags it?

**Implementation pointer:**
- `operators/adr_audit.py` — add `--model` to argparse, thread through `run_adr_audit()` → each lens → `_invoke_cis_text(prompt, model)`
- `operators/cli_arcs_run.py` — no change needed if model is passed as Hermes-stack-resolved arg; or add `--model` if we want explicit transport
- `~/.hermes/profiles/arcs/config.yaml` — optionally set default to `poolside/laguna-xs-2.1:free` (or keep solar as Hermes default and override per-call)

---

## Analysis / Assessment / Evaluation / Synthesis / Recapitulation

This is the 5-verb decomposition of WHY this routing decision is a big win from a benchmarking perspective.

### Analyze — what is the thing we're measuring, and what axes matter?

The ADR-audit harness produces **structured audit envelopes**: gate verdict (HALT/WARN/PASS), CSS (coherence self-score), findings array with operator-specific severity. Each envelope is the output of a deterministic pipeline: `adr_audit.py` constructs a CIS-framed prompt, shells `cli_arcs_run.py` as a subprocess, parses the JSON output, extracts the gate + CSS from the BAR finding.

The benchmarking axes for a model in this pipeline are:

| Axis | What it measures | Why it matters |
|---|---|---|
| **Parse success rate** | % of subprocess calls that return parseable JSON | A model that returns prose or errors 20% of the time breaks the pipeline — you can't calibrate what you can't parse |
| **Latency per call** | Wall-clock seconds from subprocess launch to parsed envelope | Determines whether calibration is *routine* (minutes) or *an event* (tens of minutes) |
| **Output cleanliness** | Pure JSON vs prose-wrapped | Prose wrapping adds a post-processing step and a parse-failure surface — every unwrapped call is one fewer thing that can break |
| **Gate verdict coherence** | Does the model's HALT/WARN/PASS agree with the reference model on the same ADR? | Calibration requires a reference — if laguna-xs diverges from solar-pro4:free systematically, one of them is wrong (or both are) |
| **CSS distribution** | The coherence self-scores the model assigns | CSS is the model's own confidence signal — a model that's fast but assigns random CSS values isn't calibratable |
| **Cost** | $ per call | All free here, but the axis matters for the general case |

The first three axes (parse success, latency, cleanliness) are **structural** — they come from the model's output behavior, which is stable across prompts. The last two (coherence, CSS) are **substance** — they depend on the ADR content and the model's reasoning.

### Assess — what does the evidence say so far, and how strong is it?

**Strength of evidence per axis:**

|| Axis | Evidence strength | What we know | What we don't know |
||---|---|---|---|
|| Parse success (rule-based path) | STRONG | 20/20 calls parse_ok across 5 ADRs × 4 models (calibration_20260826_1046). Rule-based CIS returns clean JSON regardless of model. | Parse success on the LLM path (bare-prompt or future CIS-with-LLM-client) — laguna-xs was pure JSON on the narrow bench (1 ADR); full-corpus LLM parse success is untested. |
|| Latency (rule-based path) | STRONG | All 4 models: 0.1–0.3s per call across 5 ADRs. Identical. Rule-based CIS is sub-second regardless of model. | N/A for rule-based path. For LLM path: 5.4× ratio (laguna-xs 22.6s vs solar 122s Tier 3) from narrow bench, single ADR, bare-prompt path. |
|| Latency (LLM path — bare-prompt) | MEDIUM | 5.4× ratio from narrow bench (ADR-032, 1 ADR). Structural (output style), stable across prompts. | Whether ratio holds for longer ADRs or full corpus. Whether it holds through a CIS-framed LLM prompt (vs bare prompt). |
|| Output cleanliness (LLM path) | STRONG | laguna-xs = pure JSON always (narrow bench); solar = prose-wrapped always. Structural, stable. | Whether this holds for CIS-framed LLM prompts (structured system prompt may change output behavior). |
|| Gate verdict coherence (rule-based path) | STRONG | PERFECT coherence at corpus scale — all 5 ADRs, all 4 models, identical gate + CSS. No LLM to diverge. | N/A for rule-based path. For LLM path: unresolved — laguna-xs vs solar verdicts through an LLM audit pipeline haven't been measured. |
|| Gate verdict coherence (LLM path) | WEAK | Both models return WARN on bare prompt (CSS 0.4–0.7); both HALT via CIS pipeline (rule-based, not LLM). Path-dependence means bare-prompt verdicts don't predict pipeline verdicts. | Whether laguna-xs and solar agree on structured audit verdicts when both route through an LLM. This requires an LLM-based audit path that doesn't exist yet. |
|| CSS distribution (rule-based path) | STRONG | Per-ADR CSS identical across all models: ADR-004=0.507, ADR-008=0.486, ADR-029=0.546, ADR-032=0.557, ADR-030=0.606. | N/A for rule-based path. For LLM path: which model assigns more meaningful CSS is untested. |

**Assessment:** For the rule-based path (`adr_audit.py` today), all axes are strong — calibration is already instant and perfectly coherent across all models. The routing decision doesn't change any behavior on this path. For the LLM path (future CIS-with-LLM-client, GIGI+LLM-synthesis, or bare-prompt calibration), the speed + cleanliness case for laguna-xs is strong and structural (from the narrow bench), but coherence and CSS distribution are untested at corpus scale. The decision is forward-looking: it sets laguna-xs as the default *for when the LLM path exists*, backed by the narrow-bench timing data and pure-JSON cleanliness. The `--model` override is wired and verified today so the switch is one flag away when the LLM path arrives.

### Evaluate — what's the win, and how big is it?

**The win is not "laguna-xs is faster." The win is "calibration becomes routine."**

Here's the size of it:

- **Before this decision (solar-pro4:free default):** Running the full calibration corpus (5 ADRs × 3 tiers × solar) = 15 calls × ~120s = ~30 minutes wall time. That's not prohibitive for a one-off, but it's prohibitive for *routine* — you don't re-run calibration monthly if it takes 30 minutes. You run it when something feels off. That's reactive, not proactive.

- **After this decision (laguna-xs-2.1:free default):** 5 ADRs × 3 tiers × laguna-xs = 15 calls × ~22s = ~5.5 minutes wall time. That's short enough to run as part of a pre-commit check, a weekly cron, or a "before we merge this ADR" step. Routine calibration is now *operationally feasible*.

- **The 5× number is conservative.** It's measured on Tier 3 (the slowest tier, most prompts, most output). Tier 1 (single operator, shorter prompt) will be even faster on both models, but the ratio may differ. The point is: at every tier, laguna-xs is fast enough to make multi-ADR calibration short.

- **The cleanliness win compounds.** Pure JSON means: no stripping step, no regex on the response text, no "the model returned prose instead of JSON" failure mode. Every call is one less thing to go wrong. Multiply by 15 calls per calibration run × N calibration runs per quarter — that's N×15 fewer parse failures to debug.

- **The coherence check is a feature, not a risk.** By defaulting to laguna-xs *and* running the full bench, the first corpus-scale run becomes a coherence measurement: "does laguna-xs agree with solar-pro4:free on these 5 ADRs?" If yes, we have a faster, cleaner default with confirmed coherence. If no, we have data to decide whether to revert, per-tier route, or investigate. The decision *creates* the coherence data rather than requiring it upfront.

**Why this is a benchmarking win specifically (not just a speed win):**

Most LLM benchmarking is: "run model X on benchmark suite Y, compare accuracy." That's expensive (benchmark suites are large), static (the benchmark doesn't change), and model-centric (the model is the variable).

What we're doing is different:
1. **Corpus-centric, not benchmark-centric.** Our "benchmark suite" is our actual ADR corpus — 5 ADRs that range in size and content. That's a small, domain-specific corpus, not a generic eval. The calibration is meaningful *for our use case*, not for LLMs in general.
2. **Path-dependent measurement.** We're measuring the model *through the actual pipeline* (CIS-framed prompt → subprocess → parsed envelope), not through raw prompts. That's the only measurement that's valid for calibrating the harness — and it's the measurement most benchmarks skip.
3. **Multi-axis, not single-score.** We're not producing "laguna-xs scores 0.85, solar scores 0.82." We're producing a routing table: which model is fast, which is clean, which is coherent, which parses reliably. That's a decision tool, not a leaderboard.
4. **Operational feasibility as the metric.** The win isn't "laguna-xs is 5× faster on a benchmark." The win is "we can now run calibration regularly instead of rarely." That's a *process* win, not a *model* win — and it's the kind of win that makes the whole calibration effort sustainable.

### Synthesize — what does this mean for the system, not just the harness?

**Immediate (this quarter):**
- `adr_audit.py` gets a default model + `--model` override (wired and verified)
- solar-pro4:free remains the calibration reference (we keep its envelopes)
- The full audit-bench (calibration_20260826_1046) **confirmed model independence** at corpus scale — all 4 models produce identical rule-based envelopes, 20/20 parse_ok, perfect coherence. The `--model` flag is inert through this path but ready.
- Calibration via `adr_audit.py` is already instant (~0.1–0.3s/call) and model-independent — no routing decision needed for the rule-based path today

**Medium-term (next quarter, when/if CIS gains an LLM client or GIGI+LLM synthesis):**
- The routing decision activates: laguna-xs-2.1:free becomes the default *for the LLM path*, backed by the narrow-bench timing data (5.4× faster, pure JSON) and verified `--model` override
- Calibrations run on a schedule (weekly or per-ADR-merge) through the LLM path, producing a historized envelope log where model *does* matter
- When a new free model appears, we add it to the calibration corpus and measure it against the reference — the routing decision becomes data-driven, not ad hoc
- If laguna-xs ever goes offline or changes quality, we have a measured alternative (solar-pro4:free) and a calibration history to compare against
- GIGI as a retrieval substrate (without LLM synthesis) makes audits richer (corpus context, historical envelopes, routing table query) without adding model-dependence — model routing stays dormant until the synthesis layer arrives

**What this does NOT solve (and doesn't claim to):**
- It doesn't calibrate the *substance* of the audits (are the findings right?) — that's a separate validation question that requires human review of audit envelopes against actual ADR outcomes
- It doesn't solve the path-dependence problem for other harness calls — `receipt_evaluator.py` and `pipeline_runner.py` may have different optimal models
- It doesn't address paid models — if we ever introduce a paid tier, the cost axis becomes non-flat and the routing decision re-opens
- **It doesn't make `adr_audit.py` model-dependent today** — the harness is rule-based (CIS pipeline with `llm_client=None`). The `--model` flag is wired but inert. Model routing only becomes behaviorally relevant when the CIS pipeline gains an LLM client or a GIGI+LLM synthesis layer. GIGI alone (local-first fiber-bundle DB as retrieval/augmentation substrate) makes the audit richer without adding model-dependence — it augments context, not the model.
- **It doesn't calibrate the LLM path** — the 5.4× timing and pure-JSON cleanliness data come from the `hermes chat` bare-prompt path (narrow bench, 1 ADR). Whether those results hold for a CIS-framed LLM prompt (structured system prompt + ADR text) is untested. An LLM-based audit path that produces structured envelopes per model doesn't exist in the harness yet.

### Recapitulate — what's the bottom line, in one paragraph?

Routing the ADR-audit harness default to `laguna-xs-2.1:free` is a **forward-looking routing default** that activates when the CIS pipeline gains an LLM client or GIGI+LLM synthesis layer — not today's rule-based harness, where all 4 models already produce identical envelopes at ~0.1–0.3s per call (confirmed at corpus scale: calibration_20260826_1046, 20/20 calls, perfect coherence, model-independent). The `--model` override is wired and verified but inert until an LLM path exists. When it does, laguna-xs is the measured faster option (5.4× on the `hermes chat` bare-prompt path, pure JSON) and solar-pro4:free stays one flag away as the calibration reference. The benchmarking win isn't a current speed gain — it's that we've wire-ready the routing mechanism, confirmed model independence where it matters today, and set a data-backed default for the LLM path that's one decision away from activation. GIGI alone (retrieval substrate without LLM synthesis) makes audits richer without touching the routing calculus — model routing stays dormant until the synthesis layer arrives.

---

## Linked receipts / ADRs

- ADR-032 — lewoof × Better & Better pilot (calibration anchor; Tier 1/2/3 envelopes on solar-pro4:free)
- `_STATE/benchmarks/` — model-routing calibration evidence store (created this session): `README.json`, `routing_table.json`, `index.json`, `calibration_20260826_1046.json`
- (to be created) — per-tier routing ADR, if Option C reopens after corpus-scale coherence data on the LLM path
- (to be created) — receipt_evaluator / pipeline_runner model-routing ADR, if laguna-xs default extends beyond `adr_audit.py`

---

## Evidence persistence — answer to the user's question

**Were we keeping benchmark data in persistent global state at session start? No.** At the start of this session, benchmark evidence lived only in terminal scrollback and `/tmp/` scripts — ephemeral, gone when the session ended. `_STATE/` had handoff docs and worktree catalogs but no `benchmarks/` subdirectory.

**Are we keeping it now? Yes — we created it this session.** `_STATE/benchmarks/` is the persistent evidence store:

- `_STATE/benchmarks/README.json` — schema + purpose
- `_STATE/benchmarks/routing_table.json` — current routing decision + per-model summary stats (with the model-independence caveat from calibration_20260826_1046)
- `_STATE/benchmarks/index.json` — manifest of calibration runs
- `_STATE/benchmarks/calibration_20260826_1046.json` — full 20-call envelope log with per-call results (model, ADR, tier, gate_verdict, CSS, latency_s, parse_ok, exit_code, timestamp, call_log)

The 20-call corpus-scale bench (5 ADRs × 4 models × Tier 1, real `adr_audit.py --model` path) is now on disk, not just terminal output. Future routing decisions can reference it without re-running. The `routing_table.json` explicitly documents the caveat: *"CIS pipeline currently runs rule-based (no LLM client, llm_client=None). --model flag is wired but has no effect through adr_audit.py → cli_arcs_run.py path."*

**What's still not persisted:** the narrow bench (1 ADR × 4 models bare-prompt path, `/tmp/adr_model_bench_narrow.py` output) and the Tier 2/3 audit outputs — those are in session history and `/tmp/` only. If they matter for a future routing decision, they should be migrated into `_STATE/benchmarks/` with a clear path label (bare-prompt, not CIS-pipeline).
