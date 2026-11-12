---
title: SSOT cross-store reconciliation, 2026-11-12
row: ssot-cross-store-reconcile
measured_at: 2026-11-12T18:12Z (oracle now), origin/main 1992584b
mode: measured read-only; fixes 1 and 2 applied 2026-11-12 18:25Z on Zach's "Yes, apply both"
---

> **Applied 2026-11-12 18:25Z** (Zach: "Yes, apply both"). The `reconcile` subcommand in section 4.2 is built (`scripts/backlog_issue_sync.py`, self-test 24/24, code in PR 2205) and was run with `--apply` against origin/main `4e4b6cc6`: 25 issues closed (11 DONE as completed, 14 COMPOSTED or SUPERSEDED as not planned, each with a comment naming its row) and 32 labelled (31 `held`, 1 `blocked`). A rerun plans 0 actions, and open issues dropped from 131 to 106. The code is under separate review in PR 2205. Fixes 6 and 7 were applied later on Zach's "Yes, apply them", relayed by the parent session: the 3 STALE rows were restated from git with their states kept (the check counted `doc-gate-false-positive-cleanup` twice, so there are 3 rows, not 4), and `backlog-graph-prior-art` was filed as DONE after the fact. The STALE check still flags those 3 rows because it fires on any cited PR that has merged or closed, even when the cite is history. Fix 5 is left to the recoil orchestrator. Fixes 3, 4 and 8 are not applied. Wiring and the oracle namespace are filed as rows `open-loops-ssot-drift-line` (OPEN) and `oracle-sync-namespace` (HELD).

# SSOT cross-store reconciliation, 2026-11-12

**Why.** Nine stores record what is open, closed or parked: backlog rows, GitHub issues, the debt tracker artifact, the surface catalog, pinned artifacts, the receipt ledger, sessions, open PRs, and Hermes. Today's groom moved dozens of rows and none of those moves reached GitHub. Several harnesses write to these stores at the same time, so drift will keep piling up unless one store owns each kind of fact and every other store follows it.

**What.** One read-only diff of every store against the store that owns that fact (ADR-065: the backlog owns rows and issues are a copy of it; GitHub issues own debt). It gives a mismatch count per store pair, a proposed fix for each, one timeline, and a sync design. No fix has been applied.

**Why now.** Zach found the drift on 2026-11-12. Every GitHub issue copied from a row was last touched in one bulk sync at 2026-10-11 01:25Z, and every row changed after that. The gap only grows.

**How.** Before: Zach reads section 1 (counts) and section 4 (design). During: on his go, a session runs the fixes in the section 3 order. After: the check runs every morning inside `/loops`, so new drift shows up within a day. How to read this page: section 1 is the summary, section 2 is the timeline, section 3 lists each fix, section 4 is the design, and the appendix holds the full per-item tables.

## 1. Mismatch count per store pair

| pair | owner (SSOT) | mismatches | fix direction | moved last |
|---|---|---|---|---|
| backlog row ↔ GitHub issue: row closed, issue open | backlog | **25** | backlog → issue: close | backlog, every case (rows 10-18 to 11-12, issues frozen 10-11) |
| backlog row ↔ GitHub issue: row parked, issue unlabelled | backlog | **32** | backlog → issue: add `held` / `blocked` label | backlog, every case |
| backlog row ↔ GitHub issue: row live, issue closed | backlog | 0 | none | |
| row `gh_issue` names a missing issue | backlog | 0 | none | |
| GitHub issue with no row, no `debt` label, still open | neither (pre-backlog tracker, J-series and blocking-root) | **31** | Zach triages: make it a row, make it debt, or close it | issues, all last touched 2026-10-11 (bulk relabel) |
| GitHub issue CLOSED but still carries `status:open` / `status:in-progress` | issue (debt) | 3 (#1014, #1002, #993) | drop the stale label | issue |
| debt issues ↔ debt tracker `debt` collection | issues | 0 state, **1** title (#1000), 36 docs whose `synced` stamp is older than the issue's last update | issue → artifact: `debt pull` | issue (latest 2026-11-06 #1000; last pull 2026-11-02 21:54Z) |
| surface catalog ↔ live routes | routes (code) | 0 (`--check` PASS; 39 of 39 `src/app` pages catalogued) | none. Not mismatches but worth noting: 15 unrouted public HTML files, 21 rows with no purpose text | catalog regenerated 2026-11-12 17:30Z |
| pinned artifacts ↔ backlog rows | rows | 14 of 17 pinned have no row; 7 of those are cited nowhere in the repo | Zach decides: add a row, unpin, or leave as a reference pin (counterpart pages need no row) | n/a |
| merged PRs ↔ `decision_receipt` | receipts | **127** of 1,580 merges since 2026-09-10 cited by no receipt (Sep 69, Oct 54, Nov 4; 3 are from today and may still be pending: #2191, #2195, #2197) | backfill receipts only where the gap matters (Sprint 5 coverage), not one by one | git |
| receipt `job_id` names a row that does not exist | rows | **1** (`backlog-graph-prior-art`, receipt `2026-11-06--backlog-graph-prior-art-pr2033--ZH`) | add the row as DONE, or a superseding receipt (ledger is append-only) | receipt |
| row has a receipt but is still OPEN/READY/RUNNING | rows | 26 candidates (receipts can record partial progress; each needs a look, not an auto-close) | human review | mixed |
| sessions ↔ rows | rows | 196 of 268 non-recurring sessions match no row; 11 active since 11-10 | the row-before-session rule, enforced at start (section 4) | sessions |
| rows behind merged PRs (found through sessions) | rows | **2**: `recoil-runner-beats` READY while #2189 merged 17:25Z; `backlog-merge-driver-by-id` RUNNING while #2188 merged 17:25Z | owner session (recoil orchestrator) sets DONE | git |
| open PRs ↔ rows | rows | **13** of 13 open PRs cited by no row (by number or branch) | row-before-session rule | PRs |
| rows citing merged or closed PRs (`backlog_status_check --gh`) | rows | **4** STALE: `asm-009-net-direction-decided` (#598 closed), `doc-gate-false-positive-cleanup` (#1982, #934 merged), `phosphor-rc1-firefox-verify` HELD (#1619 merged) | row owner re-states the row | git |
| Hermes ↔ every store | git | 0 writes. FTS index: 8 messages since 10-15, one session today (a read-only `session_search` probe at 17:34Z). `kanban.db`: 0 tasks. Every commit on main since 10-15 carries a Claude trailer except 8 (5 dependabot, 3 by Zach). Hermes claims carry no weight; git confirms no Hermes commits. | none | n/a |

The findings to act on are the 57 issue fixes (25 closes and 32 labels), the 2 rows behind merged PRs, the 4 STALE rows, and the 1 dangling `job_id`. The 31 orphan issues, 14 unrowed pins and 26 receipt-backed live rows are decisions for Zach, not syncs a script should make.

## 2. One timeline (git commit time, oracle counters)

Oracle at measurement: `adr 93` (last minted 2026-11-04 `1ff49bf8`), `handoff 146` (2026-11-12 16:24Z `170e0bfa`), `seed 18` (2026-10-20), `tao 287` (2026-10-14). No oracle namespace exists for rows, issues, receipts or syncs, so the stores have no shared sequence number. Wall-clock commit time is the only common key today (see 4.3).

| when (UTC) | store | event | consequence |
|---|---|---|---|
| 2026-10-06 15:01 to 15:03 | debt artifact | `debt push` / first sync of 78 docs | baseline |
| 2026-10-07 | debt artifact page | page last published | page shell is 5 weeks old; data newer |
| 2026-10-11 01:25 to 01:26 | GitHub | bulk sync touches all 75 row-mirrored issues (#594 to #611, #1175 to #1225) and relabels the legacy J-series | **last time any row issue changed** |
| 2026-10-18 to 2026-11-12 | backlog | 25 linked rows reach DONE/COMPOSTED/SUPERSEDED (commits `da0bcf63`, `872b7cb0`, `a8b37753`, `b2612f4e`, `6edb25bb`, `f70c2226`, `92024360`, `3542b4d9`) | 25 issues left open |
| 2026-11-02 to 2026-11-12 | backlog | 32 linked rows parked HELD/HOLDING/BLOCKED (mostly `6edb25bb` 11-04, last `3542b4d9` 11-12) | 32 issues still look open and active |
| 2026-11-02 21:54 | debt artifact | `debt pull` | 77 of 78 titles match from here on |
| 2026-11-06 00:29 | GitHub (debt) | #1000 retitled | artifact title one pull behind |
| 2026-11-06 | receipt ledger | receipt with `job_id` `job:backlog:backlog-graph-prior-art`; no such row | dangling atom (the pinned "Backlog Graph Prior Art" artifact has no row either) |
| 2026-11-12 16:14 | backlog | groom commit `3542b4d9` moves rows, two of them linked (#1187, #1223 to SUPERSEDED) | GitHub not told |
| 2026-11-12 17:25 | git | #2188 and #2189 merge | their rows stay RUNNING / READY |
| 2026-11-12 17:30 | catalog | surface catalog regenerated | check passes |
| 2026-11-12 17:44 to 18:09 | git | #2191, #2195, #2197 merge | no receipt yet (may be pending) |
| 2026-11-12 18:12 | this report | measured | |

The direction is the same every time: the owning store (backlog, or GitHub for debt) moved, and its copy did not follow. No copy moved past its owner, so no hand-edit on GitHub needs to be pulled back into a row. Applying the fixes in the owner-to-copy direction is safe.

## 3. Proposed fixes, in order (none applied)

1. **Close 25 issues** (appendix A1): DONE → `--reason completed`; COMPOSTED/SUPERSEDED → `--reason "not planned"`. Each close comments with the row id, state, status note, and the commit that changed the row. Two-way door (an issue can be reopened).
2. **Label 32 issues** (appendix A2): create label `held`; HELD/HOLDING get `held`, BLOCKED gets `blocked`; drop `status:open` on those.
3. **Drop 3 stale `status:*` labels** on closed debt issues #1014, #1002, #993.
4. **Run `debt pull`** and apply its batch to the tracker, which fixes the #1000 title. This is an artifact write, so it needs Zach's go.
5. **Two rows behind merged PRs**: message the recoil orchestrator ([local_6d106b64](#local_6d106b64)) to set `recoil-runner-beats` and `backlog-merge-driver-by-id` to DONE. This session does not edit rows it does not own.
6. **4 STALE rows**: the owners re-state them (`backlog_status_check --gh` names them).
7. **Dangling `job_id`**: add row `backlog-graph-prior-art` as DONE (it served PR 2033), so the receipt resolves. Rows can be appended; receipts cannot be edited.
8. **Zach decides** (no script action): 31 orphan issues (appendix A3), 14 unrowed pins, 26 receipt-backed live rows, and whether to backfill receipts for the 127 uncited merges.

## 4. Sync design (proposal)

### 4.1 Who owns what

| fact | SSOT | copies | sync direction |
|---|---|---|---|
| work item state (open, parked, closed) | backlog row on origin/main | GitHub issue (opt-in `gh_sync` rows), `/loops`, backlog pages | row → issue, one way |
| debt item | GitHub issue (label `debt`) | tracker artifact `debt` collection | issue → artifact, one way (`debt pull`) |
| served surface | code (`next.config.ts`, `src/proxy.ts`, `src/app`) | `surface-catalog.json`, surfaces page | code → catalog (existing `--check`) |
| a merge happened | git | `decision_receipt` | git → receipt (receipt cites merge sha + an existing `job_id`) |
| a number (ADR, handoff, seed, tao) | `_SEEDS/_oracle.json` on origin/main | every file that cites it | oracle first |

A copy never writes back to its owner. A copy that is newer than its owner counts as a hand-edit: flag it and never adopt it silently. The one exception is debt, where the issue is the owner.

### 4.2 Extend `scripts/backlog_issue_sync.py` (no new tool)

Unbuilt proposal. Ground: today the script is create-only and never rewrites an issue (its docstring, `scripts/backlog_issue_sync.py` lines 2-12, on origin/main `1992584b`), which is why the 25 closes in appendix A1 never happened. Add a `reconcile` subcommand next to `debt pull`:

- `reconcile --check`: read-only; exit 1 on any row/issue mismatch; print the counts in section 1's first five rows. Pure `gh issue list` plus the backlog file.
- `reconcile --dry-run` (default): print each planned `gh` call.
- `reconcile --apply`: for `gh_sync` rows only:
  - row in DONE → close `completed`; COMPOSTED/SUPERSEDED → close `not planned`; comment with row id, state, status note and the commit that last changed the row.
  - row in HELD/HOLDING → label `held`; BLOCKED → `blocked`; remove the label when the row leaves the parked states.
  - row live but issue closed → **report only** (reopening is Zach's call).
  - replace the five `status:*` labels with one label that mirrors the row state (`state:<enum>`), so an issue shows exactly one state.
  - never write to the backlog file (no write-back fields, so no new merge conflicts). The issue comment carries the provenance.
- `--self-test` covers each branch with the stubbed `gh` it already has.

Out of scope here: copying all 541 rows to issues. Opt-in stays opt-in (75 rows today). Mirroring 148 HELD rows would add noise, not signal.

### 4.3 Cross-harness write order

Every harness (Claude Code, Hermes, scheduled tasks) follows the same four steps:

1. **Number first.** Any new number comes from `python3 scripts/oracle.py next <ns>` and lands in a pushed `_SEEDS/_oracle.json` commit. git's non-fast-forward rejection is the lock; on rejection, fetch and mint again.
2. **SSOT second.** The row change (or code change) merges to origin/main. git is the lock for rows too, and PR #2188's merge-by-id driver removes the by-hand resolution step.
3. **Copies third, from origin/main only.** Issue close or label, `debt pull`, catalog regenerate. A copy writer reads `git show origin/main:…`, never a worktree file (AGENTS.md gotcha 14).
4. **Receipt last.** It cites the merge sha and a `job_id` that already exists on main (the one dangling `job_id` here came from skipping this check).

Attribution: every commit carries a harness trailer (Claude's `Co-Authored-By` already does; Hermes adds `Harness: hermes`), so the timeline can name the writer. Proposed addition: an oracle namespace `sync` that `reconcile --apply` mints once per run and writes into each issue comment. That gives copies and owners one shared sequence number instead of wall-clock time alone.

### 4.4 Wire it into an existing recurring run (no new cron)

- **Morning `/loops` note** (`scripts/open_loops.py`, scheduled task `arcs-open-loops-morning-note`): it already calls `gh` for PR loops. Add one line from `backlog_issue_sync.py reconcile --check --json` plus `backlog_status_check.py --check --gh`: "SSOT drift: 25 to close, 32 to label, 4 stale rows". Zero drift prints nothing.
- **Night-moves** stays git-only by design (`night_moves_gather.sh` says "no network"), so it is not the place for `gh` calls.
- **Apply step:** a session runs `reconcile --apply` after Zach's yes in that session. Closing an issue is a two-way door, so Zach could later grant a standing approval for the close and label classes only. Until he does, every run asks.
- **MCP-only stores** (debt artifact, receipts, sessions, artifact list) cannot be reached from a script. The `/scrum` groom or the weekly cruise-control pass covers them with the same pair checks as this report.

### 4.5 Rows to file on approval

- `backlog-issue-reconcile-mode`: build 4.2 (S, about 2 h; self-test first).
- `open-loops-ssot-drift-line`: 4.4 wiring (S).
- `oracle-sync-namespace`: 4.3 shared sequence (S; needs Zach's go on a new namespace).

## Method and limits

- Row "last changed" is the last commit whose diff touches a line with that row's id (`git log -G`). That catches any edit to the row, not only a state change.
- PR-to-receipt matching looks for the PR number in `receipt_id` or `refs`. A receipt that names a merge only by sha counts as missing, so 127 is an upper bound.
- The session-to-row matching is `backlog_graph.py --sessions` heuristic, which matches title/branch to row id. It missed the two recoil sessions above, which have rows.
- The 36 debt docs with old `synced` stamps match on state and title; whether their bodies or labels differ was not checked.
- Pinned-artifact rows were found by grepping the artifact id in rows and repo files only; a row could name an artifact by title.
- Hermes was checked through its FTS index (`messages_fts_trigram`, read-only), not the sessions table alone (AGENTS.md gotcha 14a).

## Appendix

### A1. Row closed, issue open (25). Proposed fix: close the issue.

| row | issue | row state | row last changed (commit) | issue last updated | proposed close reason |
|---|---|---|---|---|---|
| `receipted-fears-stunt` | #1202 | DONE | 2026-10-18T14:17 `da0bcf63` | 2026-10-11T01:25 | completed |
| `accountable-copypasta-card` | #1203 | DONE | 2026-10-18T14:17 `da0bcf63` | 2026-10-11T01:25 | completed |
| `handoff-postmerge-ci-936` | #1221 | DONE | 2026-10-18T14:17 `da0bcf63` | 2026-10-11T01:26 | completed |
| `orphan-seeds-curation` | #1175 | DONE | 2026-10-20T14:09 `872b7cb0` | 2026-10-11T01:26 | completed |
| `tao-backfill-066-067` | #1176 | DONE | 2026-10-20T14:09 `872b7cb0` | 2026-10-11T01:26 | completed |
| `adr-085-acceptance-redecide` | #1215 | DONE | 2026-10-20T14:09 `872b7cb0` | 2026-10-11T01:26 | completed |
| `vico-arcs-care-battle-card-ammo` | #1191 | COMPOSTED | 2026-10-21T10:16 `a8b37753` | 2026-10-11T01:25 | not planned |
| `magic-patterns-true-up-hud` | #1222 | COMPOSTED | 2026-11-02T20:18 `b2612f4e` | 2026-10-11T01:26 | not planned |
| `jobs-arcs-care-recruiter-workflow-fork` | #1192 | COMPOSTED | 2026-11-04T10:02 `6edb25bb` | 2026-10-11T01:25 | not planned |
| `pond-etch-protocol-serialize-molt-test` | #1200 | COMPOSTED | 2026-11-04T10:02 `6edb25bb` | 2026-10-11T01:26 | not planned |
| `lore-franchise-ephemera-surface` | #1204 | COMPOSTED | 2026-11-04T10:02 `6edb25bb` | 2026-10-11T01:25 | not planned |
| `arcs-olympics-first-games` | #597 | COMPOSTED | 2026-11-04T10:02 `6edb25bb` | 2026-10-11T01:25 | not planned |
| `compass-mobile-timeout-recover-receipt` | #1195 | DONE | 2026-11-04T14:40 `f70c2226` | 2026-10-11T01:25 | completed |
| `outcome-loop-timing-wiring-horizon-reviewdate-blind` | #1198 | DONE | 2026-11-04T14:40 `f70c2226` | 2026-10-11T01:25 | completed |
| `unfold-uses-librarian` | #604 | DONE | 2026-11-04T14:40 `f70c2226` | 2026-10-11T01:26 | completed |
| `forensic-arc-reconstruction` | #1214 | DONE | 2026-11-04T14:40 `f70c2226` | 2026-10-11T01:26 | completed |
| `receipt-test-real-tag` | #1217 | DONE | 2026-11-04T14:40 `f70c2226` | 2026-10-11T01:25 | completed |
| `greenhouse-arcs-care-seedbank-surface` | #1182 | COMPOSTED | 2026-11-05T10:27 `92024360` | 2026-10-11T01:25 | not planned |
| `algorethics-in-scope-benchmark` | #1185 | COMPOSTED | 2026-11-05T10:27 `92024360` | 2026-10-11T01:26 | not planned |
| `autopilot-arcs-care-battle-card-ammo` | #1190 | COMPOSTED | 2026-11-05T10:27 `92024360` | 2026-10-11T01:25 | not planned |
| `case-squads-multiplayer` | #1206 | COMPOSTED | 2026-11-05T10:27 `92024360` | 2026-10-11T01:25 | not planned |
| `freshness-zeno-ceiling` | #1207 | COMPOSTED | 2026-11-05T10:27 `92024360` | 2026-10-11T01:26 | not planned |
| `echo-scheduled-receipts` | #1208 | COMPOSTED | 2026-11-05T10:27 `92024360` | 2026-10-11T01:26 | not planned |
| `compass-model-agnostic-provider-abstraction` | #1187 | SUPERSEDED | 2026-11-12T11:14 `3542b4d9` | 2026-10-11T01:25 | not planned |
| `prl-golive-empty-email-guard` | #1223 | SUPERSEDED | 2026-11-12T11:14 `3542b4d9` | 2026-10-11T01:26 | not planned |

### A2. Row parked, issue open with no held label (32). Proposed fix: add label `held` (BLOCKED rows: `blocked`).

| row | issue | row state | row last changed (commit) | issue labels |
|---|---|---|---|---|
| `anthropic-spend-monitor` | #1212 | BLOCKED | 2026-11-02T20:18 `b2612f4e` | none |
| `req-reality-dim-board-and-champion` | #1178 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `scan-huds-migrate-to-tokens-css` | #1179 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `tokens-css-vs-ds-font-stack-drift` | #1180 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `mcp-connector-wrapper-adr-076` | #1181 | HELD | 2026-11-04T10:02 `6edb25bb` | sev:P1 |
| `state-of-union-dashboard-ahmed-impeccable-pass` | #1183 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `session-drift-detection-eval` | #1184 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `embedding-storage-target-pgvector-vs-duckdb` | #1186 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `operator21-gaussian-process-posterior-then-rt-core` | #1188 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `gauntlet-wargame-embedding-dedup` | #1189 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `svc-sage-should-it-exist-decision` | #1193 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `nftt-story-factory-index-instructions-stale` | #1196 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `nftt-template-kintsugi-contrast-and-label-heuristics` | #1197 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `moral-to-gate-alchemy-pipeline` | #1199 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `hypothesis-generator-plg-surface` | #1201 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `conviction-chips-calibration` | #1205 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `rc-ops-001-graduation-ruling` | #594 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `hyperstition-pipeline-first-graduate` | #596 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `tao-renders-regenerated-from-projection` | #599 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `lore-tao-cross-cite` | #600 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `accountant-external-cohort-nonzero` | #602 | HOLDING | 2026-11-04T10:02 `6edb25bb` | none |
| `accountant-calibration-curve` | #603 | HOLDING | 2026-11-04T10:02 `6edb25bb` | none |
| `asm-003-cold-molt-decided` | #605 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `operator-13-choreographer-unblock` | #606 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `choreographed-pickup` | #607 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `operator-25-first-catch` | #609 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `adr-index-drift-repair` | #611 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `memory-seven-axis-scorecard` | #1209 | HELD | 2026-11-04T10:02 `6edb25bb` | none |
| `nftt-monday-fde-takehome-build-log` | #1225 | HELD | 2026-11-04T10:02 `6edb25bb` | sev:P1 |
| `jsonl-ledgers-merge-union` | #610 | HELD | 2026-11-05T09:35 `fde2dce9` | none |
| `agent-receipts-audit-first-conversion` | #601 | HOLDING | 2026-11-05T10:27 `92024360` | none |
| `swipe-left-rationale-loop` | #1177 | HELD | 2026-11-12T11:14 `3542b4d9` | none |

### A3. Open issues with no backlog row and no debt label (31). Proposed fix: Zach triages each (row it, debt it, or close).

- #645 compass: model invents a prior score ('SAGE signal (NCI 94, 
- #542 [blocking-root] tripwire
- #541 [blocking-root] fe-smoke
- #540 [blocking-root] smoke
- #539 [blocking-root] leak-check
- #171 [security] J12 targets dropped tables (pathogen_log/immune_s
- #99 [security] J25: recursion/termination audit of self-referen
- #97 [product] J23: freshness stamps on all derived/cached surfa
- #96 [security] J22: MCP server identity pinning (churning IDs a
- #94 [refactor] J18: rename scoped agent types to generic primit
- #93 [security] J16: gather robustness: explicit consented input
- #92 [security] J15: cheaper verify: Sonnet first-pass refute, O
- #91 [research] J3: falsifiability harness: make the eval matrix
- #90 [security] Step-up auth roadmap: TOTP optional layer, WebAu
- #88 [governance] DEWY commit stamp: NCI/receipt provenance in c
- #87 [governance] Drift Sentinel: detect entropy-masquerading-as
- #86 [product] Receipt save prompt: soft-auth nudge (largest PLG
- #85 [product] Outcome handler: PATCH /api/receipts/[id] (close 
- #84 [security] J11: /ultrareview enforces the ADR-032 conforman
- #83 [security] J13: dual-control handshake for routine decision
- #82 [security] J12: wire Skeptic Sentinel verdicts into pathoge
- #81 [security] J20: Skeptic Sentinel as a reusable operator (pr
- #80 [security] J14: global write-lock serializability (Yoav pro
- #79 [security] J19: harden /api/compass (input validation + rat
- #78 [product] Case study social-proof section: Dan approved (cl
- #77 [security] J2: repo split DECIDED (ADR-036); execution owne
- #76 [security] Enable branch protection on main (concurrent-sess
- #75 [security] Rotate overdue secrets: Supabase DB password + Re
- #74 [human] Add ANTHROPIC_API_KEY to GitHub Actions Secrets (ena
- #73 [human] Add GITHUB_TOKEN to Vercel to tighten /api/pulse rat
- #72 [human] Set INTERNAL_EMAILS in Vercel to gate /internal to t
