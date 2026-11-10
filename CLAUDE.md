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

# Handoff — v3.143.0 (2026-11-10)

> ### Shavasana — handoff pause, 2026-11-08 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 1 commits, 1 merges to main (scope: branch claude/allowlist-read-only-batch), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 1 unconfirmed markers in the day's records.
> - **Breath balance**: manifesto (exhale, no inhale).
> - **Sycophancy check**: agreement 7 / dissent 1 (ratio 3.5) → OK: dissent present.
> - **Cold re-read (canary on the draft handoff-frag.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: every claim cites a PR, merge sha, receipt id or file; kept. "Production deploy not checked" stays unconfirmed. Somatic: not asked. Disposition: release.
>
> > Louisville proposal session, 2026-11-06 to 11-08: the build pipeline and PDF gate landed, the PDF was redesigned from the page's own parts, and the page was rewritten audit-first with a give/get time trade. Plus side work: a plain-verb /catalog table, backlog routing at induction, a sanity-check agent, an allowlist batch, and the main checkout moved onto origin/main.
>
> > Rebuilt good.arcs.care/rfp-engine from verbatim UI kit blocks with earned-fidelity rendering, merged as PR 2110, live and receipted.
>
> ### Shavasana — handoff pause, 2026-11-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/rfp-engine-handoff), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: breathing (both directions).
> - **Sycophancy check**: agreement 2 / dissent 0 (ratio 2.0) → OK: dissent present.
> - **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: every claim cites a PR, sha, path or receipt id; the light-mode claim is held to "headless screenshot at 1280 only". Somatic: not asked. Disposition: release.
>
> > My Ally hub polish and docs restyle, the permission allowlist, then orchestration of the Gravity (Harrison Wright) brief through review and merge, 2026-11-06 to 2026-11-10.
>
> ### Shavasana — handoff pause, 2026-11-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)
>
> - **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-myally-gravity-2026-11-10), receipts in digest: no digest file.
> - **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
> - **Breath balance**: breathing (both directions).
> - **Sycophancy check**: agreement 8 / dissent 0 (ratio 8.0) → RETURN: agreement with no dissent on record.
> - **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
> - **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
> - **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
> - **Disposition** (human): release the handoff, or return it to the queue with this block attached.
>
> _This block asserts nothing new. Counts, paths, and questions only._
>
> - Attachment release: the sycophancy check returned RETURN (no dissent marker in the day's records). Dissent did happen and is recorded here: I corrected Zach's reading of the Bull vs Bear rows (the bull row is transaction counts, not cost; Allium is a volume filter, not a trend signal), and PR 2115 kept three parts over Grug's cut. Two claims are held as the owner session's report, not checked by me: PR 2120's gates, and Zach's approval of the four rows. Somatic: not asked. Disposition: release, with RETURN noted.

## Goal / true north
Get the My Ally Step 1 agreement and hub in front of the founders, and get the Gravity Labs brief to a reviewed, merged state Zach can send.

## What changed
- #1891 free repo check at good.arcs.care/audit/check (receipt 2026-10-31--audit-check-pr1891--ZH)
- #1896 audit report generator, cold-1 as the first sample (receipt 2026-10-31--audit-report-gen-pr1896--ZH)
- #1898 /audit and /audit/check re-poured onto current kit tokens; 3 design waivers deleted (receipt 2026-11-01--audit-kit-converge-pr1898--ZH)
- #1900 RFP engine card on the good.arcs.care index (receipt 2026-11-01--good-index-rfp-pr1900--ZH)
- #1902 NFTT post "!Hot-Fix to The Idempotent Fix" (receipt 2026-11-01--nftt-idempotent-fix-pr1902--ZH)
- #1904 cold-1 report through two counterpart gauntlets and a grug pass (receipt 2026-11-01--audit-report-gauntlets-pr1904--ZH)
- #1907 HUD ripples labelled "roadmap waypoints, not data"; merged over a stuck fe-smoke on Zach's go (receipt 2026-11-01--hud-ripples-label-pr1907--ZH)
- fbc2920d universe snapshot refresh, history epoch 1 as of 286a9dad (receipt 2026-11-01--universe-snapshot-refresh-epoch1--ZH)
- #1911 WORLD.md "THE HUD" section (route-finding, three layers); merged by another session with its own receipt
- Sessions started from here merged #1903, #1905, #1909 (kit pull), #1912 (HUD widget registry), #1913, #1914, #1916 (gate hygiene), #1919, #1920 (flight manual), each with its own receipt per their reports
- #2054 merged (`b0609c04`): `scripts/proposal_build.py` and the PDF checks in `page_gate.py`; receipt 2026-11-06--proposal-build-pipeline-pr2054--ZH
- #2062 merged (`6e12621e`): PDF redesign (cover with contents line, running header and footer, numbered sections); receipt 2026-11-08--louisville-pdf-design-pr2062--ZH
- #2064 merged (`ed76a041`): the three-part rule planted, then echoed on the RFP engine card; receipt 2026-11-08--louisville-rfp-tie-in-pr2064--ZH
- #2069 merged (`ca47d910`): give/get grid, trimmed list, H2 sections, audit-first rewrite through two decisions; receipt 2026-11-08--louisville-audit-first-give-get-pr2069--ZH
- #2082 merged (`d4d064cc`): read-only allowlist batch; receipt 2026-11-08--allowlist-read-only-batch-pr2082--ZH (job_id NULL, no backlog row)
- Child sessions: #2065 /catalog plain-verb table (`0807af01`), #2067 backlog rows need a route and a trigger (`b66b5bce`), #2079 sanity-check agent (`64796b29`), #2083 sanity-check sample 1 (`c37e0334`); each filed its own receipt.
- The main checkout was moved to detached origin/main (`d4d064cc`). Its four edits are saved on local branch `backup/main-checkout-wip-2026-11-08`.
- PR 2110 merged (`2d877499`, head `bdce89e6`); receipt 2026-11-10--rfp-engine-kit-rebuild-pr2110--ZH (job:backlog:rfp-engine-public-good, tool:script:safe_merge.sh).
- `public/good-rfp-engine.html` now carries kit blocks 27 section-label, 30 button, 37 fidelity, 39 theme, 45 fact-tile and 51 display preferences, plus the generated grammar-chip CSS; tool swatch moved to steel `#3d6a9e` (plan C).
- `.impeccable/config.json`: four one-file waivers for kit-origin findings on this page; seam booked in `_PATTERNS/kintsugi-visual-grammar-seams.md`.
- `_QUEUE/induced-backlog.jsonl`: anthropic-spend-monitor resolve_by moved 2026-11-09 to 2026-11-16 (Zach), which had failed jtbd-graph --check for every commit.
- PRs 2087, 2101 (My Ally hub polish), 2103 (fewer-permission-prompts allowlist) and 2104 (classname_guard kit CSS) merged; prod READY at 4b1e9f83; a receipt for each.
- Word file and Google Doc restyled to match the PDF (same Doc link).
- Gravity: PR 2074 merged (9619bf1d); gravity.arcs.care live behind GRAVITY_PASSCODE. PR 2114 merged (6ea9b0bb, proof-of-judgment rework, two review rounds). PR 2117 merged (byline, dated forecast). PR 2115 merged (65311f6b, token tuner: breakpoint, wrap, rhythm and in-place text edit with a JSON patch).
- Bull vs Bear rebuild brief sent to the Harrison session (local_9625ee21) on Zach's "Yes, send it"; result is PR 2120.

## Current state
- PR 2120 (signal-ledger kit part, four approved rows, four real recommendation quotes in the hero) is open and MERGEABLE, gates reported passing by its owner session; not merged.
- PR 2073 (Wright recoil close + findings) is open and MERGEABLE; the war-room report renders only after it merges.
- The war room has no password: /warroom/[slug]/recoil is Auth.js sign-in plus ADMIN_EMAILS; RECOIL_PASSWORD is retired.
- The page editor works on tabbed-brief pages only (Gravity's five): `scripts/tabbed_brief_build.py --tune OUT.html`, then `?tune` or `?edit`, Copy JSON, `--apply PATCH.json`. Other single-file pages get sliders only via `scripts/token_tuner_inline.py`.
- Louisville: louisville.arcs.care/proposal serves "A checkup on your AI build" (PR 2119, curl-checked). Row brooks-audit-proposal-send is HOLDING on Jeben's review; Zach sends.

## Decisions made
- Zach: drop the repo-alias claim on the cold-1 report.
- Zach: the HUD's shared mental model is "the clearest, safest approach to a destination", loading terrain, route and time (belief change).
- Zach: refresh the universe snapshot; ratify the 2-of-3 cold-read threshold.
- Zach: merge #1907 over the stuck fe-smoke check; hold #1917.
- Positioning frame: "cold start problem / cold read problem", one problem from two sides; receipts solve both.
- Zach: audit first. Adobo is one example decision, not the subject, because leading with it read as a disconnect from his ask.
- Zach: two decisions, one technical and one business ("decisions, not phone calls").
- Zach: no Justin session and no security session in the give list; the optional call is staffed by Brooks.
- Zach: keep 50/50 for Brooks. Default terms by size: about $2K or under 100% up front, larger fixed fee 50/50, multi-month monthly.
- Zach: no tiers or second lane on the page until a receipt exists (the Jeben-era tiers stay air-gapped).
- myAlly asks typed here by mistake went to the Sync MyAlly hub session (PR 2059 owner).
- Zach: keep OS-following light/dark rather than pinning dark.
- Zach: move the expired resolve_by to 2026-11-16 rather than skip the hook.
- The chip block's internal sentinel comment was removed from the public copy (J24 leak check), not allowlisted; nothing reads it on the page.
- Zach: approved all four candidate Bull vs Bear rows (cost per payment, AML/KYC blind spot, Put beside the Call, reading errors), per the owner session's report.
- One owner per PR branch: the Harrison session owns 2073, 2117 and 2120; this session only briefed it.

## Open decisions (waiting on Zach)
1. Zach: grade the s5 blind-judging sheet, runtime/specs/jtbd-s5-quality/JUDGE.md.
2. Zach: read and approve the DRAFT abort and rollback on backlog row agent-receipts-audit-first-conversion (releases 4 rows; conviction 75 given).
3. Zach: accept or reject ADR-090, ADR-091, ADR-092 (PROPOSED).
4. Zach: #1917 hold, trim to sourced gauges, or keep.
5. Zach: send Brooks the link, with the passcode in a separate message; delete stale Gmail drafts.
6. Zach: file the ex-ante receipt at send, scope line "two decisions, $5K, no tiers until a receipt".
7. Zach: check the live gated page and PDF after deploy.
8. Zach: cold-read header (Why, What, Why now, How, How to read) is not applied to tool-getting-started pages; a template-level decision.
9. Zach: merge PR 2120 and PR 2073 (say it in the Harrison session, which owns them).
10. Zach: confirm Jeben's review of the Brooks proposal, then send it himself.
11. Zach: send the Harrison note himself; then mark row gravity-eir-candidate-brief DONE.

## Open (other)
1. Repo cold read to hardened README to video session is running; it stops for Zach after the README PR and before any paid voice or upload.
2. Approvals ledger gap: a merge (#1912) landed when its session reported none, and a child session cited a mount approval not given in the parent. The flight manual's ledger script now lists approvals; enforcing the cruise agent's no-merge limit is still open (#1922).
3. Reading Room digests have not been re-graded since 2026-09; 19 of 20 slices dirty; nothing regenerates them.
4. No canon file maps public surfaces to roles and on and off ramps.
5. Sanity-check agent has 1 of 3 fresh samples; run it before any future proposal polish round.
6. Open backlog rows from the verb table: decompose-page-atomic-params, catalog-verb-table-drift-check.
7. Kit file 45 fact-tile label is .75rem, off the type ramp; fix in the kit file, then drop the font-size waiver.
8. The video facade on this page is a candidate kit primitive.
9. Copying the grammar chip block onto a public page needs its sentinel stripped; no build step does this yet.
10. My Ally discovery is over its cap (33.6 to 45.9 h unpaid vs a 10 h cap, sentry finding): a choice to make on purpose.
11. Optional: wire the editor onto My Ally and Louisville (needs the tabbed-brief data build for text editing).

## Next action
Zach reviews PR 2120 in the Harrison session and gives or withholds the merge go.

## Cold-start recipe
- Read PR 2120 and PR 2073 descriptions; `gh pr view 2120`.
- Editor how-to: PR 2115 description.
- Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: Lessons
- Fix the mold, not the cast: a hand edit to a generated page is refused; edit the generator or its data.
- A stale status note on a DONE row misled this session into reporting a ruling as pending; read the state field, not the prose.
- Pages that inline an old token copy fall back to browser defaults with no error, and the design detector still scores them 0; check a re-tokened page in a real browser.
- Relayed approvals must be quoted verbatim and labelled relayed in the receipt.

### Notes: Shavasana
- Exhale and inhale as printed by scripts/shavasana_handoff.py on this draft: canary GROUNDED, no ground return none, thin air none.
- Sycophancy check: THIN (agreement 10, dissent 1). Dissent on record this session: refused "100% reconstructable" for a 5,000-commit repo; corrected "ziggurat as the altitude axis" after the moire audit's network finding; retracted the nested-doll load-in object and flocking as new work once prior art was read; recommended holding #1917 over Zach's earlier yes.
- Attachment release: merges by other sessions are stated "per their reports"; #1915, #1921, #1922, #1923 are listed as not confirmed here.
- Somatic: not asked.
- Disposition: release.

> Molted from `_HANDOFFS/fragments/20261101T051357Z--claude-handoff-audit-hud-night.md` (branch `claude/handoff-audit-hud-night`, head `9d596480`); `_HANDOFFS/fragments/20261109T040317Z--claude-handoff-louisville-2026-11-08.md` (branch `claude/handoff-louisville-2026-11-08`, head `d4d064cc`); `_HANDOFFS/fragments/20261110T142439Z--claude-rfp-engine-handoff.md` (branch `claude/rfp-engine-handoff`, head `2d877499`); `_HANDOFFS/fragments/20261110T172255Z--claude-handoff-myally-gravity-2026-11-10.md` (branch `claude/handoff-myally-gravity-2026-11-10`, head `e4784510`).
