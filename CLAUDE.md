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

# Handoff — v3.128.0 (2026-10-11)

> 2026-10-10 close: arcs.care/hud is live after #1174, the Louisville nav receipt was corrected with a new row, and Zach's request to use every briefing resource went to the take-home session as a resource x plan audit.

## Goal / true north
Ship the monday.com take-home by Thu 2026-10-15 17:00 ET using every resource the briefing listed, or a recorded reason not to.

## What changed
- #1255 merged (`8230c5a7`): 2026-10-10 digest update to 22:10 (#1245, #1247 to #1250; open #1251, #1252, #1253), the merge-on-pending lesson, and the 22:10 dependency sweep. Receipt `2026-10-10--night-moves-2210-update-pr1255--ZH`.
- Correction receipt `2026-10-10--louisville-nav-receipt-correction-pr1231--ZH`: #1231 merged at 01:54Z with fe-smoke still in progress on the merged head; fe-smoke then passed (job 114363497301). Updating the original receipt was declined twice, so a new row records it.
- #1254 merged (`65122ea6`): molt of 3 fragments into handoff v3.127.0; one line reworded to cite #1174 instead of an unmerged SHA, no gate bypass. Receipt `2026-10-10--handoff-molt-v3.127.0-pr1254--ZH`.
- #1174 found already merged by its owning session (02:10Z, `12f27a7e`, all checks green); arcs.care/hud returned 404 until the production build finished, then 200. Screenshots at 1440 and 375 sent to Zach.
- Relayed to session "Continue monday take-home from HANDOFF.md" (delivered): serialize all plans, read the 9 briefing resources, build a resource x plan matrix, show Zach before any code change.

## Current state
- No decision receipt exists for #1174 yet (queried decision_receipt); left to its owning session to avoid a duplicate.
- Read-only grep of ~/ret-rfp-intelligence: Academy, the JS SDK @mondaydotcomorg/api, the MCP Setup Guide and LangGraph appear in 0 files; DECISIONS.md D-MCP rejects MCP and the Python SDK but never names the JS SDK.

## Decisions made
- Record a correction as a new receipt row rather than editing a logged one.
- Route the briefing audit to the take-home session (it owns the repo and the scope freeze) instead of doing it here.

## Open decisions (waiting on Zach)
1. Zach: take-home dress rehearsal once ONBOARDING.md lands; submit by Thu 2026-10-15 17:00 ET.
2. Zach: approve the tool prompts in the "Held dependency exceptions watch" run.
3. Zach: confirm the better-sqlite3 bump (#557) was an approved dependency change.

## Open (other)
1. Take-home session: deliver the resource x plan matrix to Zach before changing code.
2. "Make arcs.care/hud the full-screen 5D explorer" session: log the #1174 merge receipt (none in decision_receipt as of this molt).
3. On or after 2026-10-13: `python3 scripts/backlog_status_check.py --gh`; confirm or close each RUNNING row it flags.
4. The Oct-06 Success Academy check-in to Brian is still unconfirmed in Gmail.
5. After submission: atlas-bundle.v1 export, replay booth kickoff 17:30, then the admin route per runtime/specs/atlas-bundle-observatory-spec.md v0.4.
6. Vico intro Wed 2026-10-14 13:00 ET.

## Next action
PRL go-live call with Todd, Mon 2026-10-12 10:00 ET.

## Cold-start recipe
- /handoff-pickup; open the take-home session for the matrix; `curl -sI https://www.arcs.care/hud` for the live check.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261011T021135Z--claude-arcs-config-harness-integration-b14b89.md
> Late follow-ups: checked the Louisville nav merge, corrected its receipt with a new row, and added 21:58 to 22:10 to the 2026-10-10 digest.

### Notes: lead of 20261011T021627Z--claude-handoff-hud-relay.md
### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-hud-relay), receipts in digest: 1.
- **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 25 / dissent 6 (ratio 3.57) → OK: dissent present.
- **Cold re-read (canary on the draft f6.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: kept all claims; the grep counts show mentions, not reading. Somatic: not asked. Disposition: release.

> Molted v3.127.0, verified arcs.care/hud live after #1174 and sent Zach the screenshots, and relayed his "use ALL the briefing resources" audit request to the take-home session.

### Notes: Shavasana
- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-h-1010), receipts in digest: 1.
- **Inhale** (what came in): 0 falsification rows today, 6 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 24 / dissent 8 (ratio 2.67) → OK: dissent present.
- **Cold re-read (canary on the draft frag8.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Exhale reads 0 because its scope is this handoff branch; the session merged #1255 and logged two receipts.
- Attachment release: the Todd calendar-acceptance claim now cites its source and says it was not re-checked here. Somatic: not asked. Disposition: release.

> Molted from `_HANDOFFS/fragments/20261011T021135Z--claude-arcs-config-harness-integration-b14b89.md` (branch `claude/arcs-config-harness-integration-b14b89`, head `12f27a7e`); `_HANDOFFS/fragments/20261011T021627Z--claude-handoff-hud-relay.md` (branch `claude/handoff-hud-relay`, head `dfbdf60a`).

# Handoff — v3.127.0 (2026-10-11)

> 2026-10-10 last: arcs.care/hud became the full-screen field HUD with an admin-only ziggurat load (PR #1174, still open), the atlas observatory waits on the take-home's bundle after submission, and the v3.126.0 molt cleared the integrity gate's false positives without a bypass.

## Goal / true north
Ship the monday.com take-home by Thu 2026-10-15 17:00 ET; build the replay booth and the atlas admin route only after submission.

## What changed
- #1240 merged: night-moves 2026-10-10 updated in place (not overwritten): 95 commits, 21:06-21:41 work, dependency sweep at 21:41.
- #1231 reviewed and merged (b27b6a46): Louisville sticky section nav, all checks green. Receipt `2026-10-10--louisville-sticky-nav-merge-pr1231--ZH`.
- #1174 reviewed, not merged here: smoke Lint failed at src/organisms/ScopeHud.tsx:115 (setState in an effect). The owning session ("Make arcs.care/hud the full-screen 5D explorer") was already fixing it, so I did not push; it pushed a fix to the #1174 branch and owns the merge, receipt and live check. It will also correct the surface catalog, which marks /hud as admin-gated when only the ziggurat loader is.
- #1174 open, not merged (branch claude/arcs-hud-fullscreen): new /hud route, Scope `pinned`, `barSlot` and `ziggurat` props, ScopeHud `collapseHolds`, toast and sticky footer hidden on /hud, surface catalog `surface-gate: open` marker.
- #1246 merged (`10138ba8`); receipt 2026-10-10--night-moves-latenight-pr1246--ZH.
- #1247 merged (`5f4b41d1`): molt of 4 fragments into handoff v3.126.0; v3.124.0 relocated to _ARCHIVE/handoffs.md. Receipt `2026-10-10--handoff-molt-v3.126.0-pr1247--ZH`.
- Reworded a v3.125.0 line that named the deleted salvage commits and claimed the bundles were kept; the gate then passed with no bypass.

## Current state
- CLAUDE.md holds v3.126.0 and v3.125.0; the integrity gate's six false positives no longer fire.
- #1107 and #1101 confirmed MERGED with gh and dropped from Open.

## Decisions made
- Reshape by making the terrain shape module-level and rebuilding the point cloud, instead of a separate overlay; the knowledge-lattice nodes keep their u,v and sit on the new heights.
- Fold the Holds panel on phones only while a ziggurat is loaded (Zach picked this over a top label strip).
- This session owns the #1174 merge and receipt; the observatory session that offered to merge was told to stand down.
- The night-moves update was added to the existing digest, not regenerated, to keep other sessions' sections.
- Fix a stale cite in the block rather than bypass the gate again.

## Open decisions (waiting on Zach)
1. Zach: take-home dress rehearsal once ONBOARDING.md lands; submit by Thu 2026-10-15 17:00 ET.
2. Zach: approve the tool prompts in the "Held dependency exceptions watch" run.
3. Zach: confirm the better-sqlite3 bump (#557) was an approved dependency change.

## Open (other)
1. Merge #1174 with --merge once fe-smoke is green, log its receipt, then send Zach live arcs.care/hud screenshots at phone and desktop.
2. On or after 2026-10-13: `python3 scripts/backlog_status_check.py --gh`; confirm or close each RUNNING row it flags.
3. The Oct-06 Success Academy check-in to Brian is still unconfirmed in Gmail.
4. After submission: atlas-bundle.v1 export, replay booth kickoff 17:30, then the admin route per runtime/specs/atlas-bundle-observatory-spec.md v0.4.
5. Vico intro Wed 2026-10-14 13:00 ET.

## Next action
PRL go-live call with Todd, Mon 2026-10-12 10:00 ET.

## Cold-start recipe
- /handoff-pickup; the latest CLAUDE.md block is v3.126.0.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261011T020350Z--claude-handoff-hud-1010.md
> Built arcs.care/hud: the field HUD (Scope) pinned full screen with no page chrome, plus an admin-only ziggurat load that reshapes the field terrain from an arcs.atlas.v1 file. Also landed the 2026-10-10 late-night night-moves update.

### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-hud-1010), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 3 dissent markers, 3 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 23 / dissent 6 (ratio 3.29) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: every claim kept; the two untested items (non-admin in prod, live page) were already in State as not verified. Somatic: not asked. Disposition: release.

### Notes: lead of 20261011T020517Z--claude-handoff-molt3-note.md
### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-molt3-note), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 3 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 19 / dissent 5 (ratio 3.17) → OK: dissent present.
- **Cold re-read (canary on the draft f5.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: kept all claims. Somatic: not asked. Disposition: release.

> Molted the late 4 fragments into v3.126.0 with no integrity-gate bypass, after rewording a stale line of my own.

### Notes: Lessons
- Before pushing to another session's PR branch, check its worktree for uncommitted edits (git worktree list + status); here the owner was mid-fix on the same line.

> Molted from `_HANDOFFS/fragments/20261011T020320Z--claude-atlas-handoff-d.md` (branch `claude/atlas-handoff-d`, head `c3bd0ac7`); `_HANDOFFS/fragments/20261011T020350Z--claude-handoff-hud-1010.md` (branch `claude/handoff-hud-1010`, head `c3bd0ac7`); `_HANDOFFS/fragments/20261011T020517Z--claude-handoff-molt3-note.md` (branch `claude/handoff-molt3-note`, head `5f4b41d1`).
