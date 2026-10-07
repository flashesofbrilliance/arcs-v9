@AGENTS.md
@WORLD.md

# Session orientation — read this much, and no more

This file (+ its `@`-imports AGENTS.md and WORLD.md) already loads automatically. That is your
baseline context. **Do not read further to "orient."**

- **To resume work:** read the latest `# Handoff` block below (bottom of this file) — nothing else.
  Or run `/handoff-pickup`, which reads `_STATE/snapshot.json` + the latest handoff only.
- **Progressive handoff (2026-09-04):** a global hook checkpoints git state to
  `_STATE/handoff-progress.jsonl` every turn-with-change, and asks for a `## Delta` in
  `_STATE/handoff-progress.md` at each compaction. Both are gitignored. `/handoff` folds them
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
L0=atomic signal · L1=coherence · L2=path survivability · L3=cascade · L4=cross-domain · L5=global coherence · L6=ecosystem · L7=meta-governance

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
  ROM primitives, token-saving rules) plus **only the latest 1–2 handoff sections**. Sessions no longer edit
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

# Handoff — v3.116.0 (2026-10-07)

> # Handoff — carry-over from closed #811 (2026-10-06)
>
> > **No new work: two Open items from #811 (itself carried from closed #777), moved to a fragment because handoffs no longer edit CLAUDE.md (#898).**
>
> > **Orchestrator molt (2026-10-06 noon): landing control + cleanup handed to a fresh session.** This session ran 24h+; the usage panel showed long, high-context, parallel sessions burn the limit, so it molts here.
>
> > **Docs Reconciliation round (2026-10-06 afternoon): tracker decisions worked through, 15 PRs landed, Actions cost cut, integrity gate baselined and blocking.** Tracker (debt view): https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm; Issues (#1025) is now the source of truth.
>
> > **Docs Reconciliation, evening round (2026-10-06): defaults approved, Librarian calibrated, lattice re-authored, ADR → Queue fixed. 5 tracker rows remain "needs a decision", all yours.** Continues fragment `20261006T183213Z--claude-docs-reconciliation-orchestration`. Tracker: https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm; Issues are the source of truth.

## Goal / true north
Finish the judgment calls on the tracker with defaults and one-pass rulings, inside Zach's time budget.

## What changed
- Landed with receipts today: #942, #876, #956, #920, #644, #961 (this session); #951, #959, #962, #963, #965, #941, #950, #947 and others (their sessions, cleared here).
- Disk 4.5 GB -> 18 GB: 30 worktrees pruned with incremental bundles + salvage preflight; showcase-mirror branch retired (bundle + refs/cruft-archive/showcase-mirror-1c120fff).
- Anthropic key moved to Zach's Individual Org in all 3 homes (.env.local, Vercel arcs-v9, GH Actions secret); CI security review moved off Opus 4.1 (#965, the main API leak).
- Tracker (debt SSOT until Issues migration): https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm `debt` collection.
- #1029 merged (1fceb396): Receipt.provenance + Outcome.synthetic (migration 20261006120000, applied in prod), compass accepts provenance/resolveBy, outcome route allows synthetic only on test receipts, Accountant test/real cohorts, scripts/receipt_efficacy_probe.py (dry-run).
- Receipts 2026-10-06--receipt-provenance-pr1029--ZH and 2026-10-06--provenance-backfill-189--ZH.
- Merged #1033 (98829d06), #1035 (63b0c591), #1037 (81a6d5a4), all docs under _ARTIFACTS/: crypto-defi-predictions-closing-the-loop-2026-10-06.md (scorecard), usdc-jan-2026-belief-log-2026-10-06.md (H1 to H36), closing-the-loop-crypto-defi-draft-2026-10-06.md plus .evidence.jsonl (provenance_lint 46 metrics, slop_lint pass).
- Supabase decision_receipt: 5 resolution receipts logged and later updated (2026-10-06--rwa-filtering-event-close, section-404-falsifier-close, collateral-wars-gold-falsifier-close, custody-collateral-cascade-close, deposit-token-unified-ledger-check) plus merge receipts for PR 1033, 1035 and 1037 (--ZH).
- Branches deleted locally and remotely after merge.
- **Merge train 1** (#1030 status live read, #976 orphan audit, #959 alert_test, #964 forensic arcs, #676 checkout@7) and **train 2** (#1039, #1040, #1025), receipts `2026-10-06--pr<N>-merge-train--ZH`. Direct merges: #1031 (sage_efficacy.mjs cites), #1032 (Actions cost fix), #934 (advisory gates, path-filtered, through the train), #1034 (release_notes.py), #1036 (integrity baseline + 4 scripts archived), #932, #1027 (PM bundle, Zach's yes). #1037 merged by its own session.
- **Actions cost (P1, issue #1046):** leak-check + belief-log + generated-views folded into one `gates` job; draft PRs skip CI; `intent` only on AGENTS.md changes. Cause of the "red" PRs was the 14:18Z billing block, not code.
- **Integrity gate:** 648 failing cites across 131 of 398 live records grandfathered in `scripts/integrity_baseline.json`; `_ARCHIVE/` exempt; pre-commit now **blocks by default** (INTEGRITY_GATE_BLOCK=0 opts out once). Whole tree exits 0, a new vapor cite exits 1.
- **Release notes:** `scripts/release_notes.py` writes `_RELEASES/<date>.md` from git (area by files touched). 09-15 to 10-06: 366 merged PRs; compass 16, operators 7. Compass is NOT wired to operators beyond an advisory SAGE pre-screen (fired 65 of 91 receipts; it feeds synthetic signal from stakes/horizon, not the question).
- **Sweeps (run directly, no chips):** icon/manifest 74 hosts x 6 paths all 200; 72 static subdomain pages have no og:image; ATS PDFs 93 of 96 clean by poppler (not a real ATS).
- **Tracker/Issues sync:** relabelled 20 and closed 14 GitHub issues to match today's edits (debt push only creates missing issues; it does not update existing ones).
- **Sessions archived (harvested, clean):** forensic arcs, job tracker, key audit, orphan audit, dup docs, induct backlog, Issues SSOT, receipt efficacy, DeFi review.
- **Defaults approved (10-06):** closed adr-citation-linter (stays manual), frontend-design (won't fix), conflicting-prs-811-854 and salvage-recoil-close-pr644 (#811 closed, #854 and #644 merged); parked nftt-index, culture-rescore, reading-room-lexicon; fixed the status-page row. 3 flagged ATS PDFs (aircall, comet, morgan-stanley) moved to Trash; 93 remain. GitHub issues relabelled and closed to match (debt push does not update existing issues).
- **#1050** ADR → Queue fix: multi-line output now uses the heredoc form, so a push touching 2+ ADRs no longer fails the job; template-only change is a no-op. First real multi-ADR push will prove the generate and commit steps.
- **Librarian (Op 21), #1052 + #1060:** picks carry band `likely` (p >= 0.6) or `maybe` (cut in `read-friction-tiers.json`); name-match bonus 0.2 (key-rotation memory now pick 3); take loop skips an unpayable item instead of stopping. All three knobs rest on 11 labelled picks (tentative). Still absent: `project_todd_hotes_prl_resins` on the strict-gate query (labelled useful). SAGE query returns 11 maybes.
- **Claim unit v1, #1054:** PROPOSED amendment in `runtime/specs/operator-25-shavasana-v0.md` (bullet or sentence instead of section). Same handoff scores 0.89 (section) vs 0.47 (claim). The confidence function exists only on closed PR #598's branch (`claude/zen-pasteur-85c635`).
- **Lattice, #1062:** eng, kai, echo (true to gate), lat, om re-authored; last_reviewed 2026-10-06; lattice_drift_check fresh. 23 other non-ok nodes not individually verified; hpipe unchecked.
- **Old Anthropic key, local files:** `arcs-v9/.env`, `~/.hermes/.env`, `arcs-care-local/.env.local` now hold the new key (fingerprint matches `.env.local`; hermes probe OK). Not touched: `~/.vercel/.env.preview.local` (auto-pulled), Vercel arcs-care and arcs production keys (last updated 131 and 134 days ago), GitHub arcs-care secret. `~/arcs/.env.local` and `~/question-compass/.env.local` hold valid keys of unknown org.
- **Sessions archived (harvested, clean):** Issues-as-SSOT, receipt-efficacy, DeFi review, plus six earlier. PM application session NOT archived: 2 untracked files (`_ARTIFACTS/forge-nous-hermes-pm/` resume + cover HTML).

## Current state
- main tip `acd41a12`; CI on it still running at handoff (the prior tip `4a05a4b2` passed). Deploy of the latest commits unconfirmed.
- Open PRs: #730 draft, #557 better-sqlite3 major.
- Tracker "needs a decision" now 5 rows: confidence-claim-unit-v1, lattice-regenerate, og-image-unfurl-check, old-anthropic-account, write-lock-adr-085.

## Decisions made
- Landing control: sessions ask the orchestrator for "cleared" before merging; merge with --merge on all-green only; one receipt per merge.
- Budget rules (memory session-budget-discipline-cap-parallel-molt-long): max 4 live sessions; molt past ~150k context or ~8h; no fan-out for small jobs; cheap models for mechanical work.
- Zach picks (10-06): fewer-permission-prompts, local security-review before PRs, keep repo nci-scoring and retire the anthropic-skills duplicate.
- Zach: tag the 189 pre-09-21 founder receipts as test (confirmed in session, count verified 189 before write).
- Zach: log the five receipts; merge #1033, #1035, #1037 with --merge; delete merged branches; commit and push each follow-up.
- Rule used: silence counts as evidence only for required routine disclosures; conflict-of-interest stories (pardon, Lutnick/Tether, Sacks, IRS/Epstein) stay out of attribution, kept as sourced facts versus alleged claims.
- Archive exemption + baseline (not bulk qualify); flip block now. Park #700. Archive only 4 of 17 orphan scripts (rest have tests/callers). Close pulse-oracle ADR row and Alexandria apex row. Add arcs-skills marketplace. Fix cost before landing #934. Stay in one session instead of a Fable orchestrator.
- Approve defaults; keep adr_cite_lint manual; Librarian: sample first, then bands, then name bonus 0.2 then loop fix; trash the 3 ATS PDFs; apply the lattice evidence table as a PR; stay in one session.

## Open decisions (waiting on Zach)
1. Zach: tag the 20 founder receipts since 2026-09-21 as test or real individually; real cohort is empty until he files real ones.
2. Zach: confirm the next artifacts. Requested, not started: an NFTT post (nftt-story-factory skill, LITERARY theme, good.arcs.care/blog/nftt/<slug>) and a follow-up LinkedIn article. Publishing either needs Zach's explicit yes, the PII gate and a decision_receipt row.

## Open (other)
1. **Jarrod / Success Academy:** an unsent Gmail DRAFT nudge to Brian Mayer sits in thread `1a0d48867025d2b3`
   (reply to brian.mayer@automatedindustries.ai). Plan: send Tue 10-06 only if Jarrod is still silent. Zach sends, never Claude.
2. **Found, not fixed (from closed #777):** the dependency sweep script that /night-moves names was never merged to main,
   so the digest's section 6 runs by eye; and two separate handoffs were both numbered v3.79.0 (#750 merged, #738).
3. Old Anthropic keys: move/delete the remaining copies, then revoke in the old org console (CLI chore list in the 10-06 orchestration chat; list in #958).
4. ADR-085 acceptance re-decision ~2026-10-13 (train as the only merge path).
5. Close the 7 SECRETLY-DONE backlog rows with `scripts/backlog_ripeness.py --apply-closes`.
6. P1: GitHub Actions minutes leak (~200 CI runs/day x 6 jobs, per-job minute rounding). Fix: collapse CI jobs, path-filter heavy jobs, fold `intent` into CI, skip drafts, merge-train batching, daily spend line in the morning note.
7. Cheap adds: CLAUDE.md rule "run local security-review before opening a PR"; note the nci-scoring duplicate decision.
8. Run `fewer-permission-prompts` as its own session (heavy read).
9. FieldOS explorer: gated on Issues SSOT + server-side /api/pulse; then one `field-state.json` contract (internal + public-safe tiers), then the explorer reusing arcs.care dataviz / terrain-atlas / Observatory.
10. Supabase billing page check (plan, compute, add-ons); no preview branches exist.
11. Real receipts need passing provenance:"real" + resolveBy (no UI yet, API body only).
12. Run scripts/accountant_weekly.py with the new export columns and confirm the test/real cohorts show up.
13. Writing synthetic outcomes to prod (plumbing proof against the real route) needs Zach's explicit yes.
14. Orchestrator owns the tracker row outcome-closure-gap.
15. Decisive test not run: were USD1 mints funded by USDC redemptions? Needs Binance conversion data or an entity-level USDC burn list (Arkham, Nansen, CryptoQuant exchange netflows, all paid).
16. Draft post unpublished; figures still secondary: Tether attestation (via press), January liquidation totals, Binance campaign details, Unusual Whales posts (WSJ report on WLF/UAE unverified; coverage thin before Jan 15).
17. CoinGecko daily points are 00:00 UTC snapshots (one-day offset versus events); DefiLlama and CoinGecko USDC differ by about $1B on some days.
18. Old Anthropic keys: move/delete remaining copies, then revoke (list in #958).
19. ADR-085 acceptance and step 3 about 2026-10-13.
20. Confidence claim unit v1 (spec-table diff to draft) and Librarian prescore calibration (sample to lay out): chosen today, not started.
21. og:image per host: which of the 72 static hosts should unfurl.
22. PM session worktree holds 2 untracked files (Nous Hermes resume + cover HTML in _ARTIFACTS/forge-nous-hermes-pm/): commit or keep local before archiving that session.
23. 7 SECRETLY-DONE backlog rows: `scripts/backlog_ripeness.py --apply-closes` (not run).
24. Lattice epoch (2026-09-03) is judgment layer; needs a human re-author.
25. **ADR → Queue workflow fails on any push touching 2+ ADR files** (multi-line GITHUB_OUTPUT; runs 37499499209, 37481234702, 37472043262). Fix: heredoc output.
26. `backlog_issue_sync.py debt` has no update/sync step; until it does, tracker edits must be mirrored to issues by hand (done once today), and `debt pull` only stamps `synced`.
27. Baseline-only-shrinks check; measure Actions minutes saved on real PRs; fold the `changes` job.
28. status.arcs.care: map each section to its source (stamped, live, Issues-derived, hand-written) and add a check for stale hand-written dated numbers.
29. adr_cite_lint: 82 suspects not hand-verified; decide manual aid vs advisory CI.
30. frontend-design plugin is project-scoped to the stale /Users/zharris/arcs clone; disable there or leave.
31. Cheap adds: CLAUDE.md rule "run local security-review before opening a PR"; note the nci-scoring duplicate decision (keep repo copy). fewer-permission-prompts as its own session. FieldOS explorer. Supabase billing page check. 8 scheduled-task sessions left unarchived.
32. **Claim unit v1:** adopt (series breaks), keep v0, or run both. Adoption also needs the confidence function re-landed.
33. **Lattice:** kai status (aspirational vs partial); what the lat "100 receipts" gate counts (total about 267 vs external 10).
34. **og:image:** which of the 72 static subdomain pages should unfurl (they have no og or twitter tags).
35. **Old keys:** update Vercel arcs-care and arcs (production, check Preview/Development), GitHub arcs-care secret, then revoke the old key in the old org console. Check ~/arcs and ~/question-compass keys' org.
36. **ADR-085 about 2026-10-13:** accept and decide step 3 (default `--lock`) together.
37. PM session files: commit or keep local, then archive it. Also still open from the earlier fragment: 7 SECRETLY-DONE backlog rows (`backlog_ripeness.py --apply-closes`), disable frontend-design plugin at the stale clone (optional).
38. Merge-train speedup: `changes` job treats scripts/ and .github/ as app code, so Python-only PRs wait about 8 minutes on fe-smoke. Restrict app code to src/, public/, prisma/, tests/, package files, next.config.
39. no-squash check failed 18:33Z on `1d4b35d3`, cause not diagnosed (local rerun only flagged unfetched merge commits).
40. Librarian: more labelled picks; todd_hotes miss; the maybe volume on broad queries.
41. status.arcs.care module mapping and a stale-number check; baseline-only-shrinks check; debt sync needs an update step.
42. hpipe lattice node: do stages 1-2 have a runtime representation? Unchecked.
43. Earlier fragment's list still stands (Actions cost measurement, ADR citation spot checks, cheap adds, fewer-permission-prompts, FieldOS explorer, Supabase billing).

## Next action
Confirm CI and the Vercel deploy are green on main `acd41a12`, then clear the 5 decision rows with Zach.

## Cold-start recipe
- Tracker link above (filter "Needs a decision"); `python3 scripts/release_notes.py --since 2026-10-06` for what landed.
- Librarian: `python3 operators/arcs_librarian.py "<query>" --stakes medium`; knobs live in `runtime/specs/read-friction-tiers.json`.
- Merge path: `scripts/merge_train.sh --lock --yes <PRs>` (refuses any PR with a failed or cancelled check; re-run stale reds first).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261006T141643Z--claude-handoff-carry-811.md` (branch `claude/handoff-carry-811`, head `7fdfdf3c`); `_HANDOFFS/fragments/20261006T160909Z--claude-handoff-orchestrator-molt.md` (branch `claude/handoff-orchestrator-molt`, head `7073958e`); `_HANDOFFS/fragments/20261006T163645Z--claude-confident-kare-bcdb8c.md` (branch `claude/confident-kare-bcdb8c`, head `dc50746b`); `_HANDOFFS/fragments/20261006T181646Z--claude-defi-crypto-predictions-review.md` (branch `claude/defi-crypto-predictions-review-bad684 (merged and deleted)`, head `81a6d5a4`); `_HANDOFFS/fragments/20261006T183213Z--claude-docs-reconciliation-orchestration.md` (branch `claude/docs-reconciliation-next-06852d (worked from worktree orchestration-repo-cleanup-6f304f)`, head `df007580`); `_HANDOFFS/fragments/20261007T025007Z--claude-docs-reconciliation-evening.md` (branch `claude/docs-reconciliation-next-06852d (worked from worktree orchestration-repo-cleanup-6f304f)`, head `acd41a12`).

# Handoff — v3.115.0 (2026-10-06)

> Two sessions. One shipped the Question Compass UX and lint cleanup (#887, #918; ESLint 174 errors to 0, deploys READY) but got no CI verdict because GitHub Actions is billing-blocked. The other audited every caller still holding an old capped-org Anthropic key (read-only, fingerprints and free probes) and handed Zach the move list (#958).

## Goal / true north
Keep the paid surfaces honest on 2026-10-06: Anthropic spend on the one new key, Question Compass shipped clean with CI verdicts.

## What changed
- Compared key fingerprints (sha256 prefix, never values) against the new key and sent a 1-token probe (capped org answers "usage limit" for free).
- On the new key: arcs-v9 `.env.local`, Vercel arcs-v9, GitHub arcs-v9 secret. Morning jobs task goes through the site, so also new.
- On the old capped org (probed): `arcs-v9/.env` (scripts that load `.env` still spend there), `~/.hermes/.env`, `arcs-care-local/.env.local` + `~/.vercel/.env.preview.local`.
- Old by date (set May 2026, not probed): Vercel arcs-care, arcs, arcs-decision-receipts; GitHub arcs-care secret.
- None in scheduled tasks, `~/.arcs/jobs-pipeline.env`, or shell rc; no local n8n.
- **#887:** receipt Y-gate verdict under True North, headings, AA contrast on the dashboard, 16px inputs (no iOS zoom), a wrapping dashboard heading,
   server refusals skip the 15s receipt-recovery poll and the error is `role="alert"` under the button. Lint: `public/**` ignored, 64 JSX entities
   escaped, hook-rule errors fixed in 5 files, `tests/unit` `any` removed, `sage_efficacy` and the PRL parser test moved to `.mjs`.
   Rebased onto main twice (main kept moving; the pre-commit kintsugi gate blocks a local merge commit that carries main's resume HTML).
- **#918:** True North statement is the `h1` in `AhmedOrder` (receipt and brief share it).
- **Deploy:** production deployments of `68024c46` and `8ff408e7` are READY, aliased to `app.arcs.care`.

## Current state
- Anthropic: new key in arcs-v9 `.env.local`, Vercel arcs-v9, GitHub arcs-v9. Old capped org still in `arcs-v9/.env`, `~/.hermes/.env`, `arcs-care-local/.env.local`, Vercel arcs-care/arcs/arcs-decision-receipts, GitHub arcs-care secret.
- Compass: `68024c46` and `8ff408e7` READY on app.arcs.care; local Playwright 302 passed; no CI verdict (Actions blocked).

## Decisions made
- Zach owns all key moves and revocations; tracker row `old-anthropic-account` is status decision, owner Zach.
- #887 and #918 merged with `--merge` on Zach's yes.

## Open decisions (waiting on Zach)
1. Zach: move or delete the old-org keys above, then revoke the old keys in the old org console.

## Open (other)
1. question-compass and the stale `~/arcs` clone hold working keys that are not the new key; org unknown (check in console).
2. Cloud n8n not checked; `~/.bash_history` holds 2 capped-org keys in plain text (harmless once revoked).
3. GitHub Actions billing or spending limit is blocking runs again (human). No PR or main commit has a CI verdict until it is fixed.
4. Receipt row for #918 needs the two corrections above if the table should match (a project-scoped Supabase connector worked for UPDATEs in an earlier session).
5. Not done from the audit: sub-44px touch targets, sub-12px mono labels, 51 ESLint warnings.
6. (Fixed 2026-10-06: ADR-026 and ADR-059 now cite `scripts/sage_efficacy.mjs`.)

## Next action
Zach: unblock GitHub Actions billing, then move or delete the old-org Anthropic keys and revoke them in the old org console.

## Cold-start recipe
- Tracker: https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm (rows `old-anthropic-account`).
- Key check without exposure: memory `anthropic-key-three-homes-verify-without-exposing` (sha256 prefix compare; 1-token probe, capped org replies "usage limit").
- Receipts: `2026-10-06--old-anthropic-key-caller-audit--ZH`, `2026-10-06--compass-ux-lint-cleanup-pr887--ZH`, `2026-10-06--receipt-h1-pr918--ZH`.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261006T143343Z--claude-handoff-anthropic-key-audit.md
> **Old Anthropic org key audit (read-only): 8 places still use the capped account; Zach moves and revokes.** Receipt
> `2026-10-06--old-anthropic-key-caller-audit--ZH`. Docs Reconciliation row `old-anthropic-account` set to v3, status decision, owner Zach.

### Notes: lead of 20261006T143350Z--claude-handoff-compass-lint.md
### Shavasana — handoff pause, 2026-10-06 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-compass-lint), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 1 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 5 / dissent 2 (ratio 1.67) → OK: dissent present.
- **Cold re-read (canary on the draft handoff-draft.md)**: GROUNDED; no ground return: none; thin air: none.


- **Attachment release** (judgment): every claim re-read cold. The deploy and local-suite claims are measured (deployment IDs, run counts); the
  receipt corrections are stated as stale-but-unwritten, not as fixed. Nothing downgraded.
- **Somatic read**: not asked.
- **Disposition**: release.

> **Question Compass smoke test and audit shipped: UX fixes plus repo-wide ESLint 174 errors to 0 (#887, `68024c46`), then the receipt h1 (#918, `8ff408e7`).**
> Both merged with `--merge` on Zach's yes. Receipts `2026-10-06--compass-ux-lint-cleanup-pr887--ZH` and `2026-10-06--receipt-h1-pr918--ZH`.

### Notes: Lessons
- `arcs-v9/.env` and `.env.local` held different keys: Next reads `.env.local` first, so the site looked fixed while scripts kept the old key.
- A capped-org probe costs nothing and names the org; a fingerprint match only proves "same as new key".

### Notes: Corrections to the receipts (the Supabase UPDATE was declined, so they live here)
Receipt `2026-10-06--receipt-h1-pr918--ZH` still lists `fe-smoke` as pending and the deploy as unverified. Both are stale:
- Deploy of `8ff408e7` is READY (dpl_Gwh3BNDHhRjZcwRcRjYAS9BAtQLw), `app.arcs.care/dashboard` returned 200.
- `fe-smoke` never produced a CI verdict. The PR run hung 16+ minutes, main's runs on `8ff408e7` were cancelled by `cancel-in-progress`,
  and later runs refused to start (GitHub Actions payment or spending-limit block).
- The only evidence is local: the full Playwright suite on a production build of main `48c44214` (includes `8ff408e7`) ran 302 passed, 3 skipped, 0 failed.
- Not confirmed: the live production receipt page `h1` was not viewed.

### Notes: Lessons
- A local production server needs `AUTH_TRUST_HOST=true` or `/api/auth/session` returns 500 and the smoke console-error tests fail for a reason that is not the code.
- `npm run test:smoke` runs all of `tests/`, and one spec rewrites `_ARTIFACTS/atlas/atlas-almanac.html`; restore it before committing.

> Molted from `_HANDOFFS/fragments/20261006T143343Z--claude-handoff-anthropic-key-audit.md` (branch `claude/handoff-anthropic-key-audit`, head `b04f43d5`); `_HANDOFFS/fragments/20261006T143350Z--claude-handoff-compass-lint.md` (branch `claude/handoff-compass-lint`, head `b04f43d5`).
