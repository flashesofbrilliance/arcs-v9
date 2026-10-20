---
title: Risk underwriter, an entangled risk-adjustment policy agent (proposal, not built)
date: 2026-10-20
status: PROPOSED
author: Claude (side session of the shared-intention session), for Zach
asks_for: Zach's ruling on the five questions in section 9
parent: _PROPOSALS/2026-10-20-shared-intention-before-snap.md, section 4b (tactical layer)
freeze: s4 freeze (amendment 6) holds; this file edits no tool description and no code
---

# Risk underwriter: an entangled risk-adjustment policy agent

Zach's words (2026-10-20): "entangled risk adjustment policy agent working with pathogen detection
and kintsugi to progressively derisk and underwrite risk with updating policy".

Prior art: `/prior-art` ranked `control-integrity-described-vs-wired`, `pathogen-detection-via-temporal-paradox-pre-merge`,
ADR-033 (serialization pathogen family), `operators/arcs_kintsugi.py`, `operators/receipt_evaluator.py`
and `scripts/risk_sweep.py` as the top applicable hits. All were read for this design. Marks used
below: **REUSE** (exists and runs), **REUSE-THIN** (exists, under-filled), **GAP** (does not exist).

## 1. The job in one sentence

For each tactical issue (one backlog row), keep a written price of its risk that rises when a pathogen
is detected and falls when a repair is proven, and show that price to Zach before he picks a fate.
It prices. It never decides.

## 2. What "underwrite" means here

**Who holds the risk.** Zach does, always. The agent is the actuary, not the insurer: it cannot
absorb a loss, so it must not pretend to. Underwriting here means three things written on the row:

1. **Exposure**: what is lost if the row goes wrong. Read from `ruin` (60 of 326 rows) and `door`
   (31 rows; one-way vs two-way). REUSE-THIN: 266 rows carry no ruin value.
2. **Cover**: what limits the loss. Read from `gates` (304 rows, REUSE), `rollback` (10 rows) and
   `abort` (10 rows). REUSE-THIN: most rollback and abort text is still marked "DRAFT, unreviewed".
3. **Premium**: the price paid up front to carry the row. The unit is the coin from
   `runtime/specs/effort-policy.json` board (1 coin = about 10 human minutes or 1 USD compute;
   10 coins a day). REUSE. The premium is the number of coins of de-risking work (a gate run, a
   rollback rehearsal, a cohort check) the policy asks for before the row is ready to fire.

A row is **underwritten** when the premium has been paid and the receipts show it: each required
gate has a passing result, and a one-way door has a write-lock declaration (ROM 7). Uninsurable is
a valid answer: a one-way door with ruin high and no rollback gets the price "no cover available",
shown plainly, and the fate is still Zach's.

**Pricing rule (v0, pre-registered here, tuned only by the update loop in section 5):**

| Exposure | Door | Cover present | Premium (coins) |
|---|---|---|---|
| ruin low or blank | two-way | any gate | 0 |
| ruin medium | two-way | gate + rollback | 1 |
| ruin medium | two-way | gate only | 2 |
| ruin high | two-way | gate + rollback + abort | 3 |
| any | one-way | gate + abort + write-lock | 4 |
| ruin high | one-way | no rollback possible | uninsurable (shown, not blocked) |

Loading: each open pathogen finding on the row's files adds 1 coin; each proven kintsugi repair on
the same class removes 1 (floor at the table value). GAP: no loading ledger exists.

## 3. Where it lives

At the **tactical** altitude of the shared-intention grid (section 4b of the parent proposal): the
issue row already holds blockers (`depends_on`, `unblocks`), configs (`route`, `needs`), risks
(`ruin`, `door`, `gates`) and failure modes (`abort`, `rollback`). The agent reads those fields and
writes one new field. The **surgical** spec file per issue (`runtime/specs/issues/<row-id>.md`,
proposed, not built) is where the premium's de-risking steps would be listed.

Proposed field: `underwriting` on the row, holding `{premium, exposure, cover, loading, priced_at,
policy_version, evidence: [...]}`. GAP. `backlog_status_check.py` does not restrict row keys, so it
needs no gate change.

Operator fit: no existing operator prices risk. Immune (op 18, `ConstitutionalCourt`, PARTIAL) only
adjudicates on a BAR ruin verdict; Accountant (op 19, READY) scores outcomes after the fact; Conductor
(op 22, `receipt_evaluator.py`, READY) runs the Kintsugi phase gate on a receipt. The underwriter sits
between them: it reads detection before the fact and is scored by the Accountant after. Numbering is
the periodic table only (AGENTS.md gotcha 16); this proposal does not assign an operator number.
GAP, and Zach's call whether it is an operator, a mode of Immune, or a plain script.

## 4. How detection and repair feed the policy (the entanglement)

"Entangled" here means one ledger, read three ways: a pathogen finding, the repair that answered it,
and the price change it caused share one id, so no one of them can move without the others showing it.

**Detection side (raises the price):**

| Source | What it detects | Mark |
|---|---|---|
| `scripts/risk_sweep.py` | breaking or non-idempotent diffs on main; tiers 0 to 3, tier 3 = one-way door never auto-healed | REUSE; its register `_STATE/risk-register.jsonl` was not present on this machine 2026-10-20, so it may never have run here |
| temporal-paradox pre-merge check (memory) | content on origin that matches a fix but predates it: duplicate work | REUSE as practice; GAP as a script |
| ADR-033 pathogen family + `attribution_provenance_lint.py` | serialization pathogens incl. ventriloquy (speaker dropped) | REUSE |
| `scripts/backlog_ripeness.py` | BLOCKED rows (dead dependency), SECRETLY-DONE rows | REUSE |
| `scripts/findings_gait.py` | open findings and reopen rate per source, false positives by source | REUSE |

**Repair side (lowers the price, only when proven):**

| Source | What it proves | Mark |
|---|---|---|
| kintsugi seam ledger (memory `kintsugi-seam-when-the-test-was-wrong`: seam, detected_by, whose_error, repair, heading_change, evidence) | a named repair, written in the turn it happened | REUSE as a format; GAP as one repo-wide ledger |
| `operators/receipt_evaluator.py` Kintsugi phase gate | a receipt passed its phase gate | REUSE |
| findings_gait closure rule: a closure counts only if it survives re-detection | the repair held | REUSE |

**The one rule that joins them:** a repair lowers the premium only after the detector that found the
pathogen has run again and stayed quiet. A repair that is only written down, or that a detector of
the same model family judged, lowers nothing (memory `control-integrity-described-vs-wired`: a
control owned by the agent it polices is captured). Detector false positives are tracked per source
(findings_gait already does: seedbank-drift 7 of 15 false today), and a source's loading is scaled
by its measured precision, so a noisy detector cannot inflate prices for long.

## 5. What updates the policy, and how fast

Two speeds, kept apart on purpose.

**Fast (prices, every run):** the per-row price is recomputed from the table in section 2 whenever a
detector or repair writes to the ledger. This changes numbers, not rules. Cadence follows the
detectors (risk_sweep nightly cron, ripeness and findings_gait at session start). REUSE of existing
cadence; no new schedule.

**Slow (the table itself, by human ruling only):** the pricing table changes only when the Accountant
scoreboard has enough closed outcomes to say it is wrong. Trigger: at least 10 priced rows reach a
terminal state (DONE, COMPOSTED, SUPERSEDED) with an outcome recorded via
`scripts/receipt_outcome_queue.py`. The agent then drafts a table amendment with the evidence
(which price bands lost money, which were overpriced) and Zach rules on it. Each table version gets
a `policy_version` stamp so old prices stay readable. Amendment numbering through `scripts/oracle.py`.

Why 10 and not 30: the Accountant's calibration floor is 30 per cohort, which this backlog will not
reach for months. 10 is enough to propose, not to conclude; the draft says its n out loud.
Evidence grade follows effort-policy: a self-graded outcome is recorded but never moves the table.

## 6. What the agent may never do (NOTOMATION)

1. Never veto, block or delay a row. It shows a price; Zach may fire an uninsurable row.
2. Never set a fate (`state`), claim a row, or write `abort`, `rollback` or `ruin`. It may propose
   text for them, marked DRAFT, as rows already do.
3. Never lower a price on its own word. Only a re-run detector or an external outcome lowers it.
4. Never edit its own pricing table. Table changes are Zach's ruling (section 5).
5. Never auto-heal a one-way door (risk_sweep tier 3 rule, kept).
6. Never hide a price change. Every change writes a ledger line with the triggering evidence id,
   the seam visible (ROM 6).
7. Never price a person. Rows about counterparts are priced on the action, not on the human
   (feedback_job_search_positive_screen PII rules).

## 7. Pre-registered test (written before any build)

**Claim:** the v0 table ranks rows by realized trouble better than the existing `ruin` field alone.

**Set:** every row that reaches a terminal state between the build date and 30 days after, plus the
10 rows already carrying `rollback`. Frozen list written to `_STATE/underwriter-test-set.jsonl` on
build day, before any price is shown to Zach (so the price cannot steer the fate).

**Trouble (the outcome, counted by script, not judged):** a row had trouble if any of: a revert commit
cites it; a risk_sweep or findings_gait finding on its files reopened after closure; its PR needed a
follow-up fix PR within 7 days; its receipt outcome is recorded as missed.

**Pass:** Spearman correlation between premium and trouble is at least 0.15 higher than between
`ruin` (low=1, medium=2, high=3, blank=0) and trouble, on the frozen set, with n at least 15.
**Fail:** anything else, including n under 15 at day 30. On fail the agent is composted, not
re-tuned on the same set (the s4 amendment-6 lesson: tuning on the test set voids it).

## 8. Gaps, in build order (none built here)

1. `underwriting` field on rows. GAP.
2. One entangled ledger joining finding id, repair id and price change. GAP (risk register,
   findings_gait ledger and seam ledgers exist separately).
3. Temporal-paradox check as a script. GAP.
4. Fill `ruin` on the 266 blank rows (a cheap pass, Zach confirms each band). REUSE-THIN.
5. Review the DRAFT `abort` and `rollback` text on the 10 rows. REUSE-THIN.
6. Confirm `risk_sweep.py` has run on this machine (register absent 2026-10-20). Unverified.

## 9. Decisions for Zach

1. Is the coin the right premium unit, or should premium be in gate runs?
2. Operator, a mode of Immune (op 18), or a plain script?
3. Accept "uninsurable is shown, never blocked"?
4. Accept 10 closed outcomes as the trigger to draft a table change?
5. Does this wait for s4 to be scored (the freeze), or may gap 4 (filling `ruin`) start now as
   data work that touches no tool description?

No ADR is proposed yet; if Zach accepts, the number comes from `python3 scripts/oracle.py next adr`.
