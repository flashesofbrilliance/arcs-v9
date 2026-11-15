# Fact sheet: mechanization outcomes mining, 2026-11-15 (pass 1, mechanical)

Repo state: origin/main 3f9b9f9. Every fact names the command that re-derives it. Facts only; no interpretation.

F1 Backlog: 571 rows. HELD 149, HOLDING 56, OPEN 86, BLOCKED 8, READY 21, RUNNING 8, DONE 165, COMPOSTED 71, SUPERSEDED 7.
   cmd: python3 -c "import json,collections;print(collections.Counter(json.loads(l)['state'] for l in open('_QUEUE/induced-backlog.jsonl') if l.strip()))"
F2 Waiting pile age (HELD+HOLDING with `added`): 60d+ 17, 30-60d 122, 7-30d 44, <7d 22.
F3 407 rows carry depends_on; 0 dangling ids.
F4 scripts/backlog_ripeness.py reports ~27 rows RIPE today (all depends_on terminal, or trigger date passed), incl. recoil-kairos-7s-test (gates recoil-brian-acceptance), recoil-ship-twin, recoil-skills-on-runner, recoil-service-cli, seat-backlog-row-adapter, seat-unbound-triage, receipt-randomized-plumbing-closes.
   cmd: python3 scripts/backlog_ripeness.py
F5 pre-commit runs backlog_ripeness.py only as --self-test, only when the script itself is staged (scripts/git-hooks/pre-commit ~L1260). Nothing in hooks/CI runs it on the real file.
   cmd: grep -n backlog_ripeness scripts/git-hooks/pre-commit; grep -rn backlog_ripeness .github/ scripts/*.sh
F6 Heuristic count: 12 of 96 pre-commit gate blocks only self-test when their own script is staged, incl. backlog_ripeness, backlog_freshness, open_loops, oracle, archive_move_gate, recoil_public_share_gate, share_control_gate. (Classifier is approximate: some may have a separate data check elsewhere. UNVERIFIED per gate.)
F7 36 non-terminal rows have review_by in the past (oldest 2026-10-25).
F8 9 non-terminal rows cite a PR number that has merged on main (e.g. recoil-ship-twin cites 2175/2180; recoil-kairos-7s-test cites 2173).
F9 RUNNING claims older than 3 days: 4 (engagement-compounding-v0 11-08, gravity-eir-candidate-brief 11-08, gauntlet-brief-polyform 11-11, pr-design-brief-habit 11-11).
F10 Rows added per ISO week: W41 26, W42 222, W43 37, W44 48, W45 43, W46 77.
F11 PR merges per day 11-02..11-15: 7,26,13,12,11,(11-07 0),17,21,11,13,74,21,10,5. 11-12 = 74.
F12 Sync-from-main merge commits (branch pulls main back in) per week: W44 4, W45 14, W46 68.
   cmd: git log origin/main --merges --since=2026-10-26 --format='%ad %s' --date=format:%V | grep "origin/main" | grep -v "pull request" | cut -d' ' -f1 | sort | uniq -c
F13 Of 556 non-merge commits on main since 10-15: NCI:SKIP 324 (58%), scored 203, untagged 29.
F14 Of merged PRs in W46 (113), 17 (15%) are backlog bookkeeping only (chore(backlog) ... set X DONE after PR N).
F15 decision_receipt: 1,683 rows; job_id+tool_id present on ~99% since 11-01 (daily counts track merge counts: 11-12 79 receipts vs 74 merges). 1,657 (98%) carry >=1 what_unconfirmed item.
   cmd (Supabase xbbpiryokswwvcrcutge, read-only): select count(*), count(*) filter (where cardinality(what_unconfirmed)>0) from decision_receipt;
F16 Outcome closure: Outcome 10 rows (5 synthetic) vs prod Receipt 277; SessionReceipt 4 rows, all past scoreBackDate, 0 with outcome; LaneOutcome 2 (both closed).
F17 ADR-086 (two-pass induction) is DRAFT, never run on a real plan; it records Op 20 has no backlog-row adapter. Backlog row seat-backlog-row-adapter is RIPE (F4).
F18 All 5 kit-wire self-tests, kit_job_ratchet live, safe_merge self-test, backlog_status_check, operator_registry, surface_catalog and status_page_build --check pass on 3f9b9f9.
F19 The CLAUDE.md handoff (v3.146.0, 11-12) is ~50 merged PRs stale; no fragments exist; its open items 1-3 have since closed (#2180, #2209, #2210).
F20 Ripe rows by current state: HOLDING 7, OPEN 17, HELD 5, BLOCKED 1, READY 3, DONE 3. runtime/specs/backlog-status.json defines HOLDING as "Waiting on depends_on rows to clear" and READY as "OPEN and its trigger has fired / deps are clear", so 24 rows meet READY by the spec's own words. backlog_ripeness.py header: "this script detects, it never resolves. Fates stay human (NOTOMATION)"; its only write mode is --apply-closes. Readers: backlog_graph.py, open_loops.py, readiness_packet.py, reconcile_epoch.py (all on demand). scripts/scrum.py (the groom) has no ripeness input.
   cmd: grep -n ripe scripts/scrum.py; python3 scripts/backlog_ripeness.py --json

## Artifact-sourced facts (19 pinned artifacts, read 2026-11-15 by a read-only agent; UNVERIFIED unless marked)
F21 Counterpart loops stall after the draft, at the human send: harrison-followup-2026-11-09 READY ("Zach sends"), 6 days past; Brian recoil page bets dated 11-13 and 11-27, no outcome recorded; myally-step1-audit BLOCKED while the agreement doc holds 23 unaccepted suggestions from 11-09 and its own sign-by date (11-10) has passed; Louisville "DO NOW" hook (October renewal) expired, no row; PRL 1.2 receipt check-in (Aug 24) never closed, prl rows HELD since 09-26; Pilot Decks pitch (11-05) and Dioptra 11-09 prediction have NO ROW.
F22 Ex-ante probabilities live in at least 5 artifacts (Harrison, Brian, Dioptra, Bitfury, Journey Map); only Harrison has a scoring row (harrison-recoil-close-score, first check 11-16).
F23 Debt tracker (Docs Reconciliation db): 78 items, 19 open, 8 in progress, 7 "decision" (all waiting on Zach, ~40 days, no backlog row; two past their own deadlines: old-anthropic-account "Nov 1", write-lock-adr-085 "~10-13").
F24 Monetization named in 3 artifacts (Monetizable Surfaces Audit "price + pay link ~1 hr", Glass Box next move, Journey Map); rows HOLDING/BLOCKED; no price/Stripe commit since 11-11 (agent-checked git).
F25 five-person-outcome-test READY since 11-04, unclaimed 11 days; Journey Map baseline: 0 outcomes from outside users.
F26 Snapshot artifacts pinned and stale: Backlog Graph Prior Art (460 rows), Glass Box (445 rows), Scheduled-tasks dashboard (48h stale since 11-08, "not refreshed automatically").
F27 Self-named repairs with no row: Glass Box "write depends_on on unblock-only rows" (226/325 wave-0); Journey Map ~10 analytics events + G5 optional note; Eightfold Wheel 3 thin Heart factors + unscheduled 30/90-day rechecks (0 repo matches); composer visual-grammar deliverable.
F28 Privacy hygiene: passcodes in client JS (Bitfury post-call), inline (Dioptra card); phone+email in a shared pitch footer; recoil-public-share-gate (DONE) covers recoil pages only.

## Pass-1 seams (Kintsugi: each break shown with its repair; the original lines above stand as written)
S1 F6 BROKEN. 5 of the 7 named gates do check real data (backlog_freshness pre-commit:1267, oracle :40-62, archive_move_gate :1384, recoil_public_share_gate :1419, share_control_gate :1406). Verified self-test-only on real data: backlog_ripeness (:1260) and open_loops (:1289) only. The 12/96 figure is withdrawn. (Loki)
S2 F12 HELD. 68 sync merges span ~40 target branches; kit-wire is 2 of 68. General integration tax, not a stacked-branch artifact. (--since 11-09 gives 63: author vs commit date.) (Loki)
S3 F13 REFRAMED. NCI:SKIP is sanctioned for docs/handoff/chore/format by ADR-035:57-61. Candidate violations: at most 46 of 556 (8%, feat/fix/refactor SKIP touching src|prisma|operators|runtime, runtime/specs inflates it) plus 17 SKIP tags with no reason (ADR-035:28 requires one). NCI is not evidence of avoidance. (Loki)
S4 F14 BROKEN. 17 does not reproduce: 9 to 12 of 113 first-parent PRs (8 to 11%). W46 had 155 PR merges in total; 113 is the first-parent count (42 stacked). (Loki)
S5 F4/F20 BROKEN by a detector defect. scripts/backlog_ripeness.py:63-64 `_status()` reads status_note before the state enum (contradicts AGENTS.md gotcha 20). Recomputed from state: 25 ripe = HOLDING 8, OPEN 11, HELD 5, BLOCKED 1. By the spec's own words 19 (HOLDING+OPEN) meet READY, not 24. (Loki; recomputed in /tmp/claude-0/ripe_state.txt)
S6 F15 TESTED (Detective, kill line fixed first). Per-merge coverage 11-01..11-15: 109 of 113 first-parent PRs have a receipt citing them (96%, line >= 90%: HOLDS). Receipts are written by sessions, never by safe_merge.sh (safe_merge.sh:241 "Not written by this script"); 31 of 109 (28%) came via ship_docs.sh, the GitHub MCP merge or kit scripts (line >= 20%: the "safe_merge causes it" story is KILLED).
S7 Alchemist counterexample TESTED. Closing a row after its PR merges (close-time, manual, no tool): 42 DONE rows cite a merged PR vs 9 open rows that do, ~82% (upper bound). Kills "followed in proportion to tool load".
S8 Prior detections of the same gap (Librarian): _PATTERNS/2026-10-17-claims-versus-proof.md:14 (~1.1% outcomes closed); scripts/receipt_outcome_queue.py:7 (834/854 receipts with open lines, 0 resolved, 10-18); backlog row outcome-capture-rate-keel-gap DONE ("not a build gap ... humans are not closing the loop"); echo-scheduled-receipts COMPOSTED 11-05 (unmoved); backlog-fate-triage-2026-10-18 READY ~4 weeks.
S9 Counterexample to keep (Bayesian): LaneOutcome 2 of 2 closed (n=2).
