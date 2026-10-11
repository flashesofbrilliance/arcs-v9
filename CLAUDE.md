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

# Handoff — v3.126.0 (2026-10-11)

> 2026-10-10 late: the backlog got a machine-checkable `state` enum with a gate, the Counterpart pulse learned to skip auto-messages, the salvage leftovers closed (~/arcs-bundles/ deleted, settle-the-debate.png kept in ~/Downloads/), and a correction confirmed #1107 and #1101 both merged on 2026-10-09, so neither needs a decision.

## Goal / true north
Ship the monday.com take-home by Thu 2026-10-15 17:00 ET; build the replay booth and the atlas admin route only after submission.

## What changed
- Corrects the 2026-10-10 handoff block "merge train, neighbor scan, adr-queue fix" (fragment from #1155, now folded into CLAUDE.md). That block said #1107 and #1101 were held and needed a decision. Both had already merged on 2026-10-09: #1107 at 16:23Z as 70bd0de5 and #1101 at 18:33Z as d9c31a7a.
- #1107's fe-smoke failure (`depth slider missing` at 375, 790 and 1280) was on earlier commits of its branch; the final commit b15f5c87 passed CI and is what merged. The cause and the fix were not opened.
- #1101 needs no rebase: its branch is 0 commits ahead of main, and a trial merge of origin/main into it had no conflicts.
- #1153 merged (`786cacbd`): enum spec `runtime/specs/backlog-status.json`, lossless migration (114 rows round-trip), `scripts/backlog_status_check.py` in pre-commit + CI, readers/writers moved to `status_note`. Receipt `2026-10-10--backlog-state-enum-pr1153--ZH`.
- #1159 merged (`20dfad2b`): doc-gates-advisory-ci and notomation-receipt-save-nudge set to DONE, flow-state-om-metric set to COMPOSTED (PR #598 closed unmerged, branch kept). Receipt `2026-10-10--close-stale-backlog-rows-pr1159--ZH`.
- AGENTS.md gotcha #20 records the rule (this PR).
- #1234 merged (`064d29b9`): PRL line in `_STATE/night-moves/2026-10-10.md` and the earlier handoff fragment struck through with a visible correction (Todd's Oct-06 message was an auto calendar acceptance). Receipt 2026-10-10--pulse-prl-correction-pr1234--ZH, pointing back to 2026-10-10--night-moves-counterpart-pulse-pr1172--ZH.
- #1239 merged (`ec32bac2`): `.claude/skills/night-moves/SKILL.md` Counterpart pulse skips calendar replies, invite.ics-only, Mixmax and no-reply messages, and labels Gmail ids. Receipt 2026-10-10--night-moves-pulse-skip-automessages-pr1239--ZH.
- Main checkout `/Users/zharris/arcs-v9` detached at origin/main `9abadfb0` (contains #1239); its 5 hook-output edits carried over untouched.
- PRL memory note replaced with the correction (local, not in git).
- #1238 merged (`9d37d2bf`): molt of 5 fragments into handoff v3.125.0; integrity gate bypassed once for the six false positives carried by the live v3.124.0 block. Receipt `2026-10-10--handoff-molt-v3.125.0-pr1238--ZH`.
- Deleted ~/arcs-bundles/ (both salvage bundles, about 234 MB) on Zach's say; moved settle-the-debate.png to ~/Downloads/ first.

## Current state
- The salvage loop is closed: no falsifiable-position branches or bundles remain; their content is on main.
- settle-the-debate.png has exactly one copy, ~/Downloads/settle-the-debate.png, and is not in the repo.

## Decisions made
- Drop from the active handoff: "Zach: merge each PR on green CI; do not touch #1107 or #1101 yet", the open decision "decide #1107 and whether #1101 gets a rebase", and Open items 1 and 2 of the train fragment. Nothing replaces them.
- Zach classified the 13 rows the prefix classifier could not; the other 101 were classified by rule.
- Legacy RUNNING claims got `claimed_at` 2026-10-10 because no original claim time existed.
- COMPOSTED (not DONE) for flow-state-om-metric because its work never landed.
- Correct by visible strike-through plus a new receipt, never by deleting the wrong claim.
- Keep the image outside the repo (Zach chose "keep image, delete bundles").

## Open decisions (waiting on Zach)
1. Zach: take-home dress rehearsal once ONBOARDING.md lands; submit by Thu 2026-10-15 17:00 ET.
2. Zach: approve the tool prompts in the "Held dependency exceptions watch" run.
3. Zach: confirm the better-sqlite3 bump (#557) was an approved dependency change.

## Open (other)
1. On or after 2026-10-13: run `python3 scripts/backlog_status_check.py --gh` and confirm or close each RUNNING row it flags.
2. The Oct-06 Success Academy check-in to Brian is still unconfirmed in Gmail.
3. After submission: atlas-bundle.v1 export, then the admin route per runtime/specs/atlas-bundle-observatory-spec.md v0.4; then the replay booth.
4. Vico intro Wed 2026-10-14 13:00 ET.

## Next action
PRL go-live call with Todd, Mon 2026-10-12 10:00 ET.

## Cold-start recipe
- /handoff-pickup; the latest CLAUDE.md block is v3.125.0.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261011T015254Z--claude-handoff-backlog-state-enum.md
> Gave `_QUEUE/induced-backlog.jsonl` a machine-checkable `state` enum with a gate, then closed the three rows the gate flagged as stale.

### Notes: lead of 20261011T015554Z--claude-handoff-pulse-fixes-1010.md
### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-pulse-fixes-1010), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 5 dissent markers, 3 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 13 / dissent 8 (ratio 1.44) → OK: dissent present.
- **Cold re-read (canary on the draft frag2.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read**: somatic: not asked.
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

> Follow-up to the earlier pulse fragment: corrected the false PRL drift line, taught the Counterpart pulse to skip auto-messages, and moved the main checkout to origin/main so the live skill carries the rule.

### Notes: lead of 20261011T015729Z--claude-handoff-bundles-closed.md
### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-bundles-closed), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 3 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 12 / dissent 5 (ratio 2.0) → OK: dissent present.
- **Cold re-read (canary on the draft f4.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: kept all claims. Somatic: not asked. Disposition: release.

> Molted the evening's 5 fragments into v3.125.0 and closed its two salvage leftovers: ~/arcs-bundles/ deleted, settle-the-debate.png kept outside the repo.

### Notes: Shavasana
- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-backlog-state-enum), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 19 / dissent 6 (ratio 2.71) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Attachment release: all claims re-checked against gh/git; none dropped. Somatic: not asked. Disposition: release.

> Molted from `_HANDOFFS/fragments/20261011T014943Z--claude-mystifying-tesla-6bc6f3-correction.md` (branch `claude/handoff-fragment-correction`, head `064d29b9`); `_HANDOFFS/fragments/20261011T015254Z--claude-handoff-backlog-state-enum.md` (branch `claude/handoff-backlog-state-enum`, head `9d37d2bf`); `_HANDOFFS/fragments/20261011T015554Z--claude-handoff-pulse-fixes-1010.md` (branch `claude/handoff-pulse-fixes-1010`, head `c869fcaf`); `_HANDOFFS/fragments/20261011T015729Z--claude-handoff-bundles-closed.md` (branch `claude/handoff-bundles-closed`, head `80f5dccb`).
