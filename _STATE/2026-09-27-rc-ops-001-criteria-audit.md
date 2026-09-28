# RC-OPS-001 graduation criteria audit (2026-09-27)

> **What this is:** a PROPOSAL. `operators/RC-REGISTRY.json` `criteria_status` is a human ruling.
> Nothing here writes it. The proposed diff is at the bottom; it lands only on Zach's explicit go.
> **Backlog row:** `hyperstition-rc-criteria-run` (rank 4, issue #581), blocked by
> `echo-detector-embedding-signature` (rank 3, issue #580).
> **Audited against:** origin/main at `e36084f4` (2026-09-27 23:02 EDT). Every claim below carries a
> path, a sha, or a live probe. Anything I could not verify is marked UNCONFIRMED.

## Level trigger check (criterion 2 dependency)

`git log origin/main -- operators/arcs_inchworm_echo.py` shows exactly one commit, `a03f1a11`
(the original candidate landing). No embedding-signature commit has merged. Issue #580 is OPEN.
Per the route rule, criterion 2 is written up as **blocked-on-detector** and criteria 1, 3, 4 are
audited in full.

## Summary table

| # | Criterion | Registry now | Proposed | Basis |
|---|---|---|---|---|
| 1 | ROM-vocabulary canon collision resolved | `false` | **`true`** | Human ruling 2026-08-28, Option A, on main at `380b8e70` |
| 2 | Detector precision adv-FP <= 0.10 @ recall >= 0.80 | `FAIL (adv-FP 1.0 @ default; dogfood 2026-08-29)` | **unchanged, tagged blocked-on-detector (#580)** | Dependency has not merged |
| 3 | K >= 3 blind, source-independent, hindsight-confirmed echoes, zero FP | `1` | **`1` (unchanged)** | One clean echo on record; no field operation has run since |
| 4 | Observatory period served | `false` | **`false` (unchanged)**, with "served" now defined | Instrument does not exist yet; the deploy blocker cited in the receipt is stale |

Net: one field flips (criterion 1). Three stay. The candidate remains `GRADUATION_INITIATED`.

---

## Criterion 1: ROM-vocabulary collision resolved

**Evidence.**
- `_DECISIONS/CANON-COLLISION-rom-vocabulary.md` header: `Status: RESOLVED, Option A (human ruling,
  2026-08-28)`. The ruling declares the 7 ROM Primitives in `.claude/arcs-canon.md` as CANON, relabels
  the 6 execution laws as "ROM behavioral laws (derived)" and the 7 axioms as "epistemic foundations".
- `runtime/specs/ROM-AXIS-INDEX.md` exists, header `AUTHORITATIVE (human ruling, 2026-08-28)`, and
  names the ORTHOGONAL ECHO DETECTOR as canon primitive 5. So the candidate has an unambiguous ROM to
  join, which is what this criterion exists to guarantee.
- Tier banners are present in all three source files (grep-verified 2026-09-27):
  `.claude/arcs-canon.md:68-70`, `runtime/specs/ARCS-v9-ROM.md:1-5`,
  `_CANON/book-ii/part-ii-rom-axioms.md:17-18`. Each points to the axis index.
- The ruling merged to main in `380b8e70` (2026-08-29 00:38 EDT, PR #194).

**Why the registry says `false`.** Timing, not disagreement. The registry field was written in
`b26e06e6` at 2026-08-29 00:20 EDT, eighteen minutes before the ruling commit landed on main. The
initiation receipt (`_STATE/2026-08-29-rc-ops-001-graduation-initiation.md`) also lists criterion 1
as OPEN for the same reason. The field has simply never been revisited.

**One deviation from the receipt's wording.** The receipt said "resolve via `/canon-review`". The
collision was resolved by a direct human ruling recorded in the collision doc instead. The
substance (a human picked Option A and the repo was aligned to it) is what the criterion needs.
The route differs; the outcome does not. Flagged so nobody later reads "via /canon-review" as unmet.

**Proposed value:** `rom_vocab_resolved: true`.

**What would flip it back:** a new escalated collision on the ROM axis (for example the open Tao
two-books collision, `_DECISIONS/CANON-COLLISION-tao-two-books.md`, is a different axis and does not
touch this), or a reversal of the 2026-08-28 ruling.

---

## Criterion 2: detector precision (blocked-on-detector)

**Status: blocked-on-detector.** The only measurable value is still the 2026-08-29 bench.

**Bench on record** (`_STATE/2026-08-29-echo-detector-dogfood.json`, harness
`scripts/echo_detector_dogfood.py`, 5 positives / 3 clean negatives / 4 adversarial negatives):

| min_sim | precision | recall | adversarial FP rate |
|---|---|---|---|
| 0.20 (default) | 0.556 | 1.0 | 1.0 (4/4) |
| 0.30 (best F1) | 0.714 | 1.0 | 0.5 (2/4) |

No threshold reaches adv-FP <= 0.10 at recall >= 0.80. The initiation receipt calls the limit
architectural (keyword-library token overlap plus a `different-domain = 1.0` orthogonality
multiplier). That diagnosis is what #580 exists to fix through the injectable `signature_fn` and
`orthogonality_fn`.

**Field proxy (UNCONFIRMED here).** The rank-3 backlog trigger records "2026-09-27 echo feed: 0 real
matches, FP proxy 0.8". I could not reproduce it: `scripts/echo_ridgeline_feed.py` reads
the unfold markdown files under the untracked inbox directory and `ridgeline` chips on backlog rows (none on main yet; PR #585
is open). In this worktree the feed returns "fewer than 2 ridgeline-shaped texts". The number is
plausible against the bench but is the fanout session's word, not mine.

**Proposed value:** keep the string, append the block reason:
`"FAIL (adv-FP 1.0 @ default; dogfood 2026-08-29); blocked-on-detector (#580)"`.

**What would flip it:** #580 merges, the dogfood harness is re-run on the same labeled bench with
the embedding signature injected, and the sweep shows a threshold with adv-FP <= 0.10 at recall
>= 0.80. The feed's scrambled-control FP proxy is a field sanity check, not the criterion; the
receipt is explicit that the labeled bench is the measurement.

---

## Criterion 3: blind, source-independent, hindsight-confirmed echoes (K >= 3)

**Definition applied** (from the initiation receipt): counts only if (a) the two sources could not
see each other (source-independent), (b) no shared searcher or intent primed the match (blind), and
(c) a human later confirmed the isomorphism was real (hindsight-confirmed). Same-session echoes are
excluded by the standing name-the-priming rule (witness `_STATE/witness/2026-08-28.jsonl`, 23:37).

**Candidates, with provenance:**

| Candidate | Source | Source-independent | Blind | Hindsight-confirmed | Counts |
|---|---|---|---|---|---|
| 2026-07-13 dual-audit reconciliation (Architect audit via Perplexity Space on a ~50-file corpus vs Implementer audit on arcs-v9; "neither audit could see the other's corpus") | `_PATTERNS/2026-07-13-dual-audit-reconciliation.md` | yes | yes | yes, by the reconciliation doc and re-affirmed in the 08-29 receipt | **1** |
| 2026-08-28 foreshadow echoes (NotebookLM vision films Dec 2025 to Mar 2026 vs the 08-28 session's "fable war game" matching the OS doc's Phase 3) | `_STATE/witness/2026-08-28.jsonl` 23:11 | partly (documents predate the session) | **no**: one searcher, one intent, same session | yes | 0 (bias-free, not blind) |
| 2026-08-28 Perplexity cross-substrate convergence (serialization + teardown) | cited in the 08-29 receipt | weak: shared-corpus common cause | partial | no explicit verdict | 0 (candidate) |
| 2026-09-04 "this is a Rom Candidate witness I think" | `_STATE/witness/2026-09-04.jsonl` 01:00 | n/a | n/a | n/a | 0 (a ROM-candidate proposal, not a cross-domain echo) |
| 2026-09-07 witness stubs | `_STATE/witness/2026-09-07-cheapest-edit-is-a-diff.json`, `_STATE/witness/2026-09-07-the-loop-closes.json` | n/a | n/a | n/a | 0 (naming moments, single domain) |
| 2026-09-27 ridgeline echo feed | rank-3 trigger text | n/a | n/a | n/a | 0 (0 real matches reported) |

I also grepped every witness file for `echo`, `isomorph`, and `blind` (8 files hit) and read each hit.
None beyond the table describes a cross-domain match between two sources that could not see each other.

**Field operation has not started.** Two mechanical facts:
- `operators/ledger/operator-receipts.jsonl` contains zero `run_inchworm` or echo entries. The MCP
  bridge has never been asked to run the detector.
- `operators/arcs_inchworm_echo.py` carries no source-independence metadata. The receipt's
  "operational trigger event" (log each candidate with `same_session` / `same_domain` /
  `same_author_intent` for later hindsight grading) is unbuilt: a grep for those fields, plus
  `source_indep` and `hindsight`, hits only the module docstring (1 line).

So the count is human-attested, not detector-produced, and can only move by hand until that logging
exists.

**A trap to name.** "Zero confirmed false positives in blind operation" is vacuously true today
because no blind operation has run. A vacuous zero must not be read as the FP half of criterion 3
being satisfied. It is satisfied only once blind candidates exist and none is refuted.

**Proposed value:** `blind_echo_count: 1` (unchanged).

**What would flip it:** two more echoes that pass all three tests, each with a human verdict, and no
refuted candidate in the same blind window. Prerequisite for that to happen mechanically: build the
source-independence logging in the detector (or in the ridgeline feed) so candidates accrue with
provenance instead of being reconstructed from witness files after the fact.

---

## Criterion 4: Observatory period served

**What "served" should mean (proposal, since the registry never defined it).** All four, each
checkable by grep or by a human verdict:

1. The detector runs in its **field version** (on new-artifact ingest against the prior-session
   corpus), not only the bench, across **multiple real sessions**. Proposed floor: at least 5
   sessions on at least 5 distinct days. The floor is a proposal for Zach to set; the receipt says
   "multiple" and nothing more.
2. Every candidate is **logged with provenance** (source-independence flags plus a severity grade)
   to an append-only file under `_STATE/` or the operator ledger.
3. Every candidate is **graded in hindsight** by a human (confirmed or refuted), and the grades are
   written back next to the candidate.
4. The log is **replayable in the Observatory**: a session can be scrubbed to the moment a candidate
   fired and its later grade seen alongside.

Explicitly NOT part of "served": a receipt count. The registry note is clear that "period + 100
receipts" was inherited by accident from the Folksonomy candidate. This audit does not reintroduce it.

**Current state against that definition.**
- (1) Field runs: none. Ledger has zero detector runs; the only executions on record are the
  2026-08-29 bench and the 2026-09-27 ridgeline feed (0 matches).
- (2) Provenance logging: unbuilt (see criterion 3).
- (3) Hindsight grading: no candidate log exists to grade.
- (4) Observatory replay: the Observatory page IS on main and live, but it has no echo surface.
  `src/app/observatory/page.tsx` landed 2026-06-05 (`4460bcea`). Live probe 2026-09-27:
  `https://app.arcs.care/observatory` returns 200 with Next.js markup. The page replays receipts
  and a risk register with severity lanes; a grep for `echo` in it returns 0 hits.

**Stale premise in the receipt, corrected.** The initiation receipt says criterion 4 "needs the
unpushed Observatory page" deployed first, citing a sha that is not an object in this clone. That blocker is gone: the page has been
on main since June and serves today. What remains is the instrument gap (an echo-findings log and a
replay surface for it), not a deploy.

**Proposed value:** `observatory_period_served: false` (unchanged).

**What would flip it:** items 1 through 4 above all true, with the floor in item 1 set by Zach.

---

## Proposed registry diff (for Zach's go; NOT applied)

```diff
   "criteria_status": {
-   "rom_vocab_resolved": false,
-   "detector_precision": "FAIL (adv-FP 1.0 @ default; dogfood 2026-08-29)",
+   "rom_vocab_resolved": true,
+   "detector_precision": "FAIL (adv-FP 1.0 @ default; dogfood 2026-08-29); blocked-on-detector (#580)",
    "blind_echo_count": 1,
    "observatory_period_served": false
   },
```

Optional, same edit: add `"criteria_audited_at": "2026-09-27"` and
`"criteria_audit": "_STATE/2026-09-27-rc-ops-001-criteria-audit.md"` next to
`graduation_receipt`, so the next auditor starts from this file rather than the 08-29 receipt.

## What this audit did not do

- Did not write `criteria_status`. Did not touch the registry at all.
- Did not run the detector in the field or grade any echo. Criterion 3 stays human-attested.
- Did not reproduce the 2026-09-27 FP proxy of 0.8 (inputs are untracked in this worktree).
- Did not append to the backlog row's `status`: the row lives on PR #585's branch and is not on main
  yet. The intended append is in the PR body; apply it once #585 lands.

## Fate

`criteria-proposed` for criteria 1, 3, 4. `blocked-on-detector` for criterion 2.
