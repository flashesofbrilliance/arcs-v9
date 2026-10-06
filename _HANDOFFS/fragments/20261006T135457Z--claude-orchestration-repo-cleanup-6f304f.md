<!--
branch: claude/orchestration-repo-cleanup-6f304f
head: 68024c46
created_at: 2026-10-06T13:54:57Z
-->
> **Orchestration session, day 2: open threads closed out, three API-key homes fixed, and a live tech-debt tracker.**
> SSOT for open debt is now the artifact **Docs Reconciliation** (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm),
> `debt` collection (19 rows seeded 2026-10-06; add/close rows with ArtifactData, no page edit needed).

## Shipped (overnight, across sessions)
#884 write-lock + leases (ADR-085 PROPOSED, opt-in) · #882 claude-models.ts single registry (#715 closed) ·
#880/#885/#890 Ahmed-order vocabulary + receipt + brief · #877 calm model errors + outage alert · #874 merge_train.sh ·
#888 receipt views no longer generate briefs · #831 fe-smoke page gate · #881 security-review fails on API error ·
#895 Missed pile sort/undo · #898 handoff fragments (this file) · #887 compass Y gate/mobile.

## Fixed this session
- Anthropic outage: the key lives in 3 homes (.env.local, Vercel arcs-v9, GH Actions secret). All held the capped
  account's key. New key from Zach's Individual Org now in all three (GH secret updated 2026-10-06T13:35:54Z via stdin,
  never printed). Proof: fresh security scan on #906 passed (scan ran, 0 findings).
- merge_train.sh validated: self-test 15/15 + a mutant fails; real dry runs (conflict path on #811/#854, clean path on #864, 31s with build).
- Memory: corrected anthropic-api-budget memory (prod WAS capped), added anthropic-key-three-homes-verify-without-exposing,
  migrated a stranded worktree-local memory. Index 1-1 OK.

## Open (all tracked as rows in the artifact's `debt` collection)
P1 decision: top up credits / auto-reload. Decisions: ADR-085 acceptance after migration step 2.
In progress (own sessions): alert-email proof, security-review skip-guard. Unassigned: npm test script, ESLint on
legacy public/*.jsx, main checkout parked on another branch, vercel experimentalServices, allowScripts.

## Lessons
- "Usage limit" can come from any of 3 key homes; check which org each key belongs to before raising limits.
- `vercel env ls` shows created age, not edit time; GitHub secret `updated_at` is reliable.
- A rerun is not a test when the action dedupes already-scanned commits: trigger a fresh scan.
