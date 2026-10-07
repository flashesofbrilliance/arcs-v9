# Compass dopeness eval v0 (the S-tier bar)

> Status: DRAFT v0, authored 2026-10-06/07 by a four-lens judge panel (GAAP auditor, field physicist, Fun House skeptic, PLG operator) over measured prod aggregates; the synthesis was scored by three judges. Field claims were NOT yet independently verified against prisma/schema.prisma (the verify stage is re-running). Em-dashes: 0. Companion files: runtime/specs/decision-geometry-cells-v0.json (the 25-cell model), _STATE/2026-10-07-tool-cluster-jtbd-map.json, the explorer at playground.arcs.care/decision-geometry.


Repo: /Users/zharris/arcs-v9/.claude/worktrees/compass-dopeness-audit-963f43. Facts: Supabase prod aggregates, 2026-10-06, custody SQL run this session. Plain numbers are custody-traced (GAAP). Numbers with a tilde (~) are assessed (non-GAAP). Percentages written plainly are arithmetic on two custody counts and are labeled "derived". Code wins over docs where the three 5-tuples disagree (AGENTS.md).

Scope note: the relayed request also asks for a map of tool clusters and their jobs to be done. This spec cannot carry that; it is a separate deliverable and is listed under open questions.

## 1. The question: can dope be objective, and the answer

The question. "Dope" is a felt quality. Can a compass output be called dope on evidence a skeptic can rerun, rather than on the founder's impression?

The answer: conditional yes, and not yet.

Dope as a feeling stays non-GAAP forever; no column holds it. But the three consequences the word names each leave a trace in a table the schema already has or can hold with one column:

- Sticky leaves a second seed receipt by the same non-founder userId on a later calendar day (Receipt.userId, Receipt.createdAt, Receipt.parentId null).
- Curiosity-inducing leaves a child receipt that names which tributary spawned it (Receipt.parentId set, Receipt.parentTributaryIndex in 0, 1, 2).
- Infectious leaves a second human with a custody link back to the first (today: nothing; proposed: a BriefShare redemption counter, or a seed carrying an origin pointer to another user's receipt).

A compass output is objectively dope exactly when (a) each trace is read from its own table, (b) at least two traces agree on distinct non-founder users without sharing a behavioral column (the diamond rule), (c) the cohort excludes the author, excludes anonymous rows, excludes provenance test rows, excludes nudged returns, and (d) the query and thresholds were committed before the count ran.

Today none of (a) through (c) is satisfiable from prod. Provenance real is 0 of 267 and the field is client-attested with no shipped client that sends it, so null means unattested, not real. parentTributaryIndex is 0 of 107 children because nothing writes it. Infectious has no column. 209 of 267 receipts are the founder's. The four other signed-in users hold 1 to 3 receipts each, all single-day.

So the honest verdict is "not yet measurable", which is a different claim from "no" and a different claim from "yes". The instrument below is what would make it measurable. Three of the four blockers are write-path fixes, not usage facts.

## 2. Operational definition

Unit: the seed receipt (Receipt.parentId IS NULL; 160 today). Every rate is seeds-that-qualify over cohort seeds, never over 267 receipts, because children are the curiosity numerator and must not sit in the denominator.

Cohort: Receipt.userId IS NOT NULL AND userId is not the founder's AND provenance IS DISTINCT FROM 'test'. Provenance 'real' counts only once the compass route derives it server-side; until then null rows are "unattested".

A seed is dope when, for a cohort user, at least two of the three traces fire within 30 days of the seed and the third trace is not blind (has a server-written column), and at least one non-synthetic Outcome exists in the lineage.

- STICKY: the same userId authors another seed on a calendar day at least 7 days after the first (date_trunc('day', createdAt) distinct count >= 2), with no debrief or reminder sent to that user in the prior 72 hours (Receipt.debriefSentAt, Receipt.reminderDate). Same-thread follow-up inside one sitting is engagement, not return.
- CURIOSITY-INDUCING: a child receipt (parentId = seed.id or a descendant) with parentTributaryIndex in 0, 1, 2 (meta, challenge, adjacent), authored by the same cohort user, whose sharpQuestion (or decision) differs from the parent's after normalization (a retry is not a return). Weak form: an Annotation row of type THOUGHT or COMMENT on the receipt (model Annotation, schema lines 523 to 540).
- INFECTIOUS: a second cohort user whose arrival is custody-linked to the first: a BriefShare redemption by a non-owner (no column today; proposed), or a seed by a different userId carrying an origin pointer to this receipt (no column today; proposed, and impossible by construction while the compass route drops a parent not owned by the caller, route lines 247 to 252). A minted BriefShare row is intent, not spread.
- CLOSURE (the only terminal proof): an Outcome row with synthetic = false on a receipt in the lineage; Receipt.status LOGGED; Receipt.driftState LANDED or DRIFTING.
- PUSH (denominator for any pull ratio): count of Receipt.debriefSentAt IS NOT NULL and count of User.debriefOptIn = true, logged with the eval date. Push is measured, never assumed zero.

Model self-reports (nciScore, nciByLens, isSatoshi, yState, renderResolution, flowTopology, and the free-text kairos, altitude, reversibility, macroTags) are inputs to the hypothesis and never evidence for it. They carry a tilde in any dopeness sentence.

## 3. Metrics table

| Name | What it measures | Exact column or event | GAAP or non-GAAP | Value today | Confound |
|---|---|---|---|---|---|
| Seeds (denominator) | Questions asked, not receipts written | Receipt.parentId IS NULL | GAAP | 160 seeds, 107 children, 267 receipts | None; this is the only legal denominator for a dope rate |
| Tributary follow edge rate (curiosity, coarse) | Follow-ups run under a seed | Receipt.parentId (written at compass/route.ts line 441) | GAAP | 107 children over 160 seeds (0.67 per seed, derived); 24 children have grandchildren; max depth 13; max version 6 | A rephrase and a followed tributary both make a child; cannot separate them without the index. ~most of the depth is founder self-use (founder holds 209 of 267; children are not split by userId in the facts) |
| Tributary index coverage (curiosity, precise) | Which tributary (0 meta, 1 challenge, 2 adjacent) spawned the child | Receipt.parentTributaryIndex (schema line 181) | GAAP column, never written | 0 of 107 children | Write-path gap, not behavior: the dashboard POST sends only parentReceiptId (dashboard/page.tsx line 190), the route destructures only parentReceiptId and provenance (lines 185, 188) and writes parentId only (line 441). The sole non-generated reference is a read-only select in the uncommitted src/app/api/geometry/route.ts |
| brief_tributary_followed | Click on a tributary from the brief | track('brief_tributary_followed') at brief/[receiptId]/page.tsx line 82 and brief/reflect page line 110; the receipt page emits nothing | non-GAAP (client event, ad-blockable, no DB join, carries no index) | Not in the facts (not queried) | Fires on click before the compass succeeds (overcounts) and only on the brief surface (undercounts) |
| Distinct-day return (sticky, strong form) | Users with seeds on 2 or more calendar days | Receipt.userId, date_trunc('day', Receipt.createdAt); Receipt.parentId IS NULL | GAAP-derivable | Non-founder: 0 of 4 signed-in users; 12 of 159 sessions span more than one day (all founder or anonymous by arithmetic, since external users hold at most 3 receipts and are single-day) | 48 anonymous receipts have no userId and can never show a return; a return that only reads history leaves no receipt |
| Session depth (sticky, weak form) | Same-thread follow-up | Receipt.sessionId grouped; Receipt.version | GAAP | 41 of 159 sessions at depth 2 or more (26 at depth 2 to 3, 15 at depth 4 plus); median span for depth 2 plus is 56 minutes | One sitting proves engagement, not return; all depth 4 plus sessions are founder or anonymous by arithmetic |
| Push applied | Nudges sent | count(Receipt.debriefSentAt IS NOT NULL); count(User.debriefOptIn = true); Receipt.reminderDate | GAAP columns, not in the facts | Not measured this session; the ripe route comment (receipts/ripe/route.ts line 15) says the email path reaches ~0 opted-in, which is a code comment, assessed | If push is truly ~0 then every observed return is unforced, but only for the founder |
| Outcome closure rate | Did a human come back to say what happened | Outcome.receiptId, Outcome.matched, Outcome.regretScore, Outcome.synthetic; Receipt.status; Receipt.driftState | GAAP; cohort split non-GAAP (~) because the facts do not split by userId | 3 of 267 (1.1 percent, derived); matched 2; synthetic 0; avg regretScore 2.33 on n = 3; status LOGGED 3, OPEN 264; driftState ON_TRACK 261, DRIFTING 4, LANDED 2; non-founder share ~0 | n = 3 is below the Accountant floor of 30 per cohort; the outcome route emits no track() and the outcomeNudge flag ships dark (src/lib/flags.ts line 27) |
| Brief generation rate | Receipts with a cartography brief | Brief.receiptId unique join | GAAP | 176 of 267 (65.9 percent, derived) | Whether a Brief needs a deliberate pull or fires on first view was not established this session; smoke tests and the founder inflate it |
| Share mint count | Owner minted a share link | BriefShare rows (briefId, createdBy, createdAt, revokedAt) | GAAP, not in the facts | Not aggregated this session | A mint is intent; BriefShare stores a tokenHash only |
| Share redemption | A non-owner resolved a share token | None. src/app/api/shared/brief/route.ts resolveShare() performs zero Prisma writes | BLIND (no column) | 0 recorded by absence of a column, not of behavior | /shared/brief carries the token in the URL fragment, so pageviews cannot be joined to a brief |
| Cross-user fork | Another user's seed whose origin is this receipt | None. compass/route.ts lines 247 to 252 scope the parent lookup to {id, userId} of the caller; forkPath null and mergedFrom "[]" are hardcoded at lines 491 to 492; batonId 0 | BLIND and structurally 0 | 0 by construction | A viewer who follows a tributary from a shared brief becomes an orphan seed |
| Anonymous claim rate | Anonymous bearing claimed after sign-in | Receipt.surface = EPHEMERAL_SAVE; client events receipt_save_clicked, completed, failed, dismissed | GAAP for the column; non-GAAP for the events | EPHEMERAL_SAVE 1; ORIENT 266; anonymous receipts 48 | The 1 claimed row carries a userId while the 48 do not, so "1 of 48" mixes populations; receiptSaveNudgeV11 ships dark (flags.ts line 34) |
| Earned-fidelity reach | Has the compass ever rendered its top state | Receipt.yState, Receipt.renderResolution (src/lib/ygate.ts) | GAAP counts of a model-derived state | GREEN 0, LOCKED 0, SHARP 0 of 267; FORK 137 plus PARADOX 116 = 253 of 267 (94.8 percent, derived); GRAIN 146, MOIRE 116, DEGRADED 5 | Aggregates cannot separate "nobody earned clarity" from "the gate cannot emit GREEN"; a known-GREEN fixture through computeYGate is the cheap test |
| NCI composite and 5C lens coverage | Model self-assessed coherence; whether the 5C record exists | Receipt.nciScore; Receipt.nciByLens (schema line 108; written at route lines 449 to 452) | GAAP population counts of non-GAAP content | nciByLens present 27 of 267 (10.1 percent, derived); nciScore avg ~57.5, p10 ~38, p90 ~78 (self-assessed values) | The 2026-06-23 S-tier rule (all five layers non-NULL) fails mechanically on 240 rows; ~rollout-date artifact, testable (see falsifiers) |
| Satoshi flag rate | Model-flagged rare moves | Receipt.isSatoshi (Boolean(parsed.is_satoshi), route line 458) | GAAP count of a non-GAAP flag | 34 of 267 (12.7 percent, derived) | Roughly 1 in 8 is not rare; self-graded, counts for nothing |
| Gate contestation and lineage | Did anyone push against the gate or use lineage | Receipt.yOverride, forkPath, mergedFrom, batonId | GAAP | yOverride 0; forkPath set 0; mergedFrom non-empty 0; batonId set 0 | Zero can mean trust or no affordance; with 137 FORK receipts and 0 forkPath, the chosen path is never recorded |
| Provenance labeling | Is any receipt labeled real | Receipt.provenance (schema line 205; from request body at route line 188; written at line 507) | GAAP count | real 0, test 189, null 78 | Client-attested, no shipped client sends it; null is "unattested" |
| Enum hygiene | Can prep enums be cohorted on | Receipt.stakes, horizon, mode, doorClass | GAAP | stakes MEDIUM 156, HIGH 74, LOW 34, lowercase variants 2, null 1; horizon WEEK 175, QUARTER 51, TODAY 22, YEARS 19 (YEAR declared, 0 observed); mode PLAN 161, COURT 96, QUICKMOVE 10; doorClass TWO_WAY 171, ONE_WAY 96 | 3 dirty stakes rows split any GROUP BY; COURT 96 equals ONE_WAY 96 and may be one signal counted twice (untested) |
| Geometry parse coverage | Can 5H and 5R be cohorted | rawResponse paths: kairos (leading status word), altitude (L-range), reversibility (leading float), macroTags (JSON array) | non-GAAP until parsed | rawResponse present 267; with geometry 266; parse-miss counts not run | Any count on these is a parse; the miss count ships beside the result |
| Tribune coverage | Anterior and posterior reads | Tribune rows per Receipt | GAAP | 12 rows against 267 receipts (under 5 percent, derived) | The reads that would show the field re-deforming as outcomes land are mostly absent |

## 4. Judgment rules

1. Seeds are the only denominator. Check: SELECT count(*) FROM "Receipt" WHERE "parentId" IS NULL; every rate divides by that.
2. Founder exclusion. The founder's rows are their own Accountant cohort and never feed a product claim. Check: every cohort query carries WHERE "userId" IS DISTINCT FROM :founder; a query without it cannot feed a tier claim. Expected cohort today: at most 58 rows (48 anonymous plus 10 across 4 users), and 10 after rule 3.
3. Anonymity exclusion. Check: WHERE "userId" IS NOT NULL on every sticky and infectious query; surface = EPHEMERAL_SAVE rows are tagged, not counted as a second visit.
4. Test and template exclusion. Check: exclude provenance = 'test' (189); run the shared-line boilerplate control over the remainder's question text against founder and test questions and drop any pair sharing a line of 8 or more tokens; print the dropped count.
5. Provenance must be server-derived before 'real' counts. Check: grep -n provenance src/app/api/compass/route.ts shows only the body destructure (line 188) and the create (line 507); until the route derives it from auth plus surface plus a test-key allowlist, null rows print as "unattested".
6. Nudge exclusion: pull counts only when unforced. Check: for each cohort receipt, createdAt minus the user's last debriefSentAt or reminderDate; if the delta is between 0 and 72 hours, tag pull_attribution = push. Also print count(debriefSentAt IS NOT NULL) and count(User.debriefOptIn) with the eval date.
7. A child without parentTributaryIndex is continuation, not curiosity. Check: grep -rn parentTributaryIndex src returns a writer in compass/route.ts, AND SELECT count(*) FROM "Receipt" WHERE "parentTributaryIndex" IS NOT NULL > 0; the curiosity metric is that count, never the children count.
8. A retry is not a return. Check: normalize child and parent sharpQuestion (fallback decision); count only when the strings differ.
9. Sticky means a second calendar day, at least 7 days out. Check: GROUP BY "userId" HAVING count(DISTINCT date_trunc('day', "createdAt")) >= 2 over seeds, with max minus min day >= 7.
10. Infectious needs a non-owner actor. Check: a redemption column on BriefShare exists and is > 0 (proposed), or a seed with an origin pointer to a receipt owned by a different userId exists (proposed); until then infectious prints "unbuilt stream" and contributes 0.
11. Closure outranks depth. A receipt at depth 4 plus with status OPEN and no Outcome is flagged LOOP (entropy masquerading as motion). Check: rank by Outcome present, then status LOGGED, then driftState LANDED.
12. Model self-reports are inputs, never evidence. Check: a lint over the eval text: any sentence containing nciScore, nciByLens, isSatoshi, yState, renderResolution, flowTopology, kairos, altitude or reversibility together with a digit must contain a tilde or the words "self-assessed"; a pull formula may read only createdAt, parentId, parentTributaryIndex, version, sessionId, Outcome.*, Brief.generatedAt, BriefShare.*, yOverride, debriefOptIn, debriefSentAt, reminderDate.
13. Minimum n before calibration. No claim about regret, match rate, or NCI versus outcome below 30 non-synthetic Outcome rows in the cohort (Accountant, Operator 19). Check: SELECT count(*) FROM "Outcome" o JOIN "Receipt" r ON r.id = o."receiptId" WHERE o.synthetic = false AND r."userId" IS DISTINCT FROM :founder; below 30 print sufficiency = insufficient with n.
14. Zero GREEN at n >= 100 triggers a gate audit before any fidelity claim. Check: if yState GREEN = 0 and renderResolution SHARP = 0 at count(*) >= 100, push a known-GREEN prep plus parsed fixture through computeYGate in src/lib/ygate.ts; if it returns FORK or PARADOX, mark the thresholds uncalibrated and drop the render condition from the ladder until re-run over the 266 rawResponse rows with geometry.
15. The diamond rule. An A or S claim cites at least two Prisma models that share no behavioral column, joined only on Receipt.id, and the traces come from at least two distinct non-founder userIds. Check: count distinct models named in the evidence (>= 2) and distinct userIds across the union of two trace sets (>= 2).
16. Enum hygiene is printed, never merged. Check: for each enum column, count(*) WHERE value NOT IN (declared set); print beside every cohort split (stakes: 3 today).
17. Free-text geometry is non-GAAP until parsed. Check: regex the leading token (status word, float, L-range) and print matched and unmatched counts side by side; unmatched > 0 forces a tilde.
18. Pre-register before counting. Check: the SQL for each metric lives in a committed file whose git SHA is older than the result; a result citing no SHA is rejected.
19. Canon must not outrun closed loops. No ADR, page or post may call the compass sticky, infectious or curiosity-inducing while non-founder non-synthetic Outcome rows are below 2 per trace. Check: grep -rniE 'sticky|infectious|dope' over _DECISIONS and public/*.html; each hit cites a receipt id whose Outcome row exists with synthetic = false and a non-founder userId, else flagged.
20. Every blind leg gets its column in the same PR as the first surface that would display it. Check: npm run build passes with the column referenced in a route; prisma migrate deploy (not db push); a smoke test writes the column on a test receipt.
21. Every surfaced tier names its falsifier and decays. Check: each tier claim carries falsified_if and re_verified_at; a tier not re-verified within 30 days drops one rung.

## 5. The ladder, F to S

Tier F, Plumbing. Receipts persist with geometry and the pipeline runs end to end. Criteria: rawResponse present, validationState PASS. Today: met. 267 receipts, rawResponse 267, geometry 266, validationState not PASS 0, briefs 176.

Tier D, Touched by a stranger. At least 1 non-founder signed-in user authored at least 1 receipt that is not provenance test. Today: met on count only. 4 users, 10 receipts by arithmetic (267 minus 209 minus 48), all single-day; ~unknown how many of the 10 are null versus test.

Tier C, Recorded (the instrument is not blind). Every leg has a server-written column and the gate is shown able to open: parentTributaryIndex written on children by the compass route; a BriefShare redemption record (proposed); provenance derived server-side; push counted (debriefSentAt, debriefOptIn); a known-GREEN fixture passes computeYGate; return-day SQL committed. Today: not reached. Index 0 of 107 with no writer; redemption has no column; provenance client-attested; push unmeasured; GREEN 0 of 267 untested against a fixture.

Tier B, Sticky. At least 1 cohort user (non-founder, non-anonymous, non-test) authors a seed on a calendar day at least 7 days after their first, with no debrief or reminder in the prior 72 hours. Today: 0. All 4 external users are single-day. Founder-only evidence exists (12 multiday sessions, 41 sessions at depth 2 plus) and is excluded by rule 2.

Tier A, Convergent. At least 2 of the 3 traces fire on distinct cohort users (sticky per B; curiosity = child with parentTributaryIndex set and a differing question; infectious = redemption or cross-user origin), the cohort holds at least 10 non-founder users with at least 1 seed each, and at least 1 non-synthetic Outcome exists per fired trace. The diamond rule applies. Today: 0, and two of the three traces cannot be recorded by shipped code.

Tier S, The S-tier bar. All of A, plus: the cohort holds at least 30 real-provenance non-founder seeds; all three traces fire; non-synthetic Outcome rows in the cohort reach 30 with the Accountant printing sufficiency = sufficient and the matched rate and regret reported; at least 1 cohort receipt reached yState GREEN or LOCKED on a gate first shown to open on a fixture; nciByLens is non-null on every cohort receipt so the 5C layer can be scored; the five layers of the 2026-06-23 bar (5D sharpQuestion, 5W hypersphere manifold, 5C nciByLens, 5R reversibility parsed, 5H altitude parsed) are non-NULL and consistent on at least 1 cohort receipt, with "consistent" defined mechanically as the parsed altitude falling inside the L-range in the rawResponse and the parsed reversibility agreeing with doorClass; and the tier is re-verified within 30 days. Model self-reports stay tilde'd even at S. Today: not reached and not measurable. Blockers in order: provenance client-attested; parentTributaryIndex never written; no redemption or origin column; outcomes 3 of 267; nciByLens 27 of 267; GREEN 0 untested.

Where the corpus sits: D on count, with F met and C not reached. Net reading: plumbing-true with a labeling debt; the dopeness numbers are not bad, they are unmeasured.

## 6. Falsifiers

1. SELECT over cohort seeds GROUP BY userId HAVING count(DISTINCT day) >= 2 returns a row with days at least 7 apart and no nudge in the prior 72h: B is met and "no external return" falls.
2. After the route writes parentTributaryIndex, 30 percent or more of new children carry an index: "curiosity is unobservable" falls. If 50 external children accumulate with the field still null: the premise that tributaries induce curiosity falls for the tributary surface.
3. A known-GREEN fixture through computeYGate returns FORK or PARADOX: 0 of 267 GREEN is a gate ceiling and every earned-fidelity claim about terrain falls until recalibration. If the fixture passes and real-cohort seeds reach 30 with GREEN still 0: the benign reading (nobody earned it) survives.
4. Vercel's brief_tributary_followed count over the same date range is greater than 0 while parentTributaryIndex stays 0: tributaries do pull and the DB is blind; the finding becomes an instrument defect, not a field reading.
5. count(debriefSentAt IS NOT NULL) > 0 and child receipts cluster inside 72h after those sends: the assumption that observed pull is unforced falls and every ratio is recomputed with push as denominator.
6. A join shows mode COURT rows are not the same rows as doorClass ONE_WAY (both 96): the two are independent signals; if they are the same rows, one signal is counted twice and cannot sit in a 5-tuple as two layers.
7. nciByLens presence on rows created after its ship date is below 90 percent: the rollout-artifact explanation for 27 of 267 falls and points to a write-path drop at route lines 449 to 452.
8. The 3 existing Outcome rows all belong to the founder: external closure is exactly 0 and every regret or calibration number is founder self-grading.
9. A human reads 20 of the 78 provenance-null receipts and 15 or more are real questions: "the corpus is test-dominated" falls and the gap is labeling, not usage.
10. The shared-line control shows the 4 external users' questions share 8-token lines with founder or test prompts: infectious is seeded, not organic.
11. At Outcome n >= 30 per cohort the dope rate does not correlate with Outcome.matched or with lower regretScore: the definition is a gate without a fate and is discarded, not tuned.
12. isSatoshi stays near 12.7 percent on a fresh external cohort: the flag is a model prior, not a rare-event detector, and leaves every dopeness surface.
13. Brief rows are shown to be generated by smoke tests or server prefetch rather than a human GET: 176 of 267 leaves the re-entry proxy list.
14. yOverride stays 0 after a visible override affordance ships and 50 FORK or PARADOX receipts accrue: "no override means no affordance" falls, and the Annotation table separates trust from indifference.

## 7. Findings the facts already force

1. The real cohort is empty and the field cannot fill it: provenance real 0, test 189, null 78; provenance is read from the request body (route line 188) and no shipped client sends it. Every number in this audit is on test or unattested data.
2. Curiosity is dropped at write time, not absent in users: 107 children carry parentId, 0 carry parentTributaryIndex, and src has no writer (dashboard sends only parentReceiptId; route writes only parentId at line 441). One field of wiring unblocks the whole curiosity stream.
3. Non-founder stickiness is 0 of 4: four signed-in users with 1 to 3 receipts each, all single-day. Founder holds 209 of 267 (78.3 percent, derived). 48 anonymous receipts can never show a return. All depth 4 plus (15) and multiday (12) sessions are founder or anonymous by arithmetic.
4. Infectious is blind at the DB and cross-user fork is 0 by construction: BriefShare stores tokenHash, createdBy, createdAt, revokedAt; /api/shared/brief writes nothing; the compass route drops a foreign parent (lines 247 to 252); forkPath 0, mergedFrom non-empty 0, batonId 0.
5. The compass has never rendered its top state in prod: GREEN 0, LOCKED 0, SHARP 0; 253 of 267 sit in FORK or PARADOX; 262 of 267 render GRAIN or MOIRE. Aggregates cannot tell gate ceiling from foggy terrain; that is itself a finding against observability.
6. The loop does not close: outcomes 3 of 267, matched 2, synthetic 0, avg regretScore 2.33 on n = 3; status OPEN 264; driftState ON_TRACK 261. ON_TRACK and OPEN are defaults, not findings: with 1.1 percent closure, ON_TRACK means nobody came back. The Accountant floor of 30 is nowhere near met.
7. Push is unmeasured, not zero: debriefSentAt and debriefOptIn counts are absent from the facts; the ripe route's ~0 opted-in is a code comment.
8. The 5C layer exists on 10 percent of rows: nciByLens 27 of 267; the 2026-06-23 S-tier rule fails mechanically on 240 rows before any judgment is applied. rawResponse geometry on 266 of 267 suggests a backfill is possible.
9. isSatoshi 34 of 267 (12.7 percent, derived) is a self-grade at roughly 1 in 8: neither rare nor evidence.
10. Founder-cohort well depth is real and custody-traced: 41 of 159 sessions at depth 2 plus, 12 multiday, 24 of 107 children with grandchildren, max depth 13, max version 6. This proves the shovel works, not that the ground pulls.
11. Enum hygiene is nearly clean: stakes has 2 lowercase variants and 1 null; horizon YEAR is declared with 0 observed; COURT 96 equals ONE_WAY 96 and is untested for overlap; kairos, altitude and reversibility are free text and uncountable without a parser.
12. Canon has outrun closed loops: the S-tier bar (2026-06-23), ADR-041 aspects and ADR-081 were authored while non-founder closed loops numbered 0 to 3.
13. Net tier: D on count, F met, C not reached. Three of the four blockers to reading the ladder above C (provenance, parentTributaryIndex, share arrival) are write-path fixes; the fourth (outcomes) is capture, which AGENTS.md already names as the P1 gap.

## 8. Instrumentation gaps (blind spots, minimal fix, no new deps)

1. Tributary choice. Blind spot: parentTributaryIndex never written. Fix: followTributary(prompt, index) on the brief, reflect and receipt pages appends trib=0|1|2 to the dashboard URL; the dashboard forwards parentTributaryIndex in the POST body; the compass route validates 0..2 and writes it only when the parent resolved. Column exists; no migration. ~half a session.
2. Share redemption. Blind spot: /api/shared/brief writes nothing. Fix: one migration adding redeemedCount Int default 0, firstRedeemedAt, lastRedeemedAt to BriefShare (proposed columns), incremented by updateMany after resolveShare. ~1 hour plus migrate deploy.
3. Cross-user origin. Blind spot: a viewer who follows a tributary from a shared brief becomes an orphan seed. Fix: one migration adding an origin pointer column on Receipt (proposed, lineage hint only, no read privilege); the shared page pushes /dashboard?q=<tributary>&origin=<receipt.id>; the compass stores it after an existence check and never loads it as parent. ~1 hour.
4. Provenance. Blind spot: client-attested, no client sends it. Fix: derive server-side in the compass route from auth plus surface plus a test-key allowlist (test when the request carries the smoke-test key or a known test userId, else unattested); backfill rule for the 78 null rows decided by Zach. No migration.
5. Push counter. Blind spot: debriefSentAt and debriefOptIn never aggregated. Fix: scripts/dope_eval.sql (checked in, pre-registered) printing count(debriefSentAt IS NOT NULL), count(debriefOptIn), and the 72h nudge join. No code change.
6. Return-day SQL. Blind spot: no committed query. Fix: same script, GROUP BY userId over seeds with distinct-day count and max-minus-min day. No code change.
7. Gate calibration. Blind spot: GREEN 0 of 267 untested. Fix: a unit test pushing a known-GREEN prep plus parsed fixture through computeYGate; then a script re-running computeYGate over the 266 rawResponse rows with geometry under reviewed thresholds. No deps.
8. Outcome capture. Blind spot: 3 of 267, outcomeNudge dark, outcome route emits no event. Fix: flip OUTCOME_NUDGE on Zach's yes; add track('receipt_outcome_matched') in the outcome route (non-GAAP, but the Outcome row is already the GAAP record). Capture rate is the keel.
9. Geometry parser. Blind spot: kairos, altitude, reversibility are prose. Fix: a stdlib regex parser in scripts/ that emits status word, L-range and float plus an unmatched count; later, enumerate in the prompt. No deps.
10. Enum normalization. Blind spot: 3 dirty stakes rows. Fix: one UPDATE to uppercase and a route-side normalization; print the dirty count beside every cohort split until it reads 0.
11. Explorer data path. Blind spot: the route that selects parentTributaryIndex for the client-side explorer (src/app/api/geometry/route.ts) is uncommitted in this worktree. Fix: commit it with the ladder JSON below as its tier source so the explorer computes tiers from the same fields this spec names.
12. Self-report lint. Blind spot: nothing stops a tilde-less model number entering canon. Fix: scripts/dope_text_lint.py over this spec and any page that cites it (rule 12), wired to pre-commit alongside the existing gates.


## 9. Ladder as JSON (the explorer's tier source)

```json
[
 {
  "tier": "F",
  "rule": "Plumbing: count(Receipt) > 0 AND every receipt has rawResponse present AND validationState = 'PASS'. Met today: 267 receipts, rawResponse 267, validationState not PASS 0.",
  "fields": [
   "Receipt.id",
   "Receipt.rawResponse",
   "Receipt.validationState",
   "count(Brief)"
  ]
 },
 {
  "tier": "D",
  "rule": "Touched by a stranger: count(DISTINCT Receipt.userId) WHERE userId IS NOT NULL AND userId <> founder AND provenance IS DISTINCT FROM 'test' >= 1. Met on count today: 4 users, 10 receipts by arithmetic, all single-day.",
  "fields": [
   "Receipt.userId",
   "Receipt.provenance",
   "Receipt.createdAt"
  ]
 },
 {
  "tier": "C",
  "rule": "Recorded, the instrument is not blind: count(Receipt WHERE parentId IS NOT NULL AND parentTributaryIndex IS NOT NULL) > 0 AND count(Receipt WHERE provenance = 'real') > 0 with provenance derived server-side AND count(Receipt WHERE debriefSentAt IS NOT NULL) is reported (may be 0) AND a BriefShare redemption record exists (proposed column, not in schema today; treat as unmet until it exists) AND a known-GREEN fixture passes computeYGate. Not reached today: index 0 of 107, real 0, push unmeasured, redemption column absent, GREEN 0 untested.",
  "fields": [
   "Receipt.parentId",
   "Receipt.parentTributaryIndex",
   "Receipt.provenance",
   "Receipt.debriefSentAt",
   "Receipt.reminderDate",
   "count(BriefShare)",
   "Receipt.yState"
  ]
 },
 {
  "tier": "B",
  "rule": "Sticky: over seeds (parentId IS NULL) in the cohort (userId IS NOT NULL AND userId <> founder AND provenance IS DISTINCT FROM 'test'), at least 1 userId has count(DISTINCT date_trunc('day', createdAt)) >= 2 with max day minus min day >= 7 days, and the later seed's createdAt is more than 72 hours after that user's last debriefSentAt or reminderDate. Today: 0 of 4 external users.",
  "fields": [
   "Receipt.parentId",
   "Receipt.userId",
   "Receipt.createdAt",
   "Receipt.provenance",
   "Receipt.debriefSentAt",
   "Receipt.reminderDate"
  ]
 },
 {
  "tier": "A",
  "rule": "Convergent: cohort holds >= 10 distinct non-founder userIds with >= 1 seed each; at least 2 of 3 traces fire on distinct cohort userIds: sticky (tier B predicate), curiosity (a child with parentId set AND parentTributaryIndex IN (0,1,2) AND normalized sharpQuestion differing from the parent's), infectious (BriefShare redemption by a non-owner or a seed whose origin pointer belongs to another userId; both proposed columns, so this trace reads 0 today); AND count(Outcome WHERE synthetic = false) >= 1 per fired trace on a cohort receipt. Diamond rule: evidence cites >= 2 Prisma models joined only on Receipt.id. Today: 0.",
  "fields": [
   "Receipt.userId",
   "Receipt.parentId",
   "Receipt.parentTributaryIndex",
   "Receipt.sharpQuestion",
   "Receipt.decision",
   "Receipt.createdAt",
   "Receipt.provenance",
   "count(Outcome where synthetic = false)",
   "count(BriefShare)",
   "count(Annotation where type in ('THOUGHT','COMMENT'))"
  ]
 },
 {
  "tier": "S",
  "rule": "The S-tier bar: tier A holds AND count(cohort seeds WHERE provenance = 'real') >= 30 AND all 3 traces fire AND count(Outcome WHERE synthetic = false on cohort receipts) >= 30 with matched rate and avg regretScore reported (Accountant sufficiency) AND count(cohort Receipt WHERE yState IN ('GREEN','LOCKED')) >= 1 on a gate first shown to open on a fixture AND nciByLens IS NOT NULL on every cohort receipt AND on >= 1 cohort receipt the five layers are non-NULL and consistent: sharpQuestion present (5D), rawResponse hypersphere manifold What/Who/Where-When/Why/Flow-State present (5W), nciByLens all five keys present (5C), rawResponse.reversibility leading float parses and agrees with doorClass (5R), rawResponse.altitude parses to an L-range (5H) AND re_verified_at within 30 days. Model self-report fields are gates on presence only, never on value. Today: not reached and not measurable.",
  "fields": [
   "Receipt.provenance",
   "Receipt.parentId",
   "Receipt.userId",
   "Receipt.yState",
   "Receipt.renderResolution",
   "Receipt.nciByLens",
   "Receipt.sharpQuestion",
   "Receipt.doorClass",
   "Receipt.rawResponse.reversibility",
   "Receipt.rawResponse.altitude",
   "Receipt.rawResponse.kairos",
   "Receipt.rawResponse.macroTags",
   "count(Outcome where synthetic = false)",
   "Outcome.matched",
   "Outcome.regretScore",
   "Receipt.status",
   "Receipt.driftState"
  ]
 }
]
```

## 10. Open questions for Zach

- Tool clusters and JTBD map: the relayed request asks to start mapping the 256 catalogued tools into clusters with jobs to be done. This spec's schema cannot carry it. Should it run as its own session over runtime/specs/tool-catalog.json, and should the dopeness traces above (sticky, curious, infectious, closure) be the cluster axes?
- Founder userId: which userId is the founder's for the WHERE clause in every cohort query? The facts give 209 receipts but not the id; the eval cannot be pre-registered without it.
- The 78 provenance-null receipts: are these your real decisions that were never tagged, or probes? A hand read of 20 (falsifier 9) is the cheapest answer; who does it and when?
- Provenance server-side derivation: is a test-key allowlist plus known test userIds acceptable as the rule, and should rows written by Playwright smoke tests carry provenance test automatically?
- Flip OUTCOME_NUDGE and RECEIPT_SAVE_NUDGE_V11 on prod? Both ship dark; capture rate (3 of 267) is the keel and neither lever has been pulled.
- The two proposed columns (BriefShare redemption counters, Receipt origin pointer): approve the migrations via prisma migrate deploy, or defer until the tributary index writer lands and shows a non-zero rate?
- COURT 96 equals ONE_WAY 96: run the overlap join now (one SQL) so the 5-tuple does not carry one signal as two layers?
- Thresholds to pre-register before any count: 7 days for sticky, 72 hours for the nudge window, 10 users at A, 30 seeds and 30 outcomes at S. Change any before they are committed with a SHA?
- Y gate fixture: do you have a known-GREEN prep plus parsed output from any past session to use as the fixture, or should the test construct one from the ygate.ts thresholds?
- Commit src/app/api/geometry/route.ts (currently untracked in this worktree) as the explorer's data path with this ladder JSON as its tier source?
