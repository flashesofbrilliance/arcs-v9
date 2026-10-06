# Arc: jobs (reconstructed 2026-10-06)

> Zach's job search grew from hand-built candidacy bundles (Comet in August, Blacksmith and the
> RecruitHaus recruiter tier in early September, Schriner/Oxenham and VICO in mid September) into a
> machine: jobs.arcs.care (the Alert Swipe Board), a bridge employer index, a scheduled morning
> intake task, and the Job Factory slices (culture evidence, Missed state, drift, autonomy,
> model-health) merged 2026-10-05 and 2026-10-06. Every tailored resume now has an ATS-plain
> companion. The live bottleneck is not code: the Anthropic API workspace cap blocks every model
> route (scoring, forges, the 11 shortlist resume cuts), so the morning task was split so intake
> keeps running without a model. Two applications (Upside, Tenex) sit ready for Zach to send.

## Goal

Turn inbound job alerts and recruiter threads into a small number of well-evidenced, honestly
tailored applications that Zach sends himself: intake without gaps, scoring that cites evidence,
resumes that never overclaim, and nothing sent on his behalf.

## What changed

- **v3.37.0 (2026-08-17):** Comet Technical PMM application in `_ARTIFACTS/resume-comet/` (designed
  resume, ATS-plain twin, 4-facet pre-send gauntlet). resume-tailor skill v0.2 pushed to its own repo
  (`flashesofbrilliance/resume-tailor-skill`).
- **v3.48.0 (2026-08-29):** live pursuit state moved to memory `arcs-job-search-pipeline`.
- **v3.52.0 to v3.53.0 (2026-09-02 to 09-04):** Blacksmith candidate bundle; recruiter-enablement
  tear sheet for RecruitHaus; growth-ai.arcs.care family live; RecruitHaus ammo tier gated at
  `/ammo` by a shared passcode env var (`src/lib/ammo-gate.ts`, `/api/recruithaus/unlock`).
- **v3.60.0 (2026-09-11):** resume.arcs.care meta description filled (#404).
- **v3.61.0 (2026-09-13):** bridge employer-quality index: 403 names from 5 lists, 578 `bridge_scan`
  rows live on jobs.arcs.care unscored (`_STATE/job-search/employer-index/README.md`).
- **v3.62.0 (2026-09-14):** Schriner/Oxenham recruiter pitch and resume bundle at schriner.arcs.care;
  lesson "technical cut must keep leadership scope".
- **v3.65.1 to v3.65.2 (2026-09-23 to 09-24):** VICO VP of Engineering candidacy fact-checked, VP
  tonality stripped per the recruiter, memo, resume and ammo pages merged; kept off the public build log.
- **v3.81.0 (2026-10-05):** Job Factory spec gauntleted from the Sept 2025 prototype. Slice 1 culture
  evidence (#757, receipt `2026-10-05--job-factory-slice1-culture-evidence-pr757--ZH`). Morning task
  found dead since 09-11 (main checkout on a dirty branch); moved to a detached worktree
  `.claude/worktrees/morning-jobs` with a loud preflight.
- **v3.83.0 (2026-10-05):** swipe made admin-only (#766, receipt `2026-10-05--swipe-admin-only-pr766--ZH`).
- **v3.90.0 (2026-10-05):** slices 2, 3, 4, 6, 7 (#771, #761, #773, #775, #769; receipts
  `2026-10-05--pr<N>-merge-train--ZH`): Missed state, backlog drift, intake-stall signal, autonomy
  read. #784 FDE handoff (receipt `2026-10-05--fde-handoff-pr784--ZH`): 52 bridge rows had never been
  scored under target-role-scan. #789 job routes on the current writer model plus
  `GET /api/jobs/model-health` (receipt `2026-10-05--job-routes-model-migration-pr789--ZH`). #846
  Tenex bundle and Upside overclaim fixes (receipt `2026-10-05--tenex-bundles-upside-overclaims-pr846--ZH`).
  #839 Role column readable on desktop.
- **v3.99.0 (2026-10-06):** Upside cover letter gauntleted (#870, `1fa411ff`, receipt
  `2026-10-05--upside-cover-gauntlet-pr870--ZH`). ATS companions for every tailored resume (#886,
  `d5652d48`, receipt `2026-10-06--ats-companions-all-pr886--ZH`): `scripts/resume_ats_render.py`
  had silently dropped Experience, Education, pillars and OSS on forge print-base resumes; 87 new
  `-ats.html/.pdf`. iCloud `ARCS/resumes/ATS/` holds 96 ATS PDFs.
- **v3.103.0 (2026-10-06):** Missed-pile Undo plus newest-listed sort (#895, `df3d79b9`, receipt
  `2026-10-06--jobs-date-sort-undo-clear-pr895--ZH`). Intake caught up after 25 days: 95 alert
  emails (09-11 to 10-05), 422 unique rows.
- **v3.106.0 (2026-10-06):** morning task split (outside the repo): model-health gates only scoring
  and forges; Gmail intake, consume, prune and drift still run on a model 503.
- **v3.108.0 (2026-10-06):** pipeline token compared in constant time (#906, `0fbcc9e3`, receipts
  `2026-10-06--jobs-token-timingsafe-pr906--ZH` and `--jobs-token-timingsafe-merge-pr906--ZH`);
  live wrong tokens return 401.
- **v3.112.0 (2026-10-06):** one-time check `check-morning-jobs-report-2026-10-07` scheduled.

## State

- All PR SHAs cited above are on origin/main (verified with `git merge-base --is-ancestor`).
- jobs.arcs.care serves from the arcs-v9 project; `/api/jobs` rejects bad tokens with 401 (per v3.108.0).
- Scheduled tasks present: `arcs-job-search-loop-retargeted-alerts` and
  `check-morning-jobs-report-2026-10-07` (verified `ls ~/.claude/scheduled-tasks`).
- API workspace cap still blocks scoring, forges, slop-eval and the 11 shortlist cuts until raised
  or 2026-11-01 (unverified live today).
- 677 scored rows are hidden behind the Missed-pile clear until Zach clicks Undo clear (unverified).
- Upside: titles confirmed by Zach 2026-10-06, ready to send. Tenex Senior FDE bundle ready in iCloud
  `ARCS/resumes/tenex-senior-forward-deployed-engineer/`, blocked on the founder first name.
- Recruiter threads (Schriner/Oxenham: VICO and Autopilot) live in memory
  `project_joe_schriner_oxenham_autopilot_vico` (last /recoil-close 2026-10-04).
- resume-tailor skill fold-back of the leadership-scope lesson is done (commit 89278b2 (separate repo, not arcs-v9) in the
  separate `resume-tailor-skill` repo, "hybrid-role completeness gate").

## Decisions

- Zach sends every application himself; Claude drafts only.
- Never fill a counterpart name from a web search: TENEX.AI (Florida cybersecurity) is not Tenex Labs.
- A technical cut keeps leadership scope.
- Every tailored resume ships an ATS-plain companion; the kintsugi design gate skips pages with the
  renderer's generated ATS header (Zach's call).
- Resumes state New York Metro only for location.
- Intake must not depend on a model: model-health gates scoring and forges only.
- Run the morning task from its own detached worktree at origin/main, never the main checkout.
- A stale queue may be a dead intake: check the intake watermark before blaming scoring.
- Granola summaries can move a number between speakers: re-read the verbatim transcript.
- Swipe is admin-only; candidacies (VICO) stay off the public build log.

## Open

1. Read the 2026-10-07 check: the report's first line should be `STATUS: PARTIAL model gate
   usage_limit` with intake counts; if intake did not run, the prompt split failed.
2. Zach: click Undo clear on jobs.arcs.care (677 scored rows hidden).
3. Zach: send Upside; supply the Tenex founder first name, then send Tenex.
4. Raise the API workspace cap (or wait to 2026-11-01), then run the 11 shortlist resume cuts
   (`forge_edit_from_seed.mjs --jobid <id>` plus location and overclaim fixes; shortlist
   `_STATE/job-search/missed-shortlist-2026-10-05.md`).
5. Add the autonomy read (`GET /api/jobs/autonomy`) to the morning task (#773 is merged).
6. Thread 2 scoring of the `bridge_scan` rows and the H1 to H4 denominator reconcile in
   `_STATE/job-search/hypothesis-ledger.md` (unverified whether done).
7. No ATS PDF has been run through a real portal parser; Blacksmith and VICO ATS omit the
   strengths panel.
8. Zach: VICO and Autopilot recruiter follow-ups (see memory slug below).

## Next action

Read the output of `check-morning-jobs-report-2026-10-07` and confirm intake ran under the split gate.

## Cold-start

- Code: `src/lib/jobs.ts`, `src/app/api/jobs/*` (drift, autonomy, model-health), `src/lib/ammo-gate.ts`,
  `scripts/resume_ats_render.py`, `runtime/specs/target-role-scan.json`.
- State: `_STATE/job-search/` (employer-index, shortlists, hypothesis-ledger, forge-cost-ledger.jsonl).
- Scheduled task prompt: `~/.claude/scheduled-tasks/arcs-job-search-loop-retargeted-alerts/SKILL.md`.
- Commands: `git log origin/main --oneline -i --grep=jobs`; `gh pr view 895`; `curl -s jobs.arcs.care/api/jobs/model-health`.
- Backlog ids: `jobs-arcs-care-recruiter-workflow-fork`, `resume-kinexys-regulated-digital-assets-cut`,
  `state-of-union-dashboard-ahmed-impeccable-pass`.
- Memory: `arcs-job-search-pipeline`, `job-search-swipe-board`, `project_joe_schriner_oxenham_autopilot_vico`,
  `technical-cut-resume-must-keep-leadership-scope`, `resume-tailor-private-overlay-skill`,
  `resume-location-new-york-metro-only`, `recruiter-enablement-two-tier-tear-sheet`,
  `confirm-before-outbound-send-even-when-authorized`, `forge-cost-edit-from-seed-not-full-forge`.
- Skills: `resume-tailor-zach`, `recoil-close`, `forge`.
