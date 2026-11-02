---
title: Leak audit, silent recurring waste beyond the CI npm cache
date: 2026-11-02
status: PROPOSED (read-only audit; nothing changed)
scope: arcs-v9 CI, self-hosted runners, Vercel, scheduled jobs, local disk
window: CI and Vercel 2026-10-30 to 2026-11-02 (3.6 days, 300 runs, 889 jobs, 100 deploys)
---

# Leak audit (2026-11-02)

Read-only. No deletions, no workflow edits, no merges. Every number below comes from a command in the
Evidence column, run on 2026-11-02 between 14:07 and 14:40 EST. PR 1941 (npm cache off, merged 18:59 UTC)
is the baseline; numbers from before it are labeled.

## Ranked table

| # | Leak | Where | Cost | Evidence | Proposed fix | Reversible |
|---|---|---|---|---|---|---|
| 1 | One runner does all the heavy work, two sit idle | `smoke`, `fe-smoke`, `blacksmith-verify`, `a11y`, `preview-db-migrate` pinned to label `arcs-mac` (one runner) | arcs-mac ran 1,000 job-min in 3.6 days; arcs-mac-2 and -3 ran 69 and 70. fe-smoke waited 12.4 min on average before starting, 66.5 min at worst; schema-dryrun waited 53.9 min. This is wall-clock to merge, not dollars | `gh api .../actions/runs/<id>/jobs` for 300 runs, grouped by `runner_name`; started_at minus created_at | Move `smoke` to `arcs-light`: it starts no server and no Postgres (the 84f395d4 rationale for pinning is servers and DB only). For fe-smoke and the DB jobs, derive the port and container name from `$RUNNER_NAME` so they can unpin too | Yes, one-line `runs-on` change |
| 2 | Post-merge smoke on main is mostly cancelled churn | `ci.yml` push trigger, `concurrency: cancel-in-progress` | 67 smoke jobs on main pushes in 3.6 days: 48 cancelled (72%), 2 failed, 17 passed. Each one still claims the arcs-mac slot ahead of PR jobs. After PR 1941 a smoke is about 1 to 2 min, so the cost is now queue position, not compute | same job dump, split by `head_branch == main` and `conclusion` | Folds into #1: on arcs-light, main smoke stops blocking PR fe-smoke. Optional: keep only the `gates` job on push, since the PR already ran smoke on the same tree | Yes |
| 3 | CI Postgres leaves an anonymous Docker volume every run, and the container keeps running | `fe-smoke` (`arcs-ci-pg-ci`, postgres:16) and `preview-db-migrate` (`arcs-ci-pg-migrate`, postgres:17): `docker rm -f` without `-v`, no teardown step | 97 volumes, 3 in use, 4.3 GB reclaimable. 6 to 16 new volumes a day since 2026-10-18 (about 47 MB each, so 0.3 to 0.75 GB a day). Two Postgres containers stay up between runs (Up 8 min and Up 49 min at audit time) | `docker system df`; `docker volume inspect --format '{{.CreatedAt}}'` binned by day; `docker inspect arcs-ci-pg-ci` shows an anonymous volume mount | `docker run --rm --tmpfs /var/lib/postgresql/data ...` (no volume at all, faster), plus a final `if: always()` step `docker rm -fv <name>`. Old volumes: leave them until Zach says the 94 unused ones hold nothing he wants | Workflow edit: yes. Pruning the old volumes: no |
| 4 | Build dirs in worktrees whose branches already merged | `~/arcs-v9/.claude/worktrees/` (43 worktrees, 32.8 GB) | 21 worktrees on merged branches hold 12.5 GB of `node_modules` plus `.next`; all 27 worktrees with `node_modules` hold 21 GB. `du` may overcount if installs were APFS clones. Disk is at 97% (34 GiB free), worse than the 94% in the brief | `git merge-base --is-ancestor <branch> origin/main` per worktree; `du -sk <wt>/node_modules <wt>/.next` | Ask first (memory `ask-before-removing-worktrees-or-archiving`). Safest step: delete only `node_modules` and `.next` in merged worktrees (both regenerate with `npm ci` and a build); leave the worktrees and their dirty files. Full removal via the `cruft-sweep` skill, which bundles each branch first | Deleting node_modules/.next: yes (regenerable). Removing worktrees with dirty files: no |
| 5 | Vercel builds production for commits that only touch repo bookkeeping | `scripts/vercel-ignore-build.sh` SAFE_PATTERN | 60 first-parent commits on main since 10-30; the current rule skips 9. Adding `_QUEUE/ _PROPOSALS/ _HANDOFFS/ _SEEDS/ docs/ tools/ tests/ .github/ .impeccable/ WORLD.md README.md` would skip 29, about 6 fewer production builds a day. Overall rate: 93 READY deploys in 39.5 h (39 production, 54 preview), about 57 a day at 45 to 60 s each, so about 50 build-min a day | `list_deployments` (Vercel MCP, since 2026-10-30); `vercel ls arcs-v9`; replay of each main commit's `git diff --name-only` against both patterns. `src/` mentions `_QUEUE` and `_PROPOSALS` only in comments and GitHub links | Widen SAFE_PATTERN as listed. Keep `_DECISIONS/` and `runtime/` out (read at request time). Latent bug found: `next.config.ts` traces `_ARTIFACTS/target-role-scan-hud.html` into `/jobs/scan`, yet `_ARTIFACTS/` is in SAFE_PATTERN, so a change to only that file never deploys | Yes |
| 6 | Scheduled Claude tasks fire in one burst on wake, and two are stuck | `~/.claude/scheduled-tasks` (16 recurring tasks enabled) | Not an API cost (they run on the subscription). On 10-30 at 14:56:11 UTC five tasks started in the same second. `arcs-drift-sentry` and `arcs-job-search-loop` each show a run still "running" since 10-30 with no activity after 14:56:55; both failed with exit 143 on 10-28. Five 8:00 weekday tasks overlap (drift sentry, LinkedIn cut, open loops note, daily reps, jobs at 8:15) | `list_scheduled_tasks`; `list_task_runs` for both tasks | Look at the two stuck sessions; stagger or merge the 8:00 cluster into one morning run. Confirm `le-woof-morning-desk` is still wanted (last ran 10-22) | Yes |
| 7 | Runner diagnostic logs never rotate | `~/actions-runner/arcs-v9{,-2,-3}/_diag` | 708 log files in arcs-mac since 10-20; 568 MB across the three runners, about 45 MB a day | `du -sh ~/actions-runner/*/_diag`; `ls _diag | wc -l` | Add `find _diag -mtime +14 -delete` to the existing weekly `arcs-worktree-cache-sweep` task | No (logs are gone), low value |
| 8 | OrbStack Kubernetes runs with nothing using it | OrbStack `k8s.enable: true` | coredns and local-path-provisioner pods restart with the VM (restart counts 19 and 9). No script or workflow in the repo calls `kubectl` or `helm`. Small CPU and memory cost, unmeasured in isolation | `orb config show`; `docker ps -a`; `grep -rlE "kubectl|helm" scripts .github` (no hits) | `orb config set k8s.enable false`, after Zach confirms nothing outside this repo (snapchain-local?) needs it | Yes |

## Checked and clean

- **Anthropic API spend from CI and schedules: no leak found.** `security.yml` runs only when a PR gets the
  `security-review` label (8 runs in the window, all label events). `smoke` and `fe-smoke` use the placeholder key
  `sk-ant-ci-placeholder`. No LaunchAgent or scheduled task calls the API: `canon_propagation_nightly.sh` runs
  `canon_propagation_check.py` (no API), `model_drift_check.py` skips without a key. The 10-05 drain path
  (memory `anthropic-api-budget-shared-cap-ci-drain`) is closed.
- **Scheduled GitHub workflows are cheap.** a11y nightly 11.4 min a day on arcs-mac at 07:41 UTC; advisory,
  no-squash, vercel-branch-pin under 1 min each; governance monthly; intent weekly. About 13 runner-min a day total.
- **setup-node cache:** PR 1941 covers every workflow on main (ci, blacksmith-verify, deploy-verify,
  preview-db-migrate, a11y). After it, smoke ran in 1.4 min and fe-smoke in 2.7 min.
- **`~/.npm`:** `_cacache` is already gone; `_npx` is 3.2 GB in 26 dirs, none older than 14 days (in use).
- **LaunchAgents:** `memory-timecapsule` every 30 min is a no-op when nothing changed (0 commits in 7 days);
  `gigi-stream` is not loaded (log ends 2026-09-03), so it costs nothing.

## Not measured (and why)

- **About 540 GB of the 891 GB Data volume is outside what `du` could read.** `~` totals about 320 GB and
  `/Applications` 25 GB; the rest is in folders that need Full Disk Access (Mail, Photos, Messages, Containers),
  system paths, and 9 Time Machine local snapshots taken since 2026-11-01 16:29. Those snapshots still hold
  the 8 GB of caches deleted today, so the free space will not show until macOS thins them. System Settings >
  General > Storage gives the real split.
- **Large but not recurring:** `~/Dropbox` 130 GB (could go online-only), `~/Library/Application Support/Claude`
  14.4 GB, `prisma-dev-nodejs` 5.8 GB, `~/.ollama` 4.4 GB, `~/OrbStack` 7.8 GB. Listed for Zach's call, not ranked.
- **Vercel dollars:** build minutes per plan are not exposed by the MCP; counts and durations only.

## Suggested order

1 and 2 together (one `runs-on` line for smoke), then 3 (stops a daily disk leak), then 5 (one regex), then 4
(after Zach's go on which worktrees). 6 to 8 when convenient.
