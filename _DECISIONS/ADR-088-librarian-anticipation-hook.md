# ADR-088 : Librarian anticipation hook: suggest an echo scan before the reader has to ask, and make each scan free to reuse

**Status:** DRAFT / PROPOSAL (2026-10-17). Not decided. Zach reviews; nothing is built or wired.
**Sequence:** allocated via `python3 scripts/oracle.py next adr` -> 88.
**Source:** `runtime/specs/librarian-anticipation-hook-v0.md` (merged in PR 1306), which holds the full trigger table, rate limits and fixtures. This ADR records the decision and the kill condition; the spec stays the working detail.
**Prior art read:** `operators/arcs_librarian.py` (already has `recommend(q, budget)`), `scripts/prior_art.py`, the `/echo-scan` skill, `scripts/provenance_lint.py`, `scripts/canon_claims_report.py`, ADR-044 (temporal provenance), ADR-075 (metabolic router), AGENTS.md gotchas 11 and 15.

## Context

On 2026-10-15, during VICO call prep, three problems surfaced late and only after Zach said he was "looking in vs looking out": unsourced quantified claims in the canon (the YellowPaper accuracy and chi-square lines, the `arcs_primitives.py` docstring figures), two differing coherence/NCI definitions, and an acronym mismatch in the Litepaper. `/echo-scan` was suggested reactively. The report `_STATE/2026-10-15-canon-uncovered-claims-report.md` lists 918 uncovered quantified tokens; the repo holds 3 closed outcomes across 254 receipts, far below the n>=30 calibration floor, so none of those figures has data behind it.

## Decision (proposed)

Add a Librarian (Operator 21) anticipation hook with three deterministic triggers: T1 a novelty or efficacy word near a claim, T2 a metric with no evidence-ledger cover, T3 a new term written into the canon or a counterpart universe.

1. **Cheap first pass, free:** `prior_art.py` plus a lookup in an echo ledger and a Rosetta table. A ledger hit is printed and ends the flow.
2. **On a miss, one line with its cost.** `/echo-scan` is offered, never auto-run, and no text is edited (NOTOMATION).
3. **Each scan compounds.** Results are filed as an append-only ledger receipt and as Rosetta rows (their term, ARCS term, MECHANISM or METAPHOR, delta, source receipt, universe). Corrections are new rows pointing at old ones (Kintsugi).
4. **Bounded noise.** One suggestion per trigger per session, three per session, stakes-gated (low: T2 only; medium: plus T1; high: all), a declined term muted 14 days.
5. **Boundaries.** The hook reads counterpart universes and never writes under them. Stdlib only, no new dependencies.

## Kill condition (pre-registered 2026-10-15, before any build)

Measured over the first 10 sessions in which the hook fires, from a suggestion log (trigger, term, accepted|declined|ignored, cost shown):

- K1: accepted / suggestions < 1/3 => throttle to stakes high and T2 only for the next 10 sessions.
- K2: 5 or more declined+ignored within 3 consecutive sessions => mute T1 until re-registered.
- K3: fewer than 2 accepted scans changed a decision (canon edit, ledger entry, strike, backlog item) by session 10 => delete the hook and keep only the ledger lookup.
- K4: no ledger hit reused by session 10 => the Rosetta design failed; drop T3.
- Zach decides at the review, not the hook. Changing thresholds after build needs a new dated entry.

## Gate for the build (gotcha 15)

Every check ships a known-bad and a known-good fixture in its `--self-test`, wired into pre-commit. The report generator already does this.

## Consequences

- Cost: a small deterministic scan per trigger; model spend only when Zach accepts a scan.
- Risk: noise (bounded by the limits and K1/K2) and a ledger that no one reads (K4).
- Not decided here: placement. Recommendation is a pre-commit warning for T2 and T3 and `/prior-art` for T1.

## Open

1. Placement of the hook (above).
2. Keep, cite or strike each uncovered canon token.
3. Reconcile the Librarian's registry row, which says store/retrieve only.
4. The NCI definition split and the Litepaper acronym mismatch are definitional drift outside these numeric triggers.
