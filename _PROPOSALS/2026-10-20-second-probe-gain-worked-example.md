# Worked example: second_probe_gain on the shared-intention session (2026-10-20)

Status: PROPOSAL, receipt-ready. Seed 17 `seed-second-probe-gain`, defined in
`_PROPOSALS/2026-10-20-second-probe-gain-and-drift.md` (PR 1699, merged). Source record:
`_PROPOSALS/2026-10-20-shared-intention-before-snap.md` sections 4g to 4k (PR 1691, open) and the
handoff fragment `_HANDOFFS/fragments/20261020T142750Z--claude-shared-intention-proposal.md`
(PR 1701, open). Seed 18 (drift classifier) is untouched: it waits on this atom. No code.

## Method (pre-registered before counting)
- Claim unit: one bullet, table row or commit-message paragraph of the pass-2 text, per the Op 25 v1
  rule. Backed: the unit itself holds an ADR, sha, repo path, script, URL, receipt id or memory link.
- New: backed in pass 2 and absent from pass 1. Guard: a later step cites or consumes it.
- gain = (new, backed, cited units) / (all pass-2 units).
- Every case was re-probed live today (2026-10-20) before counting; results in each "Re-probe" line.

## Case 1: D0 "the live decisions have no receipts"
- Pass 1: D0 inverse step (4g), from the 2026-10-18 handoff prose.
- Pass 2: D0 verification block (4g), read-only Gmail and `decision_receipt`.
- Units (6): Amy bullet (unbacked: no id); George bullet (backed, receipt id
  `2026-10-16--scout-wonderful-fde-lead-ex-ante--ZH`, cited in fragment Open 2: COUNTS); Vico bullet
  (backed, receipt id `2026-10-14--lyndon-followup-close-pr1304--ZH`, cited in fragment Corrections:
  COUNTS); funnel bullet (unbacked); "confidently false for two of four" (unbacked); revised-lean
  bullet (backed, memory link `false-null-requires-provenance-exhaustion`, consumed by sprint 4k and
  PR 1698: COUNTS).
- Gain 3/6 = 0.50. Delta: a false null became a bridge sprint (PR 1698, merged 7506fbde).
- Re-probe: both receipt ids return from `public.decision_receipt` (Supabase, read-only).

## Case 2: "over 3,500 commits" called stale
- Pass 1: the claim was judged stale against the 5,065 all-commits figure on status.arcs.care.
- Pass 2: the no-merge count.
- Units (3): commit db37e547 body, "the over 3,500 figure is the deliberate no-merge count
  (2026-10-16-concourse.json)" (backed: sha and path; consumed by the claim_index override table:
  COUNTS); fragment State line "stays as written" (unbacked in the unit); fragment Corrections line
  (unbacked).
- Gain 1/3 = 0.33. Delta: no reword of six public Concourse lines.
- Re-probe: `git rev-list --count --no-merges origin/main` = 3,596; all commits = 5,077.

## Case 3: advice to release the stale claim on receipt-test-real-tag
- Pass 1: handoff v3.140.0 Open (other) 2, "three RUNNING claims are stale", acted on as advice.
- Pass 2: the live backlog row, read during the dependency map.
- Units (2): the live row, state DONE, status_note citing `prisma/schema.prisma` and
  `src/app/api/receipts/[receiptId]/provenance/route.ts` (backed, new to the advice, cited by the 4h
  seam row: COUNTS); the 4h seam row (backed, memory link
  `verify-handoff-prose-against-live-backlog-not-just-doc`, but no later step cites it: EXCLUDED).
- Gain 1/2 = 0.50. Delta: a wasted step dropped.
- Re-probe: `_QUEUE/induced-backlog.jsonl` row `receipt-test-real-tag` state DONE today.

## Case 4: the claim index flags the 3,500 line as drifted
- Pass 1: claim index v0 (f612f6b6) read the line as all commits, about 31 percent drift.
- Pass 2: db37e547 adds the `commits_no_merges` metric and a per-source override row.
- Units (3): metric with its recompute command in `scripts/claim_index.py` (backed, asserted in the
  PR 1700 self-test: COUNTS); override row citing `runtime/recoil/generated/2026-10-16-concourse.json`
  (backed, consumed by every index run: COUNTS); "Concourse rows now drift +2%" (unbacked).
- Gain 2/3 = 0.67. Delta: flag cleared; the index output is the consumer.
- Re-probe: `python3 scripts/claim_index.py --json` shows six running Concourse locations, live 3,596,
  drift 0.027.

## Totals
7 counting units of 14 pass-2 units: aggregate gain 0.50. Every case had gain above zero, and in
every case pass 2 changed the answer, not just its wording.

## Earning conditions
| # | Condition | Result | Evidence |
|---|---|---|---|
| 1 | Worked example, both passes counted by hand, every unit listed | PASS | this file; four cases, units listed, each re-probed live |
| 2 | A downstream consumer reads the number and acts (e.g. a stop floor) | FAIL (not built) | no scheduled second probe exists and no floor is pre-registered |
| 3 | Survives a Loki attack | FAIL (not run) | no Op 23 or chief-loki pass yet; known attack surface listed below |

Verdict: the atom stays a SEED. It is not sprouted (2 of 3 unmet) and not composted (nothing was
tested and failed). Reading of the idiom order is left unverified, as memory marks it.

## Attack surface already visible (input for the Loki pass, not a substitute for it)
1. Granularity: the unit is a bullet here. Splitting the Case 1 bullets into sentences changes the
   denominator; the gain is only comparable at one fixed granularity.
2. One source, two hats: Cases 2 and 4 share the same pass-2 source (db37e547). They are not
   independent evidence for the atom.
3. Self-citation: some guard citations (fragment Open and Corrections) were written by the same
   session that wrote pass 2. A same-author cite may not count as "a later step".
4. Selection: the four cases were chosen because pass 2 changed the answer. Gain on second probes
   that changed nothing is uncounted, so 0.50 says nothing about the base rate.
5. Same model family counted these units as wrote them (the standing limit in 4g).

## Receipt-ready fields
- question: Does second_probe_gain earn its place on the shared-intention session?
- horizon: this-week | stakes: low | mode: QUICKMOVE | operator: Claude (worktree priceless-colden-30c3ff)
- what_confirmed: four cases re-probed live (two receipt ids in decision_receipt; no-merge count 3,596;
  backlog row DONE; claim_index drift 0.027); condition 1 met with units listed; aggregate gain 7/14.
- what_unconfirmed: conditions 2 and 3; granularity choice; independence of cases 2 and 4; base rate
  of gain on second probes that changed nothing.
- refs: PR 1699, PR 1691, PR 1701, PR 1700, db37e547, f612f6b6, 7506fbde, this PR.

## Next (not done here)
- Loki pass on this file (condition 3), with attacks 1 to 4 as the opening list.
- Pre-register a stop floor and name the consumer (condition 2) before the drift classifier starts.
- Pollinate last: once a receipt for this note exists, cross-link it into PR 1691 and PR 1695.
