# ADR / DEWY reconciled gems — curated 2026-08-10

> Curation pass over the 7-day session sweep (516 raw candidates → top 60 scored → 8 genuine).
> ~52/60 rejected as noise (dominant pattern: compaction recaps restating already-built internals +
> repeated build-log narration that trips the decision-cue heuristic). These 8 are real, unfiled decisions
> worth promoting to an ADR (`_DECISIONS/_TEMPLATE.md`) or a DEWY receipt. Promote or dismiss each.

| # | Proposed title | Type | Date | Session | The decision | Why file |
|---|---|---|---|---|---|---|
| 1 | Gravity Forms native Akismet over a PHP snippet | ADR | 2026-08-10 | yuri-ahmed-communication | No safe code host on the Divi site (no WPCode, won't touch functions.php) + Akismet already active → use GF's native Akismet integration, not a custom `gform_entry_is_spam` hook. | Live-client infra choice with a real constraint; future contributor needs the "why not the snippet." |
| 2 | Counterpart belief-ledger as SSOT→render read-only surface | both | 2026-08-05 | yuri-ahmed-communication | Per-read disclosures + confidence/conviction flags + a serialized "how this belief moved" ledger, one JS model powering render + JSON export, read-only; later extended to show the full pre-meeting→recoil→receipt-close loop, t0-expected vs t-end-actual. | Committed product-surface architecture (data-model shape + honesty affordances). |
| 3 | Eval non-deterministic Lyro against a fixed recognition table | ADR | 2026-08-04 | chatbot-1-1-jtbd-blockers | Grade the non-deterministic bot against a *fixed* competitor-grade→PRL-equivalent oracle table, proving recognition correctness pre-go-live rather than trusting the live model. | Reusable eval methodology for grading non-deterministic agents (fixed-oracle pattern). |
| 4 | Vercel Preview env vars are write-only; verify at runtime | ADR | 2026-06-20 | frosty-kepler | `vercel env pull` empty for Preview is expected (Preview vars default "sensitive"/write-only); confirm a fix by redeploy + runtime test, never CLI read-back. | Durable infra gotcha otherwise re-debugged as a failure. |
| 5 | Metered-hours pricing over a flat retainer (PRL) | both | 2026-08-04 | chatbot-1-1-jtbd-blockers | Price on metered hours, not a flat retainer, because it prices the thing that actually varies (coordination hours) and caps opportunity-cost exposure. | Resolved pricing-instrument tradeoff with explicit rationale; a commercial ADR. |
| 6 | Authority lives in the basin + custody rules, not a person/model | ADR | 2026-08-02 | decision-geometry-logo | Vest authority in the coordinate system (basin) + its named falsifiers/custody rules, never a person, court, or model (people get captured, models commoditized, courts fill with yes-men). | Encodes the model-agnostic moat as an enforceable governance rule. |
| 7 | The fallback agreement is nearly as valuable as the sandbox | DEWY | 2026-08-05 | chatbot-1-1-jtbd-blockers | Sandbox lands ~71%; without a fallback, Stall ~triples (~30%); if the sandbox looks slow, pivot to locking the test-lead "yes." All-four ~32%. | Real pre-commitment bet with explicit priors to check ex-post; textbook DEWY. |
| 8 | A self-scored visual must name its quantity (one call = one scalar) | ADR | 2026-08-10 | counterpart-forge-cli-build | A spike/height encoding a self-score must be labeled with the quantity ("height = my read of the fit"); one call honestly carries one independently-scored scalar, not two converging-to-sync ones. | Craft-floor/honesty constraint for generated artifacts; the forge should enforce it. |

## Promote

Each row promotes via `_DECISIONS/_TEMPLATE.md` (next `ADR-NNN`) and/or a DEWY receipt (existing schema).
Strongest immediate ADR candidates: **#1** (unfiled, today, live client), **#4** (durable gotcha), **#6**
(foundational governance). #7 is a clean DEWY to close ex-post against the Aug-11 Sugar call outcome.
