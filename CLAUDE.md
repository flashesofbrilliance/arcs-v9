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

# Handoff — v3.129.0 (2026-10-11)

> 2026-10-10 final: #1174 is merged with its receipt (`2026-10-10--arcs-hud-fullscreen-ziggurat-pr1174--ZH`) and arcs.care/hud is live; the PRL Lamarre update's real cause was found and an unpublished Zap fix plus Todd's Monday agenda are staged; the NFTT take-home build log is queued behind the Thu submission.

## Goal / true north
Ship the monday.com take-home by Thu 2026-10-15 17:00 ET using every resource the briefing listed, or a recorded reason not to.

## What changed
- #1261 merged (`9a8d71ee`): molt of 2 fragments into handoff v3.128.0; integrity gate passed first try. Receipt `2026-10-10--handoff-molt-v3.128.0-pr1261--ZH`.
- #1174 merged (`12f27a7e`, 2026-10-11T02:10Z); receipt 2026-10-10--arcs-hud-fullscreen-ziggurat-pr1174--ZH.
- #1249 merged (`5097ded0`); receipt 2026-10-10--handoff-fragment-hud-pr1249--ZH.
- #1164 merged (`00b896f4`): backlog row nftt-monday-fde-takehome-build-log, gated after Thu 2026-10-15 17:00 ET, publish scope confirmed (company named only as "a work-management platform"). Receipt 2026-10-10--queue-nftt-monday-buildlog-pr1164--ZH
- #1228 merged (`53ee0296`): row cross-references the private replay booth (cite its figures, never retype). Receipt 2026-10-10--nftt-buildlog-booth-xref-pr1228--ZH
- #1237 merged (`316d650b`): Lamarre root cause in the go-live checklist. Receipt 2026-10-10--prl-lamarre-root-cause-draft-fix-pr1237--ZH
- #1253 merged (`1d8f0cf5`): draft status in the checklist. Receipt 2026-10-10--prl-draft-title-industry-pr1253--ZH
- #1258 merged (`260189bb`): Monday agenda draft file. Receipt 2026-10-10--prl-call-agenda-draft-pr1258--ZH
- Unsent Gmail draft to todd.hotes@prlresins.com in zach.harris@gmail.com (same text as the agenda file).

## Current state
- Zap 376827315: published v5 unchanged and on. An unpublished draft has step 8 Lead mapped to `5. ID` (was static "Roger A Lamarre") and Account Description, Notes, Title, Industry emptied. Retest step never run.
- Sep 17 run 0067cd35: email was todd.hotes@prlresins.com; step 5 found lead db056406; step 8 wrote to Roger (ea77a7d2). Not an empty-email case.
- This Zap's runs are not held; the only held run is the Covestro Unbounce -> GHL Zap.
- Replied to the replay-booth session: no shared timeline generator needed.

## Decisions made
- None new.
- Draft only, not published: client's live Zap, and the cause differed from what Todd was told; show him first (Zach chose option B).
- Empty-email guard demoted: it would not have stopped Sep 17; still worth doing later per task8 sheet.
- Agenda drops the Zapier plan-upgrade ask, since runs are not held.

## Open decisions (waiting on Zach)
1. Zach: send Todd's agenda (choose the account) and own the August-test wording if wanted.
2. Zach: take-home dress rehearsal once ONBOARDING.md lands; submit by Thu 2026-10-15 17:00 ET. Whether the assessment terms allow publishing the NFTT build log.
3. Zach: approve the tool prompts in the "Held dependency exceptions watch" run; confirm the better-sqlite3 bump (#557).

## Open (other)
1. Take-home session: deliver the resource x plan matrix to Zach before changing code.
2. PRL Zap, before publishing: test whether the SugarAI update skips or clears empty fields; if it clears, remove the four emptied fields. After publishing: repair Roger, run the repeat-chat proof.
3. Check the arcs.care/hud ziggurat loader live as a signed-in admin.
4. On or after 2026-10-13: `python3 scripts/backlog_status_check.py --gh`; confirm or close each RUNNING row it flags.
5. The Oct-06 Success Academy check-in to Brian is still unconfirmed in Gmail.
6. After submission: atlas-bundle.v1 export, replay booth kickoff 17:30, then the admin route per runtime/specs/atlas-bundle-observatory-spec.md v0.4.
7. Vico intro Wed 2026-10-14 13:00 ET.

## Next action
Mon 2026-10-12 10:00 ET call with Todd: run agenda section 3 (skip-vs-clear test, publish, repair Roger, two proof chats), then log a receipt.

## Cold-start recipe
- Read `_ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md` (bottom two sections) and `2026-10-12-call-agenda-todd-DRAFT.md`.
- Zapier editor: https://zapier.com/editor/376827315/draft/376828757/fields (Chrome tab group; sign in if prompted). Never click "Retest step" on step 8.
- Build log: backlog row nftt-monday-fde-takehome-build-log, not before Thu 10-15 17:00 ET.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection).

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261011T022552Z--claude-handoff-molt5-note.md
### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-molt5-note), receipts in digest: 1.
- **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 22 / dissent 6 (ratio 3.14) → OK: dissent present.
- **Cold re-read (canary on the draft f7.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: kept all claims. Somatic: not asked. Disposition: release.

> Molted the closing 2 fragments into v3.128.0; no other work since the previous fragment.

### Notes: lead of 20261011T022634Z--claude-handoff-hud-live.md
> Follow-up to fragment 20261011T020350Z--claude-handoff-hud-1010: #1174 merged and arcs.care/hud is live; that fragment's "open, not merged" lines are superseded.

### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-hud-live), receipts in digest: 1.
- **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 3 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 25 / dissent 7 (ratio 3.12) → OK: dissent present.
- **Cold re-read (canary on the draft frag2.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: every claim kept; untested items stay in State as not checked. Somatic: not asked. Disposition: release.

### Notes: lead of 20261011T022635Z--claude-stoic-nobel-0f6cd4.md
> Session 2026-10-10 (stoic-nobel): queued the NFTT take-home build log behind the Thu 10-15 submission, then found the real cause of the PRL Lamarre update and staged an unpublished Zap fix plus Todd's Monday agenda.

### Notes: Shavasana
Canary GROUNDED; dissent present (ratio 4.0). Attachment release: kept all claims; each cites a run id, PR or receipt. Downgraded: Title/Industry clear is visually confirmed, not text-checked after reload (noted in receipt). somatic: not asked. Disposition: release.

> Molted from `_HANDOFFS/fragments/20261011T022552Z--claude-handoff-molt5-note.md` (branch `claude/handoff-molt5-note`, head `023f2752`); `_HANDOFFS/fragments/20261011T022634Z--claude-handoff-hud-live.md` (branch `claude/handoff-hud-live`, head `023f2752`); `_HANDOFFS/fragments/20261011T022635Z--claude-stoic-nobel-0f6cd4.md` (branch `claude/stoic-nobel-0f6cd4`, head `023f2752`).

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
