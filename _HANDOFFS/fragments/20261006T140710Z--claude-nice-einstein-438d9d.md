<!--
branch: claude/nice-einstein-438d9d
head: 7d495b35
created_at: 2026-10-06T14:07:10Z
-->
> **Debt tracker triage (Docs Reconciliation artifact, `debt` collection).** No code shipped; decisions + 7 chips.

## Decided by Zach (2026-10-06)
- ADR-085 stays PROPOSED, write-lock stays opt-in until the step-2 week ends (~10-13). Day-1 data: 8 locked trains vs 33 merges to main. Re-decide acceptance + step 3 (train as only merge path) together.
- allowScripts: approve all 4. Doc cleanup: measure + salvage only, no moves. Doc gates: advisory in CI now. Old Anthropic keys: audit callers, Zach retires. Main checkout: WIP-commit, push, return to main.

## Tracker
- Closed: handoff-fragments-pr898 (#898 merged).
- In progress (chips): repo hygiene PR (eslint ignore, npm test, vercel services, allowScripts) · handoff_fold sort by version · doc gates advisory CI · doc per-file breakdown + salvage (3 rows) · old-key caller audit · main checkout return · PRs #811/#854.
- Still open, waiting on data/Zach: cache-sweep-stuck (Zach), prisma-8-rc (watch), sharp-render-untested (needs first SHARP receipt).

## Lessons
- Lock adoption is measurable from `refs/locks/main` history vs first-parent merges on main; use that as the step-2 metric.
