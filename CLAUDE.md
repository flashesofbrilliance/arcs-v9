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

# Handoff — v3.119.0 (2026-10-09)

> > Night-moves scoped to reusable assets, then a hyperstition cut of a draft scope-of-work scaffold for My Ally LD. Draft only; nothing sent, priced or run through Question Compass.
>
> > PRL Phase 1.2 wrap prep for Todd: overview overclaim fixed, go-live checklist folded into the runbook, refresher email drafted; the Oct 9 call moved to Mon Oct 12 10:00 ET.
>
> > PRL go-live checklist made tickable and linked from every go-live summary; refresher email sent to Todd for Mon Oct 12 10:00 ET.

## Goal / true north
Turn the 2026-10-08 My Ally LD call (Kelly Jacobson, Chelsea Starks; founder Leah Gambal) into a send-ready, passcode-gated plain-language proposal plus intake, and send the thank-you. Relationship first: neighbors and shared parent groups, friends-and-family pricing.

## What changed
- Added `_ARTIFACTS/sow-scaffold-2026-10-08/` (asset map, graded scaffold, 31 draft assumptions asm-015 to asm-045 (adds charter hypothesis asm-028 and two UNSUPPORTED judgments) that validate against `scripts/assumptions.py`, cost-baseline template). PR open, not merged; no merge receipt yet.
- PR 1108 (merged): prl.arcs.care overview + runbook no longer claim leads carry the conversation (they carry "Chatbot Lead"; Task C unbuilt); update dated Oct 9; "nothing risky" replaced by two named checks (blank-email guard live, Zapier plan hold). Also fixed pre-existing page-gate failures: claude.ai artifact link, scrollspy error, runbook missing doctype.
- PR 1109 (merged): runbook "Go-live, three steps" expanded in place into a per-system checklist (Sugar, Zapier, Tidio, WordPress) plus a live proof chat; prl.arcs.care/go-live 307s to /status/runbook#go-live. A separate checklist page was started and dropped as a duplicate.
- Receipts logged: 2026-10-09--prl-overview-overclaim-fix-pr1108--ZH, 2026-10-09--prl-runbook-go-live-checklist-pr1109--ZH.
- PR 1111 (merged): runbook #go-live is now four tickable system cards (Sugar, Zapier, Tidio, WordPress) plus a "Prove it live" card; ticks persist per browser (localStorage). Overview (2 spots) and progress (2 spots) link "Full go-live checklist" to /go-live. Progress page got the missing doctype.
- Receipt: 2026-10-09--prl-go-live-cards-links-pr1111--ZH.
- PRs: #1098, #1106, #1107, #1113, #1114 (receipts `2026-10-09--myally-*--ZH`).
- Recoil report + 6-tab war-room SSOT (internal): `runtime/recoil/generated/2026-10-08-myallyld.json` and `runtime/recoil/generated/2026-10-08-myallyld-jacobson-starks.md` (PR 1106).
- myally.arcs.care live behind its own passcode (`src/lib/passcode-gate.ts`, `/api/myally/unlock`, proxy block; env `MYALLY_PASSCODE`; separate cookie so it opens no other gated page). Passcode was rotated to the plain phrase Zach chose.
- Proposal generator `_ARTIFACTS/sow-scaffold-2026-10-08/build_proposal_view.py` (PRs 1098, 1107, 1113, 1114): SEND on; light ARCS FIELD OS wordmark nav; sticky contents rail with scroll highlight (wide) and nested hamburger (<1100px); four detail levels (Summary, Overview, Working detail, Everything) with fit-based columns; How-to box; type roles H1/byline/lede/H2/H3; stages named by purpose (audit and discovery; alignment and refinement; set up to run on your own; strategy and review); feedback stop-loss section; Optional extras (two-week rhythm, office hours); glossary split to `/primer` (Technical primer, back nav; build fails on a missing Learn-more id); Vercel custom events (detail_level, primer, intake click, reading options, section_seen, dwell).
- Tests: `reading_matrix.smoke.cjs` (48 Reading-options combos x 4 widths = 192, incl. a 45-80ch measure gate, proven to fail on bad); page smoke updated for buttons/rail/primer.
- SOW `02`: Track O office hours ($150/hr; async 15-min increments; live 30-min minimum then 15; hard timebox; O.6 in-person workshop), 3c sprint cadence + dependency board, 3d feedback stop-loss FB.1-5, L.10 timeboxed counsel mode (team memo, counsel redlines; never "our HIPAA compliant plan").
- Tally intake form built and published: tally.so/r/xXkrP5 (first page essentials + NDA and spec uploads, later pages optional, Lexend).
- Thank-you email SENT by Zach (version B: his text + plan link/passcode/how-to); he also texted Kelly.

## Current state
- Live and verified: myally.arcs.care and /primer (gate holds without the passcode), all CI green on each merge; receipts logged for PRs 1098/1107/1113/1114.
- Ball is in their court (Zach, 2026-10-09): waiting on their NDA (mutual), intake form and build spec. Reminder set for Wed 2026-10-14.

## Decisions made
- Redaction item changed from deterministic-only to deterministic plus mandatory parent review (deterministic rules miss names in prose).
- Zach's recalled liability figure and any HIPAA/COPPA/BAA applicability claim are excluded; routed to counsel (L.2).
- One home for go-live steps: the existing runbook section, not a new page or artifact.
- Frame Monday as a go-live working session; no 1.3 pitch until the team has used it.
- Friends-and-family pricing; office hours priced in SOW only (generator bans prices on the counterpart page).
- Comments feature tabled (feedback arrives verbally; captured into one email thread).
- Stage 4 trigger line held: their pace, not ours.
- Reading column 600px (~70ch) kept; empty desktop margin used by the contents rail.

## Open decisions (waiting on Zach)
1. Zach: whose entity pays and on whose paper; which vendors are on a card; is cost visibility an outcome; disclose the recording; NDA status; meaning of "by manana"; may Phase 0 use Question Compass on real material after the NDA.
2. Zach: yes/no to append asm-015..045 to the live ledger.
3. Zach: whether to run `counterpart-gauntlet` on the scaffold (multi-agent cost).
4. Zach: review and send the refresher draft.
5. Zach: delete the redundant artifact.
6. Zach: delete redundant private artifact https://claude.ai/artifact/UKGKrsT9ygCUBAARVLqpEy (optional).

## Open (other)
1. Unknown whether the Sep 17 rough edges (lead marked dead, lagged lead, alert email not landing) were fixed; verify before Monday or say so on the call.
2. Blank-email guard verified only in draft; confirm in the published zap on the call.
3. Before Monday: unknown whether Sep 17 rough edges (dead status, lagged lead, alert email) were fixed; blank-email guard verified only in draft.
4. None.
5. When the NDA and spec arrive: run Phase 0 (audit Vault + Alice data flows first), then the written proposal with the friends-and-family rate.
6. Ex-ante receipt in the war room (scope boundary, rate floor) was never filled before send; fill it before the proposal goes out.
7. Watch Vercel Web Analytics Events (section_seen, section_dwell) once they open the page.
8. Real-phone visual check of the live page not done.

## Next action
When their NDA lands, sign and start Phase 0 from the intake answers; draft the proposal only after reading the spec.

## Cold-start recipe
- Rebuild: `python3 _ARTIFACTS/sow-scaffold-2026-10-08/build_proposal_view.py` (writes proposal-view, primer-view, public/myally.html, public/myally-primer.html).
- Gates: `python3 scripts/page_gate.py --matrix full <each of the 4>` (symlink main checkout node_modules into a temp worktree); `NODE_PATH=<main>/node_modules node _ARTIFACTS/sow-scaffold-2026-10-08/reading_matrix.smoke.cjs public/myally.html`.
- Live check: POST passcode to `/api/myally/unlock`, then curl `/` and `/primer` with the cookie.

### Notes: Lessons
- Run the page gate on the draft file that carries the page's own smoke test, not only the hosted copy; CI does.
- Fixed breakpoints break on user-scalable text; measure fit instead (nav, level buttons).
- Never update_draft an email Zach may be editing.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

> Molted from `_HANDOFFS/fragments/20261008T153950Z--claude-sad-mirzakhani-efd807.md` (branch `claude/sad-mirzakhani-efd807`, head `5ecd5c61`); `_HANDOFFS/fragments/20261009T164440Z--claude-prl-handoff-memory-check-6c5e92.md` (branch `claude/prl-handoff-oct9`, head `1ea21eeb`); `_HANDOFFS/fragments/20261009T170621Z--claude-prl-handoff-memory-check-6c5e92-b.md` (branch `claude/prl-handoff-oct9-b`, head `d43bdea4`); `_HANDOFFS/fragments/20261009T175444Z--claude-fervent-napier-9c6c13.md` (branch `claude/fervent-napier-9c6c13`, head `84ddd6cc`).

# Handoff — v3.118.0 (2026-10-07)

## Goal / true north
Land the day's open PRs safely and keep the decision-geometry explorer honest (no private text in the public feed), without burning the 5-hour limit on long Fable contexts.

## What changed
- Merged with --merge and receipts: #1070 (672a797a), #1064 (8ee8ff3b), #1065 (cc85c8b4, owner-set provenance tag; CI security review failed on "Credit balance is too low", local diff review found nothing blocking). #1073 (9 unrouted public pages deleted) was merged by another session; no repo link to them, 8 of 9 return 404 live, lewoof.html is deliberately routed to the gate.
- #1068 and #1069 merged by their own sessions. #1069's catalog was then served through the admin-gated warroom route (c220eb8b), which answers the counterpart-hostname disclosure question.
- Local security review of #1068 found the public /api/geometry feed leaked free-text `protecting` (up to 8 x 200 chars) in the shared base object. Fix e6413821 (gate `prot` on text fidelity, add non-text `protN`, client reads `protN`) landed AFTER #1068 merged, so it is on main only once PR 1082 merges.
- Worktrees: 16 stale ones pruned with bundles (cruft_sweep); live ones, zen-pasteur-85c635 (907 behind, 2 dirty) and pensive-hopper-b6feb8 (1 unmerged commit, 3 salvage claims) kept.

## Current state
- Specs are DRAFT: `runtime/specs/dopeness-eval-v0.md`, `runtime/specs/decision-geometry-cells-v0.json`, `_STATE/2026-10-07-tool-cluster-jtbd-map.json`. The adversarial verifier workflow (14 agents) recorded corrections that are NOT yet folded into the specs. Every refuted and unverifiable verdict plus the critic's missing, unverified and contradiction lists are committed at `_ARTIFACTS/decision-geometry-verify-2026-10-07/verifier-corrections-w7oi2kc36.md` (the full 357 KB JSON lives only on this Mac at `/private/tmp/claude-501/-Users-zharris-arcs-v9--claude-worktrees-compass-dopeness-audit-963f43/2a998756-827f-4413-8e5c-521f02be10e7/tasks/w7oi2kc36.output`, under `result.cells.verify`, `result.clusters.verify`, `result.critic`). Summary:
  - Cells: 12 of 46 claims refuted, 3 unverifiable. Key refutations: DELTA has two triggers (parent nci band shift as well as hasRed, `ygate.ts:170-180`); sessionVersion is parent.version + 1, not a count of session rows; driftState DRIFTING is outcome-driven (matched false) not version-driven; PrepSession.stakes/horizon equal Receipt.stakes/window by assignment so they carry no independent evidence; confidence = 1 is a ygate input so independence holds only for 2 to 5; inline prep can leave prepId null on a calibrated receipt; `observatory/page.tsx:30-36` already defines an L1 to L5 altitude rung map (off by one from the model's); the contract altitude sample uses a U+2013 en-dash so the `L(\d)-L(\d)` parse returns lo=hi=1 on the contract's own sample; "5R: no field" is false (ScanSignal.networkResonance exists, still unmappable to a receipt cell); D1 coverage L2 must read ~267 since coherencePct presence was not measured; the "0 of 267 by code path" for six columns rests on a route grep, not SQL.
  - Clusters: 4 of 16 spot checks refuted: `arcs_no_go_inventory.py` and `arcs_seed_bar.py` are not decision-lens members (post-hoc failure catalog; BAR there means Belief-Action-Rationale templates); `sugar_bulk.py` is a PRL CRM payload builder, not counterpart-facing; `fates.py` is the fate registry, not page authoring. The map also double-books 11 tools as both members and orphans.
  - Critic: `src/app/api/tribune/route.ts:205` writes batonId (so "no write path" is wrong for that column); `provenance` is client-settable by any signed-in caller; the founder userId is unrecorded so the founder cohort split is assumed; COURT and ONE_WAY are one predicate in `compass/route.ts` (same 96 rows by construction); the shipped `parseKairos` differs from the cell model's parse; ladder tier A's GREEN clause is not SHARP (CONTESTED renders DEGRADED); ladder fields use pseudo-paths not prisma names; the day-counting unit differs between tier D (sessionId) and tier B (userId).
- Admin fidelity shows no banner by design (only public and owner set one); the fidelity statement lives in the stats line.

## Decisions made
- Merge handled by the originating session; this session verified only and did not merge.
- Receipt logged in the fixed form with the JS-dispatched drawer open listed as unconfirmed rather than claimed as a click.

## Open decisions (waiting on Zach)
None.

## Open (other)
1. Merge PR 1082 (the prot fix). Until then the leak is live on main.
2. claude-security-review fails on every PR until the CI Anthropic key's org has credit (human).
3. GEOMETRY_PUBLIC defaults to on (open to anonymous callers); decide whether to default it off.
4. scripts/dependency_sweep.py is named in the night-moves skill but is absent on main.

## Next action
Fold the verifier corrections into `runtime/specs/dopeness-eval-v0.md` and `decision-geometry-cells-v0.json` (start with batonId write path and client-settable provenance), then mark them past DRAFT.

## Cold-start recipe
- Page: `public/pf-decision-geometry.html`; feed: `src/app/api/geometry/route.ts`; rewrites: `next.config.ts` lines 92 to 96 (playground) and 205 to 208 (app).
- Gate: `SMOKE_BASE_URL=https://playground.arcs.care npx playwright test tests/decision-geometry.spec.ts --reporter=line`.
- Feed shape check: `curl -s https://playground.arcs.care/api/geometry | head -c 600` must show no `"q":` and only `"t":"YYYY-MM-DD"`.
- Receipt: `2026-10-07--decision-geometry-explorer-verify-pr1068--ZH`.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: Lessons
- Claude in Chrome clicks on a canvas can land on neighbouring controls; prove a pick by dispatching the page's own pointer events and reading the drawer state, and record it as a dispatch, not a click.

> Molted from `_HANDOFFS/fragments/20261007T180720Z--claude-keen-hermann-e14d76.md` (branch `claude/keen-hermann-e14d76`, head `cc85c8b4`).
