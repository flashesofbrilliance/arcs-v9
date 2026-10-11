# Epic migration plan: induced-backlog + orphaned issues -> GitHub Milestones

Status: **grouping CONFIRMED by Zach 2026-09-27**. Open decisions below still need his answer.
Written from a session whose Bash was blocked; execute from a fresh session.

## Why

Work was split across five trackers with zero cross-linking (`_QUEUE/induced-backlog.jsonl`,
`_PATTERNS/ledger.json`, per-worktree handoff files, CLAUDE.md handoffs, Supabase
`decision_receipt`). GitHub had 30 open issues (26 orphaned from a single 2026-07-19 batch),
32 open PRs with zero `closes #` links, 0 milestones, 0 Projects. A roadmap, epics, and any
GitHub-analytics sync to status.arcs.care or the observatory all read from Issues, so this
migration is the substrate for everything after it.

## Epics = Milestones (mutually exclusive: an issue holds one milestone)

Backlog ids are `_QUEUE/induced-backlog.jsonl` `id` values. `#N` are existing GitHub issues.

| # | Milestone | Backlog items (create issue) | Existing issues (assign milestone) |
|---|---|---|---|
| 1 | Product keel: receipts & reliability | outcome-capture-rate-keel-gap (P1), prod-db-onto-prisma-migrate-deploy (P1), compass-mobile-timeout-recover-receipt (P2), svc-sage-should-it-exist-decision (P3), op20-somatic-axiom-real-signal-source | #85 (verify built, then close), #86, #97 |
| 2 | Distribution & growth surfaces | mcp-connector-wrapper-adr-076 (P1), greenhouse-arcs-care-seedbank-surface (P2), hypothesis-generator-plg-surface (P3) | #78 |
| 3 | Job search: active pursuits | autopilot-arcs-care-battle-card-ammo (P1), vico-arcs-care-battle-card-ammo (P1), resume-kinexys-regulated-digital-assets-cut (HELD, trigger-gated) | none |
| 4 | Jobs board tooling | swipe-left-rationale-loop, req-reality-dim-board-and-champion, jobs-arcs-care-recruiter-workflow-fork, flavor-filters-and-sleeper-filter, covers-for-apply-set, morgan-stanley-seed-unparseable, ingest-watermark-autobump-bug, leverage-lens-shape-moat, champion-sourcing-more-amys | none |
| 5 | Platform: model-agnostic + embeddings | compass-model-agnostic-provider-abstraction, embedding-storage-target-pgvector-vs-duckdb, gauntlet-wargame-embedding-dedup (all share /api/embed; sequence as one) | none |
| 6 | Security & trust | none | #72, #75, #76 (needs GitHub Pro), #77, #79, #83, #90, #93, #96, #99, #171 |
| 7 | Design system & artifact gates | scan-huds-migrate-to-tokens-css, tokens-css-vs-ds-font-stack-drift, nftt-template-kintsugi-contrast-and-label-heuristics (real AA failure), state-of-union-dashboard-ahmed-impeccable-pass, nftt-story-factory-index-instructions-stale | none |
| 8 | ARCS-native harness & research | session-drift-detection-eval, operator21-gaussian-process-posterior-then-rt-core, moral-to-gate-alchemy-pipeline, pond-etch-protocol-serialize-molt-test, algorethics-in-scope-benchmark | #80, #81, #82, #87 (product Drift Sentinel; do not merge with session-drift eval), #91, #92 |
| 9 | PRL client (Zapier/Sugar) | prl-empty-email-e2e, prl-task3-sla-zap, prl-task4-rep-notify, prl-task9-unassigned-digest, prl-task7-parser-install, prl-task10-zoominfo-email | none |
| 10 | Housekeeping & CI | orphan-seeds-curation, tao-backfill-066-067, gh-actions-billing (likely stale: CI runs), plus NEW items below | #73, #74, #84, #88, #94, #539, #540, #541, #542 |

Counts: 42 live backlog items + 26 orphaned issues + 4 blocking-root issues.

**New issues for milestone 10** (from the 2026-09-26/27 session; not in the JSONL):
- **Retired model still being called (P1, actively failing).** Anthropic email: 12 failed requests on 2026-09-26 to `claude-3-5-haiku-20241022` (retired 2026-02-19) from API key `CLAUDE_KEY (sk-a****)`. Not in arcs-v9, perplexity-mcp or arcs-care-local. Hits are in `~/.hermes/` (hermes-agent + `profiles/arcs`), `~/.claude.json`, cursor-agent's model catalog. `anthropic_adapter.py` only lists it in a legacy-classification table, so the live caller is more likely an auxiliary/cheap-model setting in a Hermes profile or config. Find with: `grep -rln "claude-3-5-haiku" ~/.hermes ~/.claude.json | grep -v -e cache -e tests`. Replacement per Anthropic: `claude-haiku-4-5` (check changed request params; run `/claude-api migrate`).
- **Deprecation watcher (P3).** Zach asked 2026-09-27 for a listener on Anthropic/platform deprecation docs to get ahead of retirements.
- **9 dev-scope Dependabot alerts (P3):** brace-expansion, deepmerge-ts, mysql2; no Dependabot PRs opened (likely transitive).
- **rclone Google Drive third backup copy (P3):** rclone 1.75.1 installed; `rclone config` OAuth is Zach's step.
- **GitHub Pro decision (P2):** $4/mo, the only route to branch protection / required checks (#76). Sequence after main CI is green.
- **Operator 1-19 specs (P3):** Zach is gathering operational definitions/specs for operators 1-19 from his Perplexity ARCS Space. perplexity-mcp cannot read Spaces (it only exposes search/reason/chat over public models), so export them into `operators/docs/` so they are versioned and readable.

**Do not migrate (DONE / CLOSED / BUILT; archive):** sean-wing-close-loop, prospecting-pass-1,
ziggurat-trailhead-key0, prl-task1-guard, prl-task2-cleanup, prl-task5-baseline,
prl-task6-routing-sweep, tool-catalog-dispatcher-induction-surface,
fold-2026-08-28-forensic-recall-session, worktree-sprawl-prune.

## Open decisions (ASK ZACH before executing; recommended defaults shown)

1. **PRL (milestone 9):** all six items blocked on a human trigger since 2026-08-26. Is the engagement live? *Default: create the milestone but label items `parked`; do not spend effort.*
2. **Stale statuses:** leverage-lens-shape-moat and champion-sourcing-more-amys say "DELEGATED, running" since 2026-09-08; gh-actions-billing claims CI is disabled but CI ran 2026-09-26; #85 outcome handler is BUILT per AGENTS.md. *Default: verify each, close with a note instead of migrating.*
3. **"Now" lane:** outcome capture, prisma migrate-deploy, MCP connector, Autopilot, Vico, plus the retired-model fix. *Default: these six carry label `P1` and the earliest milestone due dates.*
4. **Cross-cutting items:** one primary milestone, plus a label for the secondary epic.
5. **Fate of the JSONL:** *Default: add a `github_issue` field to each migrated row as a back-pointer; from then on Issues are the SSOT and new work goes to Issues, not the JSONL.* (Tidy house: one tracker, not six.)

## Why not op19/20/21 for the grouping

Asked and checked 2026-09-27. Operator 19 has no file. op20 is the right shape (DBSCAN) but the
wrong domain: its 54 dimensions are receipt-specific (signal, LAB, court, somatic, FATED, axioms,
trace), so feeding it backlog items would mean fabricating somatic/axiom values, which
`prod_receipt_to_op20_seed.py` and memory `op20-somatic-axiom-is-upstream-signal-gap` forbid; it
is also gated at 100 receipts. op21 is spline inference, not grouping. 52 items were grouped by
reading them.

## Procedure (fresh session)

1. `git status` / confirm branch. Check existing labels (`gh label list`); create `P1` `P2` `P3` `parked` only if absent.
2. Create milestones: `gh api repos/flashesofbrilliance/arcs-v9/milestones -f title="..." -f description="..."`. Record each returned `number`.
3. For each live backlog item: search first (`gh issue list --search "<id> in:body"`) so re-runs are idempotent, then `gh issue create --title "<short title>" --body "<jtbd + gates + trigger>\n\nMigrated from _QUEUE/induced-backlog.jsonl id=<id>" --milestone "<title>" --label <P>`.
4. Assign milestones to the existing issues listed above (`gh issue edit N --milestone "..."`).
5. Close verified-stale items with a comment stating the evidence.
6. Write `github_issue` back-pointers into the JSONL (decision 5).
7. **Verify, do not trust exit codes:** re-list milestones and open issues, confirm counts match this plan. (Write-path lesson from 2026-09-26: a GET 200 is not proof the write worked.)
8. Log one `decision_receipt` row for the migration (AGENTS.md "Receipts or it didn't happen").

## After the migration (later phases)

- **Roadmap:** Projects v2 board with a date field (native roadmap view). Optionally one parent issue per epic with sub-issues (issue-to-issue relations DO work; only PRs are excluded).
- **Sync:** status.arcs.care and the observatory page read milestone progress from the GitHub API instead of hand-kept JSON. Verify domain topology live first (status.arcs.care is an alias of the arcs-v9 production deployment as of 2026-09-26) and confirm which observatory is canonical (`src/app/observatory/page.tsx` vs the `public/observatory/` static demo, per CLAUDE.md).
- **PR linking going forward:** PR template gains a `Closes #` field; `scripts/dependency_sweep.py --emit` keeps blocking-root issues current.
