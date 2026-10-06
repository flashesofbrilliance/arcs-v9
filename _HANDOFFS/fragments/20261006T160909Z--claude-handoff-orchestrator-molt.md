<!--
session: claude-handoff-orchestrator-molt
branch: claude/handoff-orchestrator-molt
head: 7073958e
created_at: 2026-10-06T16:09:09Z
-->
> **Orchestrator molt (2026-10-06 noon): landing control + cleanup handed to a fresh session.** This session ran 24h+; the usage panel showed long, high-context, parallel sessions burn the limit, so it molts here.

## Goal / true north
One lean orchestrator sequences every landing on main, keeps live sessions at 4 or fewer, and keeps the bills (Anthropic, GitHub Actions, Supabase) predictable.

## What changed
- Landed with receipts today: #942, #876, #956, #920, #644, #961 (this session); #951, #959, #962, #963, #965, #941, #950, #947 and others (their sessions, cleared here).
- Disk 4.5 GB -> 18 GB: 30 worktrees pruned with incremental bundles + salvage preflight; showcase-mirror branch retired (bundle + refs/cruft-archive/showcase-mirror-1c120fff).
- Anthropic key moved to Zach's Individual Org in all 3 homes (.env.local, Vercel arcs-v9, GH Actions secret); CI security review moved off Opus 4.1 (#965, the main API leak).
- Tracker (debt SSOT until Issues migration): https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm `debt` collection.

## Current state
- Live sessions (3 + orchestrator): Issues as debt SSOT + status page (Sonnet), Receipt efficacy loop option C (Sonnet), API spend wrap-up of #1026 (Haiku). Each told to write a fragment and stop if its context is large.
- Open PRs needing attention: #934 (advisory gates, red), #932 (#811 carry-over, red), #964 (forensic arc reconstruction), #976 (orphan audit, cleared), #1027 (PM application materials, not orchestrated here), dependabot majors #676/#557, drafts #700/#730.
- Stale-but-paused: none; stale scheduled runs archived (tasks rerun on schedule).

## Decisions made
- Landing control: sessions ask the orchestrator for "cleared" before merging; merge with --merge on all-green only; one receipt per merge.
- Budget rules (memory session-budget-discipline-cap-parallel-molt-long): max 4 live sessions; molt past ~150k context or ~8h; no fan-out for small jobs; cheap models for mechanical work.
- Zach picks (10-06): fewer-permission-prompts, local security-review before PRs, keep repo nci-scoring and retire the anthropic-skills duplicate.

## Open decisions (waiting on Zach)
1. Old Anthropic keys: move/delete the remaining copies, then revoke in the old org console (CLI chore list in the 10-06 orchestration chat; list in #958).
2. ADR-085 acceptance re-decision ~2026-10-13 (train as the only merge path).
3. Close the 7 SECRETLY-DONE backlog rows with `scripts/backlog_ripeness.py --apply-closes`.

## Open (other)
1. P1: GitHub Actions minutes leak (~200 CI runs/day x 6 jobs, per-job minute rounding). Fix: collapse CI jobs, path-filter heavy jobs, fold `intent` into CI, skip drafts, merge-train batching, daily spend line in the morning note.
2. Cheap adds: CLAUDE.md rule "run local security-review before opening a PR"; note the nci-scoring duplicate decision.
3. Run `fewer-permission-prompts` as its own session (heavy read).
4. FieldOS explorer: gated on Issues SSOT + server-side /api/pulse; then one `field-state.json` contract (internal + public-safe tiers), then the explorer reusing arcs.care dataviz / terrain-atlas / Observatory.
5. Supabase billing page check (plan, compute, add-ons); no preview branches exist.

## Next action
Start a fresh orchestrator session, run `/handoff-pickup`, and do the cheap adds, then create the P1 GitHub Actions cost chip.

## Cold-start recipe
- Read this block only, then `gh pr list --state open` and `list_sessions` (keep live sessions at 4 or fewer).
- Tracker Active/Needs-a-decision views for debt; `_QUEUE/induced-backlog.jsonl` + `python3 scripts/backlog_ripeness.py` for ripe work.
- Merge path: `scripts/merge_train.sh --dry-run <PRs>` for batches; receipts to `public.decision_receipt` (Supabase xbbpiryokswwvcrcutge).
