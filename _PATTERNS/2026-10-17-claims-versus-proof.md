# Claims versus proof: five things ARCS is said to do

Written 2026-10-17 from live evidence, not from memory. Internal reference for product copy. It edits no page; it says which words the evidence supports today and what would move each claim to proof.

## Rule
ARCS refuses to overclaim (memory: brand-promise-refusal-to-overclaim). A claim is allowed in copy at the strength of its weakest link: a mechanism that exists, evidence that it works, and a test that could have shown it failing. Where a link is missing, use the safer wording.

Source of the five: Zach, 2026-10-15: lie detecting, honesty preserving, coherence hardening, conviction building, earned fidelity, "all in one". They are facets of one shape (the bet, the line that moved it, the update, rendered no sharper than the evidence allows). They are not equally earned.

## Evidence snapshot (each line says how it was obtained)
| Fact | Value | Obtained |
|---|---|---|
| Receipts in the production database | 271 | SQL count, 2026-10-17 |
| Receipts with a closed outcome (matched recorded) | 3 (about 1.1 percent) | SQL count, 2026-10-17 |
| Receipts tagged real / tagged test | 0 / 189 | SQL count, 2026-10-17 |
| Evaluation rows on the status page | 6 read NOT RUN (one more reads "not run") | grep of the status page, 2026-10-17 |
| Status page's own disclaimer | mechanisms enforced in the code, not results proven at scale; effectiveness pending independent verification | status page footnote |
| RET take-home forecasts resolved | 11 of 39, mean Brier 0.243; if the stated hit counts are right (7 of 11 true) the in-sample base rate scores 0.231, so no demonstrated skill | RET post-mortem raw summary (untracked); base rate derived by Zach's session partner, not re-run |
| Filing workback beliefs resolved | 7, Brier 0.238 against a base-rate reference of 0.245 (about +3 percent); the model-derived schedule group scored about -1 percent (n=5) | scripts/filing_workback.py --calibration, 2026-10-17 |
| Contradiction check precision on real memory notes | 0 of 3 (all false positives) | coherence sweep and a cheap-model judgment pass, 2026-10-15 |
| Seed ancestry machine-traceable | 16 of 70 seeds rooted, 45 free text only, 9 orphans, 0 cycles | scripts/seed_lineage_check.py --report, 2026-10-17 |
| Errors in the filing build caught by a mechanical check | 3 of 14 (the sweep script, the integrity gate, a mutation test); 10 by the author re-reading or reasoning; 1 by Zach | the filing kintsugi ledger, KF1 to KF14 |
| Served pages containing the phrase "lie detect" | 0 | grep of public and src/app, 2026-10-17 |
| Served files mentioning honesty / coherence / conviction / earned fidelity or clarity | 28 / 43 / 50 / 27 | same grep, counts are files not claims |

## The five claims
### 1. Lie detecting
- **Mechanism that exists:** checks that flag claims lacking provenance, contradicted by another claim, stale, dangling or unsourced (`scripts/coherence_sweep.py`, `scripts/integrity_gate.py`, `scripts/seed_lineage_check.py`, and VERIFIED/UNVERIFIED marking in `_STATE/earliest-public-disclosure-ledger-2026-10-15.md`).
- **Shown:** each check fires on a planted fault in its self-test.
- **Not shown:** that any of it detects lies. The contradiction check was wrong 3 times in 3 on real data (`_STATE/coherence-sweep-memory-2026-10-15.md`). What the checks catch is unearned sharpness (precision beyond the evidence), not falsehood. A sourced, consistent, fresh claim can still be wrong.
- **Safer wording:** "flags claims that outrun their evidence." Do not use "lie detector" or "detects lies" (it appears in no served page today; keep it that way). Related: [[coherence-is-not-correctness-suspect-the-tidy-reversal]].
- **To prove:** a planted-fabrication test. Mix N claims, half true and sourced, half fabricated with specific-looking details; the flag rate on fabricated claims must exceed the rate on true ones by a pre-registered margin. Kill: flag rate on fabricated is no higher than on true. Not run.

### 2. Honesty preserving
- **Mechanism that exists:** refuse-to-overclaim rules, VERIFIED/UNVERIFIED on every date, the kintsugi log of the build's own errors (`_STATE/filing-kintsugi-2026-10-15.md`), gates that block a commit citing something not on main (`scripts/integrity_gate.py`). Rule: [[brand-promise-refusal-to-overclaim]].
- **Shown:** the filing build logged 14 of its own errors in the open (rows KF1 to KF14 of `_STATE/filing-kintsugi-2026-10-15.md`; receipt `2026-10-17--filing-event-time-rebuild-pr1458--ZH` records the same caveats). Only 3 were caught by a mechanical check; 10 by the author re-reading, 1 by Zach.
- **Not shown:** that honesty is preserved when no one is reading. Today it rests mostly on the author's vigilance, supported by gates.
- **Safer wording:** "makes overclaiming visible and costly." Avoid "guarantees honesty".
- **To prove:** track, per period, errors found by gates versus by readers; the claim strengthens as the mechanical share rises. Kill: the mechanical share stays near zero while errors keep shipping.

### 3. Coherence hardening
- **Mechanism that exists:** self-tests with planted faults, mutation testing (survivors found and fixed in two scripts), the whole-equals-sum score identity, the integrity and design-debt gates, the seed lineage ratchet.
- **Shown:** gates fail on bad input and pass on good, and survivors of mutation tests were closed.
- **Not shown:** correctness. Coherence is not correctness (memory: coherence-is-not-correctness-suspect-the-tidy-reversal); a tidy story can be wrong, and a perfect result is a prompt for suspicion (the first Monte Carlo said 100 percent on every path).
- **Safer wording:** "hardens consistency and shows where it breaks." Avoid implying that a coherent result is a true one.
- **To prove:** nothing further is needed for the narrow claim; it is a property of the gates and is already demonstrated per script.

### 4. Conviction building
- **Mechanism that exists:** conviction and NCI are defined and scored; the receipt records a prediction and, when closed, an outcome.
- **Shown:** almost nothing about effect. 3 of 271 receipts are closed, none tagged real, so no calibration claim can be made; the Accountant rule needs at least 30 closed per cohort. The RET and filing ledgers show no demonstrated skill (Brier at about the base rate).
- **Not shown:** that using ARCS makes conviction better calibrated. Conviction without calibration is the failure the system exists to catch, so "building" it is the riskiest word.
- **Safer wording:** "makes conviction auditable: you can see what it rested on." Avoid "builds conviction" or "improves your decisions".
- **To prove:** close outcomes. Pre-register the test (calibration of stated conviction against matched outcomes per cohort, n at least 30, compare to the base rate). Kill: Brier at or above the base rate at n at least 30. The binding constraint is outcome capture, not analysis.

### 5. Earned fidelity
- **Mechanism that exists:** the render scale in `WORLD.md` and the Y-gate states in `src/lib/ygate.ts` (weight, tracking, grain by state), the sharpness-must-not-exceed-information principle, a design gate on served pages. Background: [[earned-fidelity-not-maximal-diamond-cut]].
- **Shown:** the render changes with the state; the principle is stated and partly tested for visual sharpness in `_PATTERNS/2026-10-15-arcade-time-machine-earned-fidelity.md`.
- **Not shown:** that readers read the fog correctly (a comprehension test), or that every rendered state matches the underlying state in production.
- **Safer wording:** "the render shows how much the data can bear." Two served pages say the render "never lies" about depth or about where truth is (`public/forge-cut.html` and `public/monolith.html`). That is an absolute; replace it with the safer wording above.
- **To prove:** a reader study (do people estimate certainty better with the fog than without), plus an automated check that rendered state equals computed state. Kill: no difference in reader estimates.

## Copy to change (flagged only; nothing edited here)
The two pages are `public/forge-cut.html` and `public/monolith.html`; the model sentence is the footnote in `public/status.html`.
| Where | Current | Why | Safer |
|---|---|---|---|
| forge-cut page | "the render never lies about depth" | absolute; nothing guarantees it | "the render shows how much the data can bear" |
| monolith page | "the render never lies about where truth is" | absolute; and the page also calls the render a truth head | "the render shows how certain each region is" |
| any copy | "lie detector", "builds conviction", "improves decisions" | claims the evidence does not support | see the per-claim wording above |

The status page's own footnote (mechanisms enforced in the code, not results proven at scale) is the model sentence; keep it, and keep the six evaluation rows reading NOT RUN until they are run.

## What would move claims to proof, cheapest first
1. Close outcomes on real receipts and tag provenance (the binding constraint for claim 4).
2. Run the planted-fabrication test (claim 1); it is a script and a pre-registration, no users needed.
3. Track the mechanical share of caught errors per period (claim 2).
4. Run the reader study and the rendered-equals-computed check (claim 5).

Not legal or regulatory advice. Numbers are as of 2026-10-17 and will drift; re-run the commands named in the snapshot before quoting any of them.
