<!--
session: claude-docs-reconciliation-orchestration
branch: claude/docs-reconciliation-next-06852d (worked from worktree orchestration-repo-cleanup-6f304f)
head: df007580
created_at: 2026-10-06T18:32:13Z
-->
> **Docs Reconciliation round (2026-10-06 afternoon): tracker decisions worked through, 15 PRs landed, Actions cost cut, integrity gate baselined and blocking.** Tracker (debt view): https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm; Issues (#1025) is now the source of truth.

## Goal / true north
Pay down tech debt and judgment calls in the Docs Reconciliation tracker in the order the critical path and premortem said, inside Zach's budget (about 75 minutes left at the time).

## What changed
- **Merge train 1** (#1030 status live read, #976 orphan audit, #959 alert_test, #964 forensic arcs, #676 checkout@7) and **train 2** (#1039, #1040, #1025), receipts `2026-10-06--pr<N>-merge-train--ZH`. Direct merges: #1031 (sage_efficacy.mjs cites), #1032 (Actions cost fix), #934 (advisory gates, path-filtered, through the train), #1034 (release_notes.py), #1036 (integrity baseline + 4 scripts archived), #932, #1027 (PM bundle, Zach's yes). #1037 merged by its own session.
- **Actions cost (P1, issue #1046):** leak-check + belief-log + generated-views folded into one `gates` job; draft PRs skip CI; `intent` only on AGENTS.md changes. Cause of the "red" PRs was the 14:18Z billing block, not code.
- **Integrity gate:** 648 failing cites across 131 of 398 live records grandfathered in `scripts/integrity_baseline.json`; `_ARCHIVE/` exempt; pre-commit now **blocks by default** (INTEGRITY_GATE_BLOCK=0 opts out once). Whole tree exits 0, a new vapor cite exits 1.
- **Release notes:** `scripts/release_notes.py` writes `_RELEASES/<date>.md` from git (area by files touched). 09-15 to 10-06: 366 merged PRs; compass 16, operators 7. Compass is NOT wired to operators beyond an advisory SAGE pre-screen (fired 65 of 91 receipts; it feeds synthetic signal from stakes/horizon, not the question).
- **Sweeps (run directly, no chips):** icon/manifest 74 hosts x 6 paths all 200; 72 static subdomain pages have no og:image; ATS PDFs 93 of 96 clean by poppler (not a real ATS).
- **Tracker/Issues sync:** relabelled 20 and closed 14 GitHub issues to match today's edits (debt push only creates missing issues; it does not update existing ones).
- **Sessions archived (harvested, clean):** forensic arcs, job tracker, key audit, orphan audit, dup docs, induct backlog, Issues SSOT, receipt efficacy, DeFi review.

## Current state
- main tip `df007580`; CI on `b23f8ce1` and `df007580` was still running at handoff. Production deploy of `d2af7045` was READY earlier; later deploys unconfirmed.
- Open PRs: #1042, #1043, #1045 (other sessions' NFTT/LinkedIn drafts), #730 draft, #557 better-sqlite3 major.

## Decisions made
- Archive exemption + baseline (not bulk qualify); flip block now. Park #700. Archive only 4 of 17 orphan scripts (rest have tests/callers). Close pulse-oracle ADR row and Alexandria apex row. Add arcs-skills marketplace. Fix cost before landing #934. Stay in one session instead of a Fable orchestrator.

## Open decisions (waiting on Zach)
1. Old Anthropic keys: move/delete remaining copies, then revoke (list in #958).
2. ADR-085 acceptance and step 3 about 2026-10-13.
3. Confidence claim unit v1 (spec-table diff to draft) and Librarian prescore calibration (sample to lay out): chosen today, not started.
4. og:image per host: which of the 72 static hosts should unfurl.
5. PM session worktree holds 2 untracked files (Nous Hermes resume + cover HTML in _ARTIFACTS/forge-nous-hermes-pm/): commit or keep local before archiving that session.
6. 7 SECRETLY-DONE backlog rows: `scripts/backlog_ripeness.py --apply-closes` (not run).
7. Lattice epoch (2026-09-03) is judgment layer; needs a human re-author.

## Open (other)
1. **ADR → Queue workflow fails on any push touching 2+ ADR files** (multi-line GITHUB_OUTPUT; runs 37499499209, 37481234702, 37472043262). Fix: heredoc output.
2. `backlog_issue_sync.py debt` has no update/sync step; until it does, tracker edits must be mirrored to issues by hand (done once today), and `debt pull` only stamps `synced`.
3. Baseline-only-shrinks check; measure Actions minutes saved on real PRs; fold the `changes` job.
4. status.arcs.care: map each section to its source (stamped, live, Issues-derived, hand-written) and add a check for stale hand-written dated numbers.
5. adr_cite_lint: 82 suspects not hand-verified; decide manual aid vs advisory CI.
6. frontend-design plugin is project-scoped to the stale /Users/zharris/arcs clone; disable there or leave.
7. Cheap adds: CLAUDE.md rule "run local security-review before opening a PR"; note the nci-scoring duplicate decision (keep repo copy). fewer-permission-prompts as its own session. FieldOS explorer. Supabase billing page check. 8 scheduled-task sessions left unarchived.

## Next action
Confirm CI and the Vercel deploy are green on main `df007580`, then fix the ADR → Queue workflow.

## Cold-start recipe
- `python3 scripts/release_notes.py --since 2026-10-06` for what landed; tracker link above for debt; `_QUEUE/induced-backlog.jsonl` + `python3 scripts/backlog_ripeness.py` for ripe work.
- Merge path: `scripts/merge_train.sh --lock --yes <PRs>`; it refuses a PR with any failed or cancelled check (re-run stale reds first).
- Premortem model: `_STATE/2026-10-06-docs-recon-montecarlo.py` (priors are subjective).
