# Converged thread: 72-hour sweep, 2026-09-25 to 2026-09-28 (cold molt)

## Ground truth (verified 2026-09-28 12:45 EDT, `git log origin/main --since=72.hours --merges` + `gh pr list`)
- About 45 PRs merged to main in the window, incl. the operator registry, MCP (Model Context Protocol, the tool bridge) bridge, LEGEND, LORE, fates, source trust, altitude canary, witness scout, Shavasana, unfold + cold molt lint, Op 19 Accountant (#578), echo embedding (#612), audit falsification count (#591), Tao backfill batches 1 to 5 (#616 to #621), and the fan-out board (#585, now merged).
- External funnel: 10 receipts, 0 outcomes (`_STATE/2026-09-27-accountant-scoreboard.json`).

## SSOT
- Open work: `_QUEUE/induced-backlog.jsonl`; board: `python3 scripts/backlog_issue_sync.py board`.
- Operators: `operators/OPERATOR-REGISTRY.json` (numbering per `operators/docs/PERIODIC-TABLE.md`).

## Routes (open PRs, each needs Zach's explicit go before merge)
1. Mergeable now: #577 (Yuri trust event), #627 (audit page restamp to 41), #624 (funnel re-run), #625 (internal owner hub), #552 (favicon), #549/#538/#537 (leak-check fixes, likely clear the inherited red), #532 (projection factory).
2. Conflicting, needs rebase by owner: #623 (Tao final batch), #598 (om_gap), #558 (base debt), #535, #531.
3. Dependabot #551 to #557: dependency bumps, need a yes per AGENTS.md gotcha 1 (no new deps without asking; majors for eslint 10, dotenv 18, better-sqlite3 13).
4. Stale (before 2026-09-16): #446, #434, #392, #359, #338, #327, #270, #255, #193, #162, #135. Triage: close or refresh.
5. After #577/#627 land: close issue #579; append status to backlog rows `kintsugi-public-falsification-count` and `echo-detector-embedding-signature`.
6. Zach rulings pending: RC-OPS-001 criteria (`_STATE/2026-09-27-rc-ops-001-criteria-audit.md`); somatic read.

## Gates
- Merge guard: only the two inherited red jobs (leak-check, smoke ledger delinquency) may be red.
- Every merge ends with one `decision_receipt` row (AGENTS.md "Receipts or it didn't happen").
- Generated views: `--check` on pre-commit plus CI `generated-views` job.

## Corrections
- Perplexity "audit" 2026-09-27 fabricated an operator map; periodic table wins (AGENTS.md gotcha 16).
- Yuri was handled 2026-09-25; the misread is logged in #577.

## Close protocol
- Merge on go, then receipt, then status append on the backlog row, then close the issue. Never send email; draft only.
