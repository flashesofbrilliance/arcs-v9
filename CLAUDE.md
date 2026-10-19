@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  the handoff-progress ledger (jsonl + md under `_STATE/`, gitignored) every turn-with-change, and asks for a `## Delta` at each compaction. Both are gitignored. `/handoff` folds them
  into the CLAUDE.md block and marks the ledger claimed; the global SessionStart hook flags any
  worktree whose trail was never claimed. Compaction never writes CLAUDE.md anymore.
- **Open work lives in `_QUEUE/induced-backlog.jsonl`** — items carry route/gates/trigger; execute
  from there without replanning. Dense multi-domain sessions: run `/fold` to spawn composed sessions.
- **On-demand only** (do NOT read to orient — open only when the task actually needs them):
  `MEMORY.md`, `SKILL.md`, `_ARCHIVE/handoffs.md`, `_ARCHIVE/memory-archive.md`, `_STATE/*`.
- There is no "read MEMORY→SKILL→WORLD→AGENTS in order" chain anymore. That mandate cost ~40k
  tokens per session and was retired 2026-07-19; open a specific file only when a task points to it.

# Project Map (read this before exploring)

## Stack
- Next.js 16 App Router · Prisma 7 + SQLite (`dev.db`) · Auth.js v5 magic link · Anthropic SDK

## Routes
| Path | File | Purpose |
|------|------|---------| 
| `/` | `src/app/page.tsx` | Home / entry |
| `/dashboard` | `src/app/dashboard/page.tsx` | **Main compass UI** — question input, prep form, result |
| `/compass` | `src/app/compass/page.tsx` | Magic-link login form |
| `/brief/[receiptId]` | `src/app/brief/[receiptId]/page.tsx` | Cartography brief (two-column) |

## API Routes
| Endpoint | File | Purpose |
|----------|------|---------| 
| `POST /api/compass` | `src/app/api/compass/route.ts` | L0–L5 Claude pipeline → Receipt |
| `POST /api/prep` | `src/app/api/prep/route.ts` | Create PrepSession |
| `GET /api/brief/[receiptId]` | `src/app/api/brief/[receiptId]/route.ts` | Generate/fetch Brief |

## Lib
- `src/lib/db.ts` — Prisma client singleton
- `src/lib/auth.ts` — Auth.js v5 config (Resend magic link)
- `src/lib/ygate.ts` — Y gate computation (GREEN/YELLOW/RED/FORK/SCRATCH/DELTA/PARADOX/DRIFT)
- `src/lib/env.ts` — env validation

## Schema (prisma/schema.prisma)
Core models: `User` · `PrepSession` · `Receipt` (DEWY + Y gate + kinematic + lineage) · `Brief` · `Outcome`
All JSON arrays stored as TEXT (SQLite). Enums as plain strings.

## Design tokens (inline style objects, no CSS framework)
```
bg: #020408 | surface: #0d1117 | border: #1e293b
text: #e2e8f0 | muted: #7a8699 | dimmed: #8391a7  (AA on bg; raised 2026-10-04)
cyan: #00F0FF | green: #00FF9D | gold: #FFD700 | red: #FF4D6D
```

## Y states → render resolution
GREEN=SHARP · YELLOW/FORK=DEGRADED · SCRATCH/DELTA/DRIFT=GRAIN · PARADOX=MOIRE · RED=GRAIN

# ARCS v9 Architecture (governing law)

## ROM Primitives — constitutional, never violate
1. **NOTOMATION** — scaffold/sequence cognition only; never compress/replace/overrule revealed preference
2. **HYPERSPHERE CONTEXT MANIFOLD** — What / Who / Where-When / Why / Flow-State
3. **HYPERSTITION PIPELINE** — Ethereal → Loki Test → Receipt Evaluation → ROM
4. **GOLDEN INCHWORM** — Red Thread → Golden Thread → Needle (3-pass, non-blocking)
5. **ORTHOGONAL ECHO DETECTOR** — surface cross-domain kinematic isomorphisms
6. **KINTSUGI IMMUNE SYSTEM** — repair seams visibly; no silent patching of integrity failures; show the break and the gold
7. **WRITE-LOCK** — one-way-door decisions require explicit write-lock declaration before commit; irreversibility is declared, not assumed

## L0–L7 Stack (current impl: L0–L5 only)
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade (canon name; the compass prompt runs L3 as the Kintsugi immune check, and no cascade code exists) · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

## ATG — next major feature (backlog)
Every compass response should include 2–4 tributaries: meta-question · need-to-hear branch · unnamed adjacent primitive

## What's NOT built yet
ATG · Kairos detection · Blockchain registry · L6–L7 engine · Python Vector Collision microservice
Observatory/replay: a **static demo** exists (`public/observatory/`, served via a `next.config.ts`
rewrite). The full interactive Next.js page IS committed on main at `src/app/observatory/page.tsx`
(landed 2026-06-23, ~1.2k LOC); the old "never pushed" note was stale (Atlas audit 2026-09-03).
Confirm the `/observatory` route vs the static-demo rewrite before relying on either.

# Token-saving rules
- **Invoke the `token-savings-bank` skill** (user-level, `~/.claude/skills/token-savings-bank`) before any
  fan-out (subagents, chips, parallel sessions), bulk edit, or long resumable task, and whenever you notice
  waste (top-tier model on mechanical work, a subagent for a one-grep question, re-deriving state). It governs
  Claude Code session tokens, which count against the subscription limit (the weekly cap stalled the morning
  jobs task 2026-09-30/10-01). API spend is separate: prompt caching, Batch API, and Haiku roles in
  `src/lib/claude-models.ts`.
- **Before planning any non-trivial task, run `/prior-art <job>`** (`scripts/prior_art.py`): it ranks memory, `_PATTERNS/`, ADRs and the tool catalog against the job so the plan starts from past lessons. Open only the top hits that apply; open the plan with a "Prior art:" line.
- Do NOT read files you already know from this map.
- Do NOT explore node_modules unless looking up a specific API.
- Before writing Next.js/Prisma code, check `node_modules/next/dist/docs/` for breaking changes.
- Inline styles only in components — no Tailwind, no utility classes. Sanctioned exceptions (only these): next/font classes on `<html>`, and the single `src/app/globals.css` (reset + keyframes + font tokens). Tailwind was removed 2026-07-11.
- No new dependencies without asking.
- **Self-contained artifact/page CSS: one shared px `--measure` for BODY/card reading text — NEVER `max-width:NNch` per element** (font-dependent → misaligned right edges that read as broken wrapping). **But LEDES are the exception: a hero/section lede spans the full lane width matching its heading (`max-width:none`), never the narrow body measure — a lede narrower than its heading reads as a broken/abridged block with a dead right gutter (EXCEPTION, 2026-09-29: text INDEX pages such as good.arcs.care/series/* put lede, rows and footer rule on the 680px measure) (`design-full-width-lede-matches-heading`; Zach's standing preference, do NOT "fix" it back to `--measure`).** The "too narrow" symptom is invisible to overflow/clip gates — eyeball lede-vs-heading edges at ~1280px too. Bordered callouts carry the measure on the box, not the inner text. Before shipping any single-file HTML, run the repo's own gate (`scripts/artifact_wrap_lint.py`; `npm test` for `zachharris-xyz`) and sweep 360–1440 incl. the 700–1000 band. Em-dashes 0. Canon: `_PATTERNS/arcs-artifact-css-base.css`; AGENTS.md gotcha #13.


# Versioning & handoff policy (amended 2026-07-19)

> Supersedes the prior "CLAUDE.md — append new sections only; never overwrite" rule, which had grown
> this file to 28 handoff sections / ~19.8k tokens loaded on **every** session. Rationale + measurements:
> `_PATTERNS/2026-07-19-token-efficiency-audit.md`.

- **CLAUDE.md is a working file, kept lean — not an archive.** It holds durable facts (Project Map,
  ROM primitives, token-saving rules) plus **only the latest handoff section** (older arcs live in `_ARCHIVE/handoffs.md` and git; `scripts/handoff_fold.py archive` trims between molts; the cap is 2, the default keep is 1, since 2026-10-17). Sessions no longer edit
  this file to hand off: `/handoff` writes a fragment (`_HANDOFFS/fragments/`, one file per session, raw
  material) and `scripts/handoff_fold.py molt` synthesizes ALL fragments into ONE arc block (Goal, What
  changed, State, Decisions, Open, ONE Next action, Cold-start recipe), versioned by
  `scripts/oracle.py next handoff`, refusing bookends; overflow moves to `_ARCHIVE/handoffs.md` by version
  (ADR-085 part (d) + 2026-10-06 amendment). Unmolted fragments are newer than any block below.
- **History is relocated, never deleted.** Older handoffs live in `_ARCHIVE/handoffs.md` and in git.
  "Never delete prior versions" is honored by archival, not by unbounded append into the hot path.
- `MEMORY.md` — keep recent entries live; relocate dead history to `_ARCHIVE/memory-archive.md`.
  New entries still go at top.
- Spec files — version field in front-matter; `*-v2` only on breaking schema change.
- Python scripts — never overwrite; create `*_v2.py` for breaking changes.


---

---

# Handoff — v3.140.0 (2026-10-19)

> Six fragments (2026-10-11 to 2026-10-18): billing-era one-way rulings, public-claim wording fixes, process architecture and session-start baseline, outcome capture on receipts, Scout/Wonderful leftovers, and the RET take-home close-out (rc46 submitted, confirmed by Zach 2026-10-18).

## Goal / true north
Keep every outward claim honest and every loop closed: decisions waiting on Zach are listed once, and the RET take-home arc is closed.

## What changed
- Ranked the OPEN induced-backlog rows into six groups (the row field is `state`, not `status`; an earlier claim that it was missing was wrong). Verified the six "probably done" rows and closed five in #1583 (b236861e), which supersedes #1288: outcome-loop-timing-wiring-horizon-reviewdate-blind, compass-mobile-timeout-recover-receipt, handoff-postmerge-ci-936, receipted-fears-stunt, accountable-copypasta-card. conviction-chips-calibration stays OPEN (its gate needs at least 5 real players before it extends past the prototype). #1288 conflicted with the backlog's growth, and a local merge commit on it was blocked by the pre-commit page checks on other sessions' files, so the change was re-made on a fresh branch off main; the gate was not bypassed.
- #1578 (d107dc2e): scripts/unfold.py fills Routes and Corrections from Librarian.recommend() pre-scores, surfaced and never acted on (row unfold-uses-librarian). The stones are still UNCUT (0 FLAWLESS before and after): their only lint reason is the integrity gate on item-text cites, not Routes or Corrections. Relevance of the pre-score lines is unjudged.
- PR 1470 (`2bd18f63`): regenerated `resume-norm-ai-fde-ats.pdf`; `public_claim_gate.py` now skips binary files (it crashed on PDF/PNG matching the resume globs). Receipt 2026-10-17--norm-pdf-regen-pr1470--ZH.
- PR 1481 (`ad3b599d`): 12 forge page.html footers say "Live commit and merge counts" (status.arcs.care shows aggregate telemetry, not a browsable log). Receipt 2026-10-17--status-wording-pr1481--ZH.
- PR 1491 (`2fcf67f2`): 44 files, covers (datadog x4, mongodb, thesis, blacksmith), bundles, forge evidence rows, served public/ pages; tear-sheet-amy gutter 44px to 40px for gutter-lint. Receipt 2026-10-17--covers-sweep-pr1491--ZH.
- PR 1500 (`39e63554`): blacksmith-observatory and growth-ai-observatory skills note now "demonstrated in a live app; code walkthrough on request". Receipt 2026-10-17--observatory-skills-note-pr1500--ZH.
- Gmail draft to amy@recruithaus.com ("Updated resume wording"), unsent.
- Proposals and tooling merged: #1307 (ADR-086, effort-policy, shape-card, port reconciliation; receipt 2026-10-15--adr-086-proposals-pr1307--ZH), #1308 (findings_gait ledger and pace clock; receipt 2026-10-15--findings-gait-pr1308--ZH), #1309 (16 LEGEND terms, FATED and KKL recorded as unruled; receipt 2026-10-15--legend-terms-pr1309--ZH), #1437 (finding-row schema and adapters; receipt 2026-10-17--finding-row-adapters-pr1437--ZH), #1467 (lap 2 quality metrics and shared ledger; receipt 2026-10-17--findings-lap2-pr1467--ZH).
- Detector and gate fixes: #1445 (seedbank local-path parsing; receipt 2026-10-17--seedbank-detector-fix-pr1445--ZH), #1478 (seed-ledger pre-commit gate; receipt 2026-10-17--seed-ledger-gate-pr1478--ZH), #1504 (repo coverage by name; receipt 2026-10-17--repo-coverage-by-name-pr1504--ZH).
- Seed bank curation, drift 47 to 0: #1449, #1485, #1494, #1497, #1508 (receipts 2026-10-17--orphan-seed-ledger-pr1449--ZH, --seed-status-mismatches-pr1485--ZH, --jobtracker-seed-ledger-pr1494--ZH, --last-orphans-pr1497--ZH, --scaffold-private-pr1508--ZH).
- Perplexity port reconciliation (archived prints under _ARCHIVE/antecedents-2026-10): #1515, #1519, #1520, #1521 (receipts 2026-10-17--antecedents-doc-classification-pr1515--ZH, --antecedents-port-verification-pr1519--ZH, --space-thread-locator-pr1520--ZH, --port-plan-vs-arcsv9-pr1521--ZH).
- Context diet: #1523 slice 1 (receipt 2026-10-17--ws1-slice1-path-scoped-rules-pr1523--ZH), #1526 slice 2 (receipt 2026-10-17--ws1-slice2-handoff-archive-pr1526--ZH), #1528 slice 3 (receipt 2026-10-17--ws1-slice3-world-split-pr1528--ZH). Always-on set 83,427 to about 47,500 bytes.
- Canon-write guard: #1532 (receipt 2026-10-17--canon-write-guard-pr1532--ZH), live-tested by Zach in a fresh session.
- Also done outside git: A.R.C.S. verified backup in ~/Backups/ARCS-antecedents-2026-10-17 (.env files excluded, unencrypted); main checkout reset to origin/main, then briefly moved to a test commit and restored.
- #1489 merged with --merge (`c19325b5`): scripts/receipt_outcome_queue.py (queue, record, status), append-only ledger _STATE/receipt-outcomes.jsonl, outcome atoms in the zach-receipts universe. Receipt 2026-10-17--universe-outcome-capture-pr1489--ZH.
- #1530 merged (`9a837d5d`): first 18 verdicts. Receipt 2026-10-18--outcome-verdicts-first-18-pr1530--ZH.
- #1540 merged (`796eccd7`): 6 more verdicts, 24 of 88 in scope. Receipt 2026-10-18--outcome-verdicts-24-of-88-pr1540--ZH.
- #1524 merged (`fa46c2ea`) and #1534 merged (`65c13523`): backlog rows status-page-public-claims-fix and trust-page-public-claims-fix. Receipts 2026-10-18--status-page-claims-row-pr1524--ZH and 2026-10-18--trust-page-claims-row-pr1534--ZH.
- #1543 merged (`801133a7`): canon universe regenerated from main after the 2026-10-17 canon strike (3 atoms changed text, 1 added). Receipt 2026-10-18--canon-universe-refresh-pr1543--ZH.
- 14 rows from the staged-rows folder appended to `_QUEUE/induced-backlog.jsonl` (none already present); `backlog_status_check.py --check` exits 0; staged folder deleted. All stay OPEN (resume-arcs-care-role-lens-page stays HELD). Checked against ADR-086, effort-policy.json and ADR-088: none of the five named rows is covered, so none was marked DONE or SUPERSEDED. `status_note` records the partial overlap for claims-atom-seed-gate (public_claim_gate.py, PR 1300) and taxonomy-conflict-ledger-and-atlas-edges (the Operator 21 label fix).
- `.claude/rules/operators-and-workers.md` (the AGENTS.md operators table was moved there 2026-10-17): OPERATOR21 row now says it shares only the number, Operator 21 is the Librarian per PERIODIC-TABLE.md row 21; LTE row now reads Lossless Translation Engine (checked against the docstring of `operators/arcs_lte.py`; the registry JSON has no LTE entry).
- Filed from the stoic-benz worktree (read only there, copied here): `_STATE/job-search/vico-call-2026-10-14-close.md`, `_STATE/job-search/vico-arcs-law-onepager-DRAFT.md`, and its 2026-10-15 witness line appended to main's `_STATE/witness/2026-10-15.jsonl` (different timestamp and quote, so not a duplicate). No Vico war-room or close note was on main. The close note says its universe edits (38 to 57 atoms) live in that worktree and were not copied; main's `vico.claims.jsonl` is unchanged.
- ret-rfp-intelligence main `1972551` produced rc46 (dist/submission-rc46.zip, 4,221,328 bytes); not an arcs-v9 PR.
- iCloud "RET take-home/" cleared to submission-rc46.zip plus the unzipped submission-rc46 folder (Zach's yes, 2026-10-18).
- ret-rfp-intelligence/dist cleared from 365 MB to submission-rc46.zip and its .sha256 (Zach's yes, 2026-10-18).
- This fragment's PR; receipt 2026-10-18--ret-submitted-handoff--ZH.

## Current state
- Submitted 2026-10-14: rc46 (Zach confirmed 2026-10-18).
- dist/videos and its MANIFEST.md are deleted, so the take-home repo's freshness script reports "nothing to compare" for videos. The explainer stays on YouTube: https://youtu.be/w7b-FVA3qSE.
- Internal RET notes (the 2026-10-1x RET notes) are untracked in the state folder of worktree mystifying-neumann-91d534, with archived copies in worktree ret-notes-2026-10 (archive folder ret-takehome-2026-10); not in the main checkout. They cite another repo, which the integrity gate blocks.

## Decisions made
- Zach: merge on local gates while Actions is off (receipts note CI is off by choice).
- Zach: merge each PR on local gates; save the Amy note as a draft, not send; sweep covers.
- Decided: status.arcs.care footer says "commit and merge counts", kept as a link (page shows commits per week, PR tempo, latest commit).
- Aspiration never raises an effort level by itself; it triggers a cohort check and a chutes-and-ladders board (`runtime/specs/effort-policy.json`, sections cohort_check and board; Zach, in chat 2026-10-15).
- A detector precision fix beats closing findings one by one, and a closure counts only if it survives re-detection (`scripts/findings_gait.py` status quality line; PR #1467).
- FATED, KKL and the two L-stacks stay UNRULED canon collisions; no policy picks one (`runtime/specs/legend.jsonl` rows FATED and KKL; PR #1309).
- Canon v1.1 asks and does not deny, because three corrective strike passes edited it on 2026-10-17 (`runtime/specs/canon-paths.json`; PR #1532).
- Prefer local compute to paid cloud when an equivalent exists, and never trade a correctness gate for cost (memory `trade-cloud-spend-for-local-compute`; Actions off since 2026-10-15).
- Merge a draft only after Zach confirms the live load: slices 1 and 3 and the canon guard waited for his check (PRs #1523, #1528, #1532).
- arcs-claude-project-scaffold is intentionally private (Zach, 2026-10-17; PR #1508, `_SEEDS/index.jsonl` row seed-repo-project-scaffold).
- Triage queue design, chosen by Zach after measurement: compass Receipt had 0 rows tagged real, and git-side adjudication is nearly always held.
- Checkable lines first; a verdict is external only with an evidence ref that resolves; self-graded is recorded but never scored.
- Zach did not accept the "no unique index on Lead" verdict, so it was not recorded. I did not add ADR-088 to the accepted-exposure list; that is Zach's call.
- Pushback kept on record. (1) The first eight verdicts were uniformly held and self-graded, which carries little information. (2) The independent check came from the same model family. (3) #1534 was merged when GitHub showed Vercel pending, on the strength of the Vercel API showing the deployment READY. (4) Canon atoms were grade A copies of text that proved unbacked; the refresh fixes the snapshot but not how the adapter trusts canon.
- Zach: keep only rc46 in iCloud and in dist; delete everything else, including history.bundle and the local videos.

## Open decisions (waiting on Zach)
1. Zach: send, edit or drop the Amy draft.
2. Zach: which Datadog, MongoDB, Thesis and Blacksmith covers were sent (sent copies keep old wording).
3. Zach: whether to rebuild the designed Norm PDF (no html source in the repo; it went to Dean Harris).
4. Zach: encrypt and copy the A.R.C.S. backup (commands in the README next to the archive); it is a plain local copy until then.
5. Zach: decide the funnel seed kill condition on 2026-10-22 (Vercel Web Analytics, at least 3 pageviews on /dashboard with utm_campaign=2026-10-05-ledger); finding f-d1cb1802f5.
6. Zach: delete or keep the eye-tracking stub in the private job-tracker-pro repo (seed anti-consentless-biometrics).
7. Zach: export three Perplexity Space transcripts that are not on this machine: the long "based-on-my-tendency-to-speak" thread, the Pilot's Manual positioning thread, the Ripple-BVF thread.
8. Zach: rule on the port candidates (my advisory lean, not a decision: compost the eight L0 skills and most missing agents, since the Python operators cover them; see `_ARCHIVE/antecedents-2026-10/2026-10-17-migration-plan-vs-arcs-v9.md`): the SuperAdmin Orchestrator spec (strongest real gap), the five advisor archetypes, the 18 PARTIAL and 5 UNVERIFIABLE docs, and the two stale REVIEW docs (Recursive Engine Spec v2, DEV_DECISIONS).
9. Zach: choose a verdict for the five GitHub Actions billing lines (still open, or dropped because Actions is off by decision).
10. Zach: accept ADR-088's VICO mention as exposure, or reword it.
11. Zach: replacement wording for the trust page and status page, and a monitored deletion contact for trust-contract line 88; any _CANON edit is proposed first.
12. Zach: verdict for the Lead unique-index line (evidence: model Lead has only two plain indexes).

## Open (other)
1. Backlog ripeness (2026-10-18): 8 RIPE rows. Zach decides: rc-ops-001-graduation-ruling (one-way), adr-085-acceptance-redecide (ADR-085 still PROPOSED; needs the train-vs-bypass counts), agent-receipts-audit-first-conversion (one-way external send). Read the 2026-10-17 accountant-weekly run output (13 s, reported succeeded, no new scoreboard since 2026-10-06) before closing accountant-weekly-first-unattended. forensic-arc-reconstruction: its claim (unnamed session since 2026-10-10) needs releasing; PR #951 merged. doc-gate-false-positive-cleanup is mechanical and ready.
2. 43 rows are past review_by (backlog_freshness.py), seven of them P1 and overdue about a week; fates are Zach's (renew, promote, compost, supersede). Three RUNNING claims are stale (> 3 days): forensic-arc-reconstruction, salvage-pass-promote-two, receipt-test-real-tag. Two rows are BLOCKED on dead dependencies (asm-009-net-direction-decided, tao-renders-regenerated-from-projection).
3. surfaces.arcs.care is not worth folding into the backlog yet (different job; one row mentions it). Revisit if rows get a stable key to a route.
4. scripts/unfold.py has a pre-existing integrity-gate failure (a vapor inbox path prefix in its docstring), present in main before #1578.
5. Fix the Actions spending limit so CI runs again (all five PRs merged on local gates).
6. Remaining "commit trail" phrases sit in atlas, red-team, CHRONICLE, nftt and defend-or-drop records, left as history.
7. cover-letter-blacksmith.md has one pre-existing em-dash that slop_lint flags.
8. Fix the AGENTS.md labels not yet corrected: OPERATOR21 is spline inference by file name only (periodic-table operator 21 is the Librarian), and arcs_lte.py is the Lossless Translation Engine, not trajectory modeling.
9. Run arcs_lte on one real technical-to-lay sample to test whether its IPS score means anything (not done).
10. Verify the Vercel production deploys reached Ready.
11. Air-gap review of _CANON/arcs-v9-additional/ARCS-DNA-Omakase-Deck.md (named profile scores), a folder the canon adapter does not read.
12. Existing rows still open: universe-atlas-tokens, universe-scenario-anonymizer, universe-breakoff-conductor-gate.
13. a. The Gmail draft to George (thread 1a135e43497f691a) is unsent and has no attachments. Owner: Zach.
   b. Debrief-vox answers for the Vico call are owed by Zach (row debrief-vox-capture).
   c. Funnel seed kill condition decision due 2026-10-22 (effort-policy session).
   d. Decide whether to send corrected resumes to direct contacts who got the old "public repo" resumes.
   e. Counterpart gauntlet has not been run on `_ARTIFACTS/scout-global-wonderful-bundle/external/`.
   f. The Vico onepager is Tier 2 (contains a formula): not to be sent before a mutual NDA or a deliberate downgrade.
14. After the interview: run /recoil-close on the RET engagement.

## Next action
Compare this session's session-start hook output with the 2026-10-17 baseline per the pending-check memory note, report pass or fail per line, then delete that note.

## Cold-start recipe
/handoff-pickup; then `python3 scripts/open_loops.py` (/loops) for the decisions waiting on Zach; RET: repo /Users/zharris/ret-rfp-intelligence, dist holds only submission-rc46.zip (the submitted build). Debt: https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm (debt collection).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261018T010206Z--claude-handoff-public-claim-fix-2.md
> ### Shavasana — handoff pause, 2026-10-17 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
> 
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-public-claim-fix-2), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: mirror (inhale, no exhale).
> - **Sycophancy check**: agreement 2 / dissent 1 (ratio 1.0) → OK: dissent present.
> - **Cold re-read (canary on the draft draft2.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
> 
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: every claim kept; each cites a PR, merge commit, receipt id or sent-folder check. Somatic: not asked. Disposition: release.

> Follow-on to the public-claim fix: regenerated the Norm ATS PDF, settled the status.arcs.care wording, swept covers and served pages, fixed the observatory skills note; four more PRs merged on local gates, deploy checked by served content.

### Notes: lead of 20261018T124627Z--claude-handoff-process-architecture.md
> ### Shavasana — handoff pause, 2026-10-18 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-process-architecture), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: mirror (inhale, no exhale).
> - **Sycophancy check**: agreement 8 / dissent 1 (ratio 4.0) → OK: dissent present.
> - **Cold re-read (canary on the draft handoff-fragment.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: re-read cold. Downgraded one claim: the bypass-mode result of the canon guard is reported by Zach (step 6 was optional and I did not ask which mode), not observed. Moved one advisory lean (compost the L0 skills) out of Decisions into Open. Kept the rest; each cites a PR, receipt id or file.
> - Scope note: the counts above are scoped to this branch, which has no commits yet, so the exhale reads 0; the session's real exhale is the 22 merged PRs under Changed. A first run scoped to the author identity read exhale 5 commits and 2 merges, and agreement 11 against dissent 1 (THIN); this run reads 8 against 1 (OK). Either way dissent in the day's records is thin. The pushback this session happened in chat prose, which those markers do not count: no 10X goal without a baseline, "novel" docs overstated, 65 percent of race closes were false positives, my own false receipt and shell-quoting slips. Disposition: release, with that limit stated.
> - Somatic: not asked. Sends today: none by me.

> Process-architecture session (2026-10-15 to 10-18): proposed the job-search effort policy and ADR-086, then ran the alternating findings race to drive the seed bank and its detectors to zero findings, reconciled the pre-v9 Perplexity material, cut the always-on context by 43 percent in three slices, and shipped a canon-write guard that Zach live-tested.

### Notes: lead of 20261018T150619Z--claude-universe-handoff-3.md
> ### Shavasana — handoff pause, 2026-10-18 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/universe-handoff-3), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: breathing (both directions).
> - **Sycophancy check**: agreement 7 / dissent 0 (ratio 7.0) → RETURN: agreement with no dissent on record.
> - **Cold re-read (canary on the draft frag4.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
> _This block asserts nothing new. Counts, paths, and questions only._
> - Attachment release: every claim re-read cold against the merged PRs, the ledger and the sweep output; none dropped. Disposition: release, with an explicit RETURN override. The sycophancy check returned RETURN (agreement 7, dissent 0) because its counter matches keywords and this draft's pushback is in other words (see the Pushback line under Decisions). I did not reword it to flip the counter. Somatic: not asked.

> Built the outcome triage queue for decision receipts, recorded the first 24 verdicts (16 of them backed by primary-source evidence), queued two public-claim fix rows, and refreshed the canon universe after another session struck unbacked canon claims.

### Notes: lead of 20261018T170000Z--claude-funny-burnell-3299b0.md
> Converged the Scout/Wonderful session (2026-10-14..18) onto main: 14 staged backlog rows appended, stale operator labels fixed, two Vico files and one witness stub filed. Nothing was emailed, messaged or published.

### Notes: lead of 20261019T005142Z--claude-ret-submitted-handoff.md
### Shavasana — handoff pause, 2026-10-18 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/ret-submitted-handoff), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 1 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 0 / dissent 1 (ratio 0.0) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Attachment release: every claim kept; the submitted-rc claim is marked unconfirmed. Somatic: not asked. Disposition: release.

> RET take-home close-out: Zach submitted the monday.com FDE take-home on 2026-10-14; this session then cleared old builds from iCloud and from ret-rfp-intelligence/dist, keeping only rc46.

### Notes: Lessons
- A count rule hid which repos differed; compare by name in both directions.
- A gate that fails on bad input must also be tested through its real entry point: two of my scripts passed their self-tests and then crashed live.
- Close the loop at the source: one detector fix cleared more findings than all the hand closures.
- Do not chain commands past a failed step: one chain logged a receipt for a PR that was never created; I deleted the row and chained strictly afterwards.

### Notes: ERRATUM (2026-10-18, appended; the text above is left as written)
Item (a) is closed and was wrong. Zach already sent the bundle email to George on 2026-10-16 14:25 UTC (new thread 1a1451af4dc0d68e, to george@scout-global.com, about 1.2 MB). The earlier note checked only the old thread 1a135e43497f691a, which holds George's Oct 13 reply. Verified from Gmail thread metadata (SENT label, sizeEstimate 1255580). A Mixmax reminder fired 2026-10-18 14:23 UTC; no reply from George seen. Open for Zach instead: wait for the reply, then close the loop and have the Accountant score the prediction. The merge receipt 2026-10-17--scout-wonderful-bundle-pr1442--ZH carries the same wrong "unsent" line; it was not edited, Zach decides how to correct it.

> Molted from `_HANDOFFS/fragments/20261011T130753Z--claude-mystifying-tesla-6bc6f3-billing.md` (branch `claude/handoff-billing-note`, head `updated 2026-10-18 (first written 2026-10-11)`); `_HANDOFFS/fragments/20261018T010206Z--claude-handoff-public-claim-fix-2.md` (branch `claude/handoff-public-claim-fix-2`, head `eb5013eb`); `_HANDOFFS/fragments/20261018T124627Z--claude-handoff-process-architecture.md` (branch `claude/handoff-process-architecture`, head `47a8ae73`); `_HANDOFFS/fragments/20261018T150619Z--claude-universe-handoff-3.md` (branch `claude/universe-handoff-3`, head `801133a7`); `_HANDOFFS/fragments/20261018T170000Z--claude-funny-burnell-3299b0.md` (branch `claude/funny-burnell-3299b0`, head `260ab9cd`); `_HANDOFFS/fragments/20261019T005142Z--claude-ret-submitted-handoff.md` (branch `claude/ret-submitted-handoff`, head `67d468d4`).
