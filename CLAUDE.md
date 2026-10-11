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

# Handoff — v3.131.0 (2026-10-11)

> Consolidation block: carries forward the open lists of v3.130.0 and v3.129.0 (the latter moves to _ARCHIVE/handoffs.md with this molt) so nothing drops out of the hot path. Only new fact: the v3.129.0 molt landed as #1266.

## Goal / true north
Ship the monday.com take-home by Thu 2026-10-15 17:00 ET using every resource the briefing listed, or a recorded reason not to.

## What changed
- #1266 merged (`b1a06808`): molt of 3 fragments into handoff v3.129.0; integrity gate passed first try. Receipt `2026-10-10--handoff-molt-v3.129.0-pr1266--ZH`.

## Current state
- CLAUDE.md holds v3.129.0 (current) and v3.128.0.
- #1174's receipt is logged; that Open item is closed.

## Decisions made
- None new.

## Open decisions (waiting on Zach)
1. Zach: spending limit on Actions (Settings > Billing > Budgets); drop the gh `user` scope when done (`gh auth refresh -h github.com -r user`).
2. Zach: clear the take-home session's pending prompt if it does not reply; that session owes the resource x plan matrix before changing code.
3. Zach: send Todd's agenda (choose the account) and own the August-test wording if wanted.
4. Zach: take-home dress rehearsal once ONBOARDING.md lands; submit by Thu 2026-10-15 17:00 ET. Whether the assessment terms allow publishing the NFTT build log.
5. Zach: approve the tool prompts in the "Held dependency exceptions watch" run; confirm the better-sqlite3 bump (#557).

## Open (other)
1. #1267 merged; confirm its receipt is logged and gl-z6 shows on prl.arcs.care/go-live.
2. PRL Zap: test skip-vs-clear on empty fields before publishing; after publishing, repair Roger and run the repeat-chat proof (Mon 2026-10-12 10:00 ET call).
3. Measure fe-smoke minutes on the first non-shared code PR after #1260; confirm the first nightly a11y run (07:41 UTC) is green; then decide on closing #1046.
4. Check the arcs.care/hud ziggurat loader live as a signed-in admin.
5. On or after 2026-10-13: `python3 scripts/backlog_status_check.py --gh`; confirm or close each RUNNING row it flags.
6. ADR-078 has a file but no `_DECISIONS/index.json` row (integrity gate WARN).
7. The Oct-06 Success Academy check-in to Brian is still unconfirmed in Gmail.
8. After submission: atlas-bundle.v1 export, replay booth kickoff 17:30, then the admin route per runtime/specs/atlas-bundle-observatory-spec.md v0.4.
9. Vico intro Wed 2026-10-14 13:00 ET.

## Next action
Confirm gl-z6 shows on prl.arcs.care/go-live and #1267's receipt is logged, then the Mon 2026-10-12 10:00 ET call with Todd.

## Cold-start recipe
- /handoff-pickup; the latest CLAUDE.md block is v3.129.0.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261011T024249Z--claude-handoff-molt6-note.md
### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-molt6-note), receipts in digest: 1.
- **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 26 / dissent 6 (ratio 3.71) → OK: dissent present.
- **Cold re-read (canary on the draft f8.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: kept all claims. Somatic: not asked. Disposition: release.

> Molted the final 3 fragments into v3.129.0; no other work since the previous fragment.

> Molted from `_HANDOFFS/fragments/20261011T024249Z--claude-handoff-molt6-note.md` (branch `claude/handoff-molt6-note`, head `ab9c6222`).

# Handoff — v3.130.0 (2026-10-11)

> Two legs on 2026-10-10/11: (a) the main-checkout salvage, the epic migration onto GitHub milestones, full issue triage, and the Actions cost cut that scopes the WCAG ratchet per PR; (b) the PRL go-live blocker correction and the take-home status check.

## Goal / true north
Leave the repo with an epic structure on GitHub (JSONL still the SSOT), Actions spend under control without weakening accessibility, and PRL / take-home state that matches the evidence before Monday.

## What changed
- #1169 merged (`ebcceb6a`): carried `_QUEUE/epic-migration-plan.md` + the v3.67.0 SKILL.md changelog line from the salvage WIP commit (head of the kept branch claude/falsifiable-position-criteria-inltlk-local-salvage); everything else STALE or STATE. Receipt 2026-10-10--salvage-carry-epic-plan-pr1169--ZH
- #1227 merged (`d494d6b3`): 10 milestones; 51 OPEN/RUNNING backlog rows mirrored to issues #1175-#1225 via `scripts/backlog_issue_sync.py` (JSONL stays SSOT); 97 issues milestoned. Receipt 2026-10-10--epic-migration-milestones-pr1227--ZH
- Triage (no PR): closed 7 stale [backlog] mirrors (#580-584, #588, #589), milestoned 22 debt/bug issues, cross-linked 5 debt twins. Receipt 2026-10-10--triage-29-unmilestoned-issues--ZH
- #1260 merged (`833a2395`): WCAG ratchet scoped to changed pages on PRs, full sweep nightly (`.github/workflows/a11y-nightly.yml`). Receipt 2026-10-11--a11y-ratchet-pr-scope-pr1260--ZH
- #1046 comments: run rate, per-job minutes, real billing (Oct 1-11: arcs-v9 8,999 min, net $42.18; included minutes gone Oct 5)
- #1267 open, not merged: Todd's go-live checklist (public/prl-status-runbook.html) adds item gl-z6 "Confirm a returning chat updates the lead it matched, never a fixed record"; `_STATE/snapshot.json` blocking line now names the step 8 static-Lead cause. page_gate 1/1; smoke pending at 02:45Z.
- No merges this leg; receipts so far: 2026-10-10--handoff-fragment-hud-live-pr1263--ZH.

## Current state
- PRL root cause (from _ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md): Sep 17 Lamarre update came from step 8's static Lead pick, not an empty email. Fix staged as an unpublished draft of Zap 376827315; published v5 unchanged.
- Take-home (~/ret-rfp-intelligence, read-only look): CI green on 90d62d5; ONBOARDING.md present; commit 823bba4 records every briefing resource as used, rejected or cited. Two files uncommitted, owned by the take-home session.
- Status request sent to session "Continue monday take-home from HANDOFF.md" (status: waiting); no reply yet.

## Decisions made
- Epics: plan defaults 1-4; JSONL stays the SSOT (ADR-065), only OPEN/RUNNING rows synced (Zach).
- WCAG gate: change when pages are checked, never whether (Zach: accessibility is 2026 design best practice).
- Zach approved both PRL edits; the client-facing item got a new checkbox id so Todd's saved ticks stay put.
- Leave the take-home repo to its own session; ask by message only.

## Open decisions (waiting on Zach)
1. Zach: spending limit on Actions (Settings > Billing > Budgets) is unread.
2. Zach: drop the gh `user` scope when done (`gh auth refresh -h github.com -r user`); a suspended `gh auth refresh` job may still sit in terminal tab c1.
3. Zach: clear the take-home session's pending prompt if it does not reply.

## Open (other)
1. Measure fe-smoke minutes on the first non-shared code PR after #1260; confirm the first nightly a11y run (07:41 UTC) is green; then decide on closing #1046.
2. Epic plan's 5 decisions are answered; retired-model row old-anthropic-callers-moved is BLOCKED, so it has no issue.
3. ADR-078 has a file but no `_DECISIONS/index.json` row (integrity gate WARN).
4. Merge #1267 when CI passes, log its receipt, confirm gl-z6 live on prl.arcs.care/go-live.
5. Relay the take-home session's reply to Zach.

## Next action
Merge #1267 once smoke passes and confirm gl-z6 shows on prl.arcs.care/go-live; then check the 07:41 UTC a11y-nightly run and a post-#1260 fe-smoke time and post both on #1046.

## Cold-start recipe
- PRL: `gh pr checks 1267`; `gh pr merge 1267 --merge`; insert a decision_receipt row; `curl -sL https://prl.arcs.care/go-live | grep -c "never a fixed record"`. Context: _ARTIFACTS/prl-1-2-close-loop/2026-10-09-go-live-blockers.md.
- Actions cost: `gh run list --workflow a11y-nightly.yml -L 3`; `gh issue view 1046 --comments`; billing needs the gh `user` scope: `gh api "users/flashesofbrilliance/settings/billing/usage?year=2026&month=10"`.
- Epics: `gh api repos/flashesofbrilliance/arcs-v9/milestones`; backlog SSOT `_QUEUE/induced-backlog.jsonl` synced by `scripts/backlog_issue_sync.py`.

Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection); not restated here.

### Notes: lead of 20261011T024037Z--claude-handoff-salvage-epics.md
> Salvaged the main-checkout WIP, ran the epic migration onto GitHub milestones, triaged every unmilestoned issue, measured Actions spend against real billing, and cut the biggest cost (the WCAG ratchet) by scoping it per PR. Memory index compacted to 17.1KB.

### Notes: lead of 20261011T024242Z--claude-handoff-prl-takehome.md
> After pickup: corrected the stale PRL go-live blocker (snapshot + Todd's checklist), then asked the take-home session for status. Follows fragment 20261011T022634Z--claude-handoff-hud-live.

### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-prl-takehome), receipts in digest: 1.
- **Inhale** (what came in): 0 falsification rows today, 5 dissent markers, 2 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 27 / dissent 7 (ratio 3.38) → OK: dissent present.
- **Cold re-read (canary on the draft frag3.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: every claim kept; #1267 and the take-home reply are stated as pending. Somatic: not asked. Disposition: release.

### Notes: Shavasana
- Mechanical: canary GROUNDED, no thin air; sycophancy OK (dissent present); exhale reads 0 only because it is scoped to this fresh handoff branch (session merged #1169, #1227, #1260).
- Attachment release: kept all claims; the #1260 saving is listed as unmeasured (Open 3), not as achieved.
- Somatic: not asked. Disposition: release.

> Molted from `_HANDOFFS/fragments/20261011T024037Z--claude-handoff-salvage-epics.md` (branch `claude/handoff-salvage-epics`, head `833a2395`); `_HANDOFFS/fragments/20261011T024242Z--claude-handoff-prl-takehome.md` (branch `claude/handoff-prl-takehome`, head `ab9c6222`).
