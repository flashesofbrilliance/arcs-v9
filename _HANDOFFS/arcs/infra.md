# Arc: infra (reconstructed 2026-10-06)

> From July to October 2026 the infra domain moved from loose, out-of-band hygiene (a disabled Drift Sentinel, a Vercel
> toolbar, scattered keys) to mechanical gates: worktree pruning with reversible bundles (cruft_sweep), a daily Vercel
> branch-pin gate, production `prisma migrate deploy`, a path-scoped security-review CI job, and a single model-id
> registry. The early October stretch was dominated by spend limits: the Anthropic workspace cap took production model
> routes down and GitHub Actions billing blocked every CI job, so many merges landed without CI on Zach's go. The
> remaining work is closing those loops (observe a green main run, add the Vercel token secret, settle the Vercel
> project and services cleanups).

## Goal
Every deploy, merge and environment change is reproducible, gated mechanically, cheap to run, and verifiable live
(git, GitHub, Vercel, Supabase), so no session has to trust memory about what is serving or what is configured.

## What changed
- v3.8.0 to v3.9.0 (2026-07-19): Drift Sentinel disabled by operator; rebuild spec written as report-only
  (`_PATTERNS/sentinel-rebuild-spec.md`). Out-of-band list in `_PATTERNS/2026-07-19-out-of-band-actions.md`.
- v3.57.0 (2026-09-07): Zach-gated carry list: Supabase Branching + `PREVIEW_DATABASE_URL` (PENDING 006), migration
  re-baseline (PENDING 007), integrity gate warn-then-block.
- v3.65.0 (2026-09-24): `/api/health` and compass timeout recovery (#489).
- v3.84.0 (2026-10-05): main red for every PR on `fe-smoke` (`import.meta` under Playwright CJS); fixed.
- v3.86.0 to v3.97.0 (2026-10-05): cruft_sweep hardened: wrong-HEAD bundles (#807), incremental bundles (#809),
  survey vs `origin/<base>` (#837, `9bef38d7`), manifest names only real refs (#861, `e8b9bd17`); first live prunes.
- v3.93.0 to v3.96.0 (2026-10-05): chase-intro, cj-brief, growth-intel were pinned to a dead preview branch; unpinned
  on Zach's go. Root `metadataBase` added so share cards stop leaking a client host (#848, `996b0418`). Daily gate
  `scripts/vercel_branch_pin_gate.py` + `.github/workflows/vercel-branch-pin.yml` (#863, `7f637e75`).
- v3.98.0 (2026-10-05): production deploys run `prisma migrate deploy` via `scripts/vercel-migrate-deploy.sh` and
  `DIRECT_URL` (#840, `942b0f46`); first run failed P3019 on a sqlite `migration_lock.toml`, fixed by #857
  (`f5fab907`). Prod `_prisma_migrations` matched all 22 migrations by sha256.
- v3.90.0, v3.104.0 to v3.105.0 (2026-10-05/06): spend limits. Anthropic workspace cap 503'd every production model
  route; key lives in 3 homes (.env.local, Vercel arcs-v9, GH Actions secret), all rotated. GitHub Actions billing
  blocked CI; Claude plan weekly limit separately killed scheduled runs. Security review scoped once per PR,
  path-scoped (#832, `feb4f300`, ~87% fewer runs on October data).
- v3.101.0 (2026-10-06): viewing a receipt no longer spends model tokens (#888, `0aad873d`).
- v3.110.0 to v3.111.0 (2026-10-06): CI repair: skip security review for dependabot (#868, `45162541`); eslint major
  pinned (#903); security-review gate stops failing re-runs red while real API errors still fail (#909, `6a29d549`).
- v3.113.0 to v3.114.0 (2026-10-06): handoff fold + integrity-gate citation fix (#921, #936). Receipt
  `2026-10-06--qualify-abb6aedb-pr936--ZH`.

## State
- All PRs above are MERGED on origin/main (checked with `gh pr view`, 2026-10-06; main head `89264922`).
- `prisma/migrations/migration_lock.toml` on origin/main says `postgresql` (verified).
- `vercel.json` uses `services` (verified): the `experimentalServices` deprecation item is done.
- `scripts/vercel_branch_pin_gate.py`, `scripts/vercel-migrate-deploy.sh`, `_PATTERNS/sentinel-rebuild-spec.md` exist.
- Integrity gate is still warn-by-default in `scripts/git-hooks/pre-commit` (`INTEGRITY_GATE_BLOCK` defaults to 0).
- No `VERCEL_TOKEN` repo secret visible, so the branch-pin workflow skips its live check (unverified: secret listing
  may need admin scope).
- GitHub Actions billing: CI ran again by v3.110.0 (re-runs succeeded); whether a clean post-merge main run has been
  observed is (unverified).
- Anthropic cap: keys rotated per v3.104.0; whether credits/auto-reload were set is (unverified).
- Drift Sentinel still disabled; rebuild not started (unverified beyond absence of a rebuild PR).

## Decisions
- Merge with `gh pr merge --merge` only; receipts cite PR boundaries.
- CI that runs an agent on every push is a production cost line: scope it to paths it protects.
- A billing block can hit one job in a running workflow: scan per job for 0 steps, not per run. A 0-step job means
  billing or outage; check annotations and githubstatus first.
- `gh run rerun` replays the old workflow file; to pick up a workflow fix on a dependabot PR, ask dependabot to rebase.
- `get_deployment(<host>)` does not reveal a branch pin; `list_project_domains` -> `gitBranch` does.
- Root metadata on a many-alias Vercel project must set `metadataBase`.
- Under Vercel services, a top-level `buildCommand` is ignored; each service owns its build.
- A wired-but-never-run step hides every latent bug behind it: run it once deliberately.
- `vercel env ls` names its project in the header and shows created age, not edit time; GitHub secret `updated_at` is
  reliable.
- The project-scoped Supabase connector (`xbbpiryokswwvcrcutge`) can write when the default MCP declines.
- Worktrees with symlinked `node_modules` break Turbopack dev: use `next dev --webpack`.
- Run repo scripts from your own worktree, never the main checkout path.
- Zach (v3.109.0): allowScripts approve all 4; doc gates advisory in CI; old Anthropic keys: audit callers, Zach retires.

## Open
1. Zach: add repo secret `VERCEL_TOKEN` (read on team arcs-care) so the daily branch-pin gate runs live.
2. Zach: Anthropic credits top-up / auto-reload decision; retire old keys after caller audit.
3. Observe one green post-merge CI run on main (every recent receipt lists it as unconfirmed).
4. Two Vercel projects named arcs-care (team + personal `prj_cVMj...`): delete or relink the personal one.
5. Zach: flip `INTEGRITY_GATE_BLOCK=1` after a clean week; `_ARCHIVE/handoffs.md` still fails on old citations.
6. Zach-gated: Supabase Branching + `PREVIEW_DATABASE_URL` (PENDING 006); PENDING 007 now largely served by
   migrate-deploy, confirm and close.
7. Drift Sentinel rebuild, report-only, per `_PATTERNS/sentinel-rebuild-spec.md`; SageTrace RLS.
8. Zach: disable Vercel platform toolbar on production (PENDING.md line ~70).
9. `security-review` label never rescans (cache key per PR): chip task_d4f6708c.
10. Orphan tools `scripts/_archive/idea_montecarlo.py`, `scripts/provision_studio_tenant.mjs`; confirm
    `state_sync_check.py` hook wiring.

## Next action
Pull the last 5 runs on main (`gh run list --branch main --limit 5`) and record whether a full green post-merge run
exists; if yes, strike Open 3 and start the clean-week clock for Open 5.

## Cold-start
- Files: `scripts/vercel_branch_pin_gate.py`, `.github/workflows/vercel-branch-pin.yml`, `scripts/vercel-migrate-deploy.sh`,
  `vercel.json`, `prisma/migrations/migration_lock.toml`, `scripts/git-hooks/pre-commit`, `_QUEUE/PENDING.md`,
  `_PATTERNS/sentinel-rebuild-spec.md`, `_PATTERNS/durable-gotchas.md`, cruft-sweep skill.
- Commands: `git log origin/main --oneline -20`, `gh run list --branch main`, `gh pr list --state open`,
  Vercel MCP `list_project_domains` and `get_deployment("arcs.care")`, `python3 scripts/vercel_branch_pin_gate.py`.
- Tracker: artifact AvE1T5TMQD164GPFGetHvm, `debt` collection (spend-limit and key rows).
- Memory: `anthropic-key-three-homes-verify-without-exposing`, `anthropic-api-budget-shared-cap-ci-drain`,
  `ci-zero-steps-means-billing-or-outage`, `ci-cancel-in-progress-main-only-newest-merge-verified`,
  `vercel-domain-gitbranch-pin-serves-dead-preview`, `prod-schema-drift-migrate-deploy-not-db-push`,
  `vercel-operations`, `arcs-v9-deploy-blast-radius-guardrails`, `safe-multiworktree-git-primitives`,
  `supabase-mcp-wrong-org-use-cli`.
