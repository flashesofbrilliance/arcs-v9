<!--
session: merge train, neighbor scan, adr-queue fix
branch: claude/handoff-train-receipts
head: a196e719
created_at: 2026-10-11T00:48:35Z
-->
## Changed
- Merge train (`merge_train.sh --lock --yes`) landed #1099 neighbor_scan (0ac7f6ec), #1096 backlog close (cec12ea0), #557 better-sqlite3 13.0.3 (aba03930), #1086 train Docker smoke (28b62934). First push was rejected non-ff (main moved), the re-run pushed.
- #1146 (28e385cf) ADR-085 addendum for the Docker smoke step. #1147 (2bf7eb5a) fixed `.github/workflows/adr-queue.yml`: a pipe-delimited sed died on the pipe-separated row and also replaced every `---` line; now awk takes the row from the environment. #1149 (54d32c55) ADR-085 Failure modes ground paragraph, which doubled as the live test: ADR → Queue went green and bot commit 1f013f7d added the ADR-085 row to `_QUEUE/PENDING.md`.
- New convention: AGENTS.md gotcha 19 and `scripts/neighbor_scan.py` (read-only; lists citers, offspring, open PRs on the same file). Ran it on the train; only real follow-up was ADR-085, now done.

## State
- Main CI green on b1b5a17f; production deploy dpl_BPRvDwUJVvXQbi5vYPRWtPGjWeoM READY on app.arcs.care and arcs.care (build from b1b5a17f, descendant of every merge above; deployment record checked, no live page requested).

## Corrections to the receipts (the UPDATE was declined, so they live here)
Receipts `2026-10-10--pr1099-merge-train--ZH`, `--pr1096-`, `--pr557-`, `--pr1086-` still list "Vercel deploy READY" and "CI run on 28b62934" as unconfirmed. Both are now confirmed: CI on 28b62934 completed success (21:33Z) and the production deploy above is READY. Same for `2026-10-10--pr1146-adr085-smoke-addendum--ZH` and `--pr1147-adr-queue-awk-fix--ZH`: deploy READY confirmed, and the "ADR to Queue run on 28e385cf stays red" line is superseded by the green run on 54d32c55. `--pr1149-adr085-failure-modes--ZH` already records the green ADR to Queue run and the PENDING.md row; its deploy line is also confirmed now. Still unconfirmed everywhere: better-sqlite3 13 behavior at runtime beyond the test suite (dev SQLite only), and the Docker smoke step has no real-train result recorded.

## Decisions
- Zach: merge each PR on green CI; do not touch #1107 or #1101 yet.

## Open
1. #1107 (My Ally Tally intake link): fe-smoke failure unread; content release needs Zach's go-ahead.
2. #1101 (retired greys swap): DIRTY, needs a rebase.
3. ADR-085 Failure modes: CAS retry count (8) and exit code 4 for a stale lock are still unverified; canary reads THIN AIR, not clean.
4. neighbor_scan lists 140+ citers for widely cited files (AGENTS.md, package.json); a cap or a widely-cited flag is a fair follow-up.
5. The default Supabase connector declines UPDATEs on decision_receipt; the project-scoped connector (project_id xbbpiryokswwvcrcutge) has worked before and was not used without Zach's say.

## Next action
Zach: decide #1107 (read its fe-smoke failure, then release or hold the My Ally link) and whether #1101 gets a rebase.
